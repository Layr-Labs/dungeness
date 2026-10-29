import asyncio
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx

from gateway_provider_cost import amount, openrouter_charge, response_charge
from gateway_usage import UsageLedger, BudgetExceeded


class ProviderCostTests(unittest.TestCase):
    def test_json_sse_and_responses_use_provider_cost_not_reference_price(self):
        for wrapper in (lambda v: v, lambda v: {'response': v}):
            value = wrapper({'id': 'gen-one', 'usage': {'cost': 0.023456789}})
            for body, content_type in [(json.dumps(value).encode(), 'application/json'),
                                       (b'data: '+json.dumps(value).encode()+b'\n\ndata: [DONE]\n', 'text/event-stream')]:
                self.assertEqual(response_charge(body, content_type), ('gen-one', 0.023456789))
        self.assertEqual(amount(0), 0)
        for value in (None, True, -1, 'nan', 'Infinity', {}, 'invalid'):
            self.assertIsNone(amount(value))

    def test_cost_in_response_does_not_query_shared_key_balance(self):
        async def run():
            def upstream(request):
                self.fail('No extra request is needed for a complete cost response')
            async with httpx.AsyncClient(transport=httpx.MockTransport(upstream)) as client:
                return await openrouter_charge(client, b'{"id":"gen-one","usage":{"cost":0}}',
                                               'application/json', {'authorization': 'Bearer synthetic'}, 'example/model')
        self.assertEqual(asyncio.run(run()), ('gen-one', 0, 'openrouter_usage'))

    def test_reconciliation_uses_only_generation_id_and_checks_model(self):
        async def run(wrong_model=False):
            def upstream(request):
                self.assertEqual(str(request.url), 'https://openrouter.ai/api/v1/generation?id=gen-one')
                self.assertEqual(request.headers['authorization'], 'Bearer synthetic')
                return httpx.Response(200, json={'data': {'id': 'gen-one', 'model': 'wrong' if wrong_model else 'example/model', 'total_cost': 0.125}})
            async with httpx.AsyncClient(transport=httpx.MockTransport(upstream)) as client:
                return await openrouter_charge(client, b'{"id":"gen-one"}', 'application/json',
                                               {'authorization': 'Bearer synthetic'}, 'example/model')
        self.assertEqual(asyncio.run(run()), ('gen-one', 0.125, 'openrouter_generation'))
        self.assertEqual(asyncio.run(run(True)), ('gen-one', None, 'unavailable'))
        self.assertEqual(response_charge(b'{"id":"https://attacker.invalid"}', 'application/json'), (None, None))

    def test_parallel_runs_keep_their_own_generation_cost(self):
        async def run():
            async def upstream(request):
                identity = request.url.params['id']
                return httpx.Response(200, json={'data': {'id': identity, 'model': 'example/model',
                                                       'total_cost': {'gen-a': 0.2, 'gen-b': 0.7}[identity]}})
            async with httpx.AsyncClient(transport=httpx.MockTransport(upstream)) as client:
                return await asyncio.gather(*(openrouter_charge(client, json.dumps({'id': identity}).encode(),
                    'application/json', {'authorization': 'Bearer same-platform-key'}, 'example/model')
                    for identity in ('gen-a', 'gen-b')))
        self.assertEqual(asyncio.run(run()), [('gen-a', 0.2, 'openrouter_generation'), ('gen-b', 0.7, 'openrouter_generation')])

    def test_actual_charge_controls_budget_and_missing_cost_stops_admission(self):
        env = {'MAX_SEARCHES': '0', 'MAX_FETCHES': '0', 'MAX_MODEL_REQUESTS': '100',
               'MAX_MODEL_TOKENS': '', 'MAX_MODEL_USD': '1'}
        with patch.dict(os.environ, env), tempfile.TemporaryDirectory() as directory:
            for name, actual in [('known', 1.01), ('unknown', None)]:
                ledger = UsageLedger(name, Path(directory)/name)
                ledger.admit_model('first')
                ledger.add_model_usage(billed_tokens=3, normalized_usd=0.001,
                                       billed_usd=actual, budget_usd=actual)
                ledger.finish_model('first', accounted=actual is not None)
                with self.assertRaises(BudgetExceeded): ledger.admit_model('second')
                usage = json.loads((ledger.directory/'summary.json').read_text())['usage']
                self.assertEqual(usage['normalized_usd'], 0.001)
                self.assertEqual(usage['billed_usd'], actual)
