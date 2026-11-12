"""Replay aggregate cache writes through the real gateway, without inference."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
import gateway_pricing
from gateway_models import openrouter_cache_ttl, apply_cache_ttl
from gateway_runtime import Gateway
from test_cache_duration import RATES

MODEL = 'anthropic/claude-opus-5.5'
USAGE = {'prompt_tokens': 13303, 'completion_tokens': 117, 'total_tokens': 13420,
         'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 13299},
         'completion_tokens_details': {'reasoning_tokens': 13}, 'cost': .068851}


class OpenRouterCacheAccountingTests(unittest.IsolatedAsyncioTestCase):
    async def test_aggregate_writes_settle_and_next_request_runs(self):
        for stream in (False, True):
            for ttl in (None, '5m', '1h'):
                with self.subTest(stream=stream, ttl=ttl):
                    await self.exercise(stream, ttl)

    async def exercise(self, stream, ttl, *, reject_mixed=False):
        reference = {**RATES, 'provider': 'openrouter', 'upstream_id': MODEL, 'request_models': [MODEL]}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
                'TESTBED_USAGE_DIR': tmp, 'DUNGENESS_ALLOWED_MODELS': json.dumps([['openrouter', MODEL]]),
                'MAX_MODEL_REQUESTS': '20', 'MAX_MODEL_TOKENS': '1000000', 'MAX_MODEL_USD': '3',
                'DUNGENESS_CREDENTIALS_FILE': str(Path(tmp) / 'credentials.json')}), \
                patch.object(gateway_pricing, 'MODEL_PRICING', [reference]):
            credential = Path(tmp) / 'credentials.json'
            credential.write_text(json.dumps({'OPENROUTER_API_KEY': 'synthetic-test-value'})); credential.chmod(0o600)
            runtime = Gateway(); await runtime.client.aclose(); calls = []
            def upstream(request):
                self.assertTrue(request.url.path.endswith('/chat/completions'))
                calls.append(request)
                data = {'id': f'gen-{len(calls)}', 'model': MODEL, 'usage': USAGE,
                        'choices': [{'index': 0, 'finish_reason': 'stop', 'delta': {'content': 'ok'}}]}
                if stream:
                    return httpx.Response(200, content=('data: ' + json.dumps(data) + '\n\ndata: [DONE]\n\n'),
                                          headers={'content-type': 'text/event-stream'})
                return httpx.Response(200, json=data)
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            payload = {'model': MODEL, 'max_tokens': 100, 'stream': stream,
                       'messages': [{'role': 'user', 'content': 'fixture'}],
                       'cache_control': {'type': 'ephemeral', **({'ttl': ttl} if ttl else {})}}
            try:
                with patch.object(gateway, 'gateway', runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app), base_url='http://gateway') as client:
                        if reject_mixed:
                            mixed = {**payload, 'messages': [{'role': 'user', 'content': [
                                {'type': 'text', 'text': 'fixture', 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}]}]}
                            response = await client.post('/model/openrouter/v1/chat/completions', json=mixed)
                            self.assertEqual(response.status_code, 400, response.text)
                            self.assertEqual(response.json()['diagnostic']['run_action'], 'continue')
                            self.assertEqual(calls, [])
                        for _ in range(2):
                            response = await client.post('/model/openrouter/v1/chat/completions', json=payload)
                            self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(len(calls), 2)
                records = [e['data'] for e in map(json.loads, (Path(tmp)/'events.jsonl').read_text().splitlines())
                           if e['kind'] == 'model.accounting']
                for receipt in records:
                    self.assertEqual(receipt['accounting_method'], 'gateway')
                    self.assertEqual(receipt['accounting_basis'], 'provider_usage_request_cache_ttl')
                    self.assertEqual(receipt['cache_write_1h_input_tokens'], 13299 if ttl == '1h' else 0)
                    self.assertAlmostEqual(receipt['normalized_usd'], .108748 if ttl == '1h' else .068851)
                    self.assertEqual(receipt['billed_usd'], .068851)  # provider invoice stays independent
                summary = json.loads((Path(tmp)/'summary.json').read_text())['usage']
                self.assertEqual(summary['model_accounting_state'], 'settled')
                self.assertAlmostEqual(summary['billed_usd'], 2*.068851)
            finally:
                await runtime.client.aclose()

    async def test_mixed_duration_rejected_before_spending_and_correctable(self):
        await self.exercise(False, '5m', reject_mixed=True)

    def test_protocol_markers_and_route_scope(self):
        payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': [
            {'type': 'text', 'text': 'x', 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}]}],
            'tools': [{'type': 'function', 'function': {'parameters': {'cache_control': {'ttl': 'bogus'}}}}]}
        self.assertEqual(openrouter_cache_ttl('openrouter', 'chat/completions', payload, RATES), '1h')
        for provider, route in (('anthropic', 'messages'), ('openrouter', 'messages'), ('openrouter', 'responses')):
            self.assertIsNone(openrouter_cache_ttl(provider, route, payload, RATES))
        self.assertEqual(apply_cache_ttl({}, '5m'), {})
        native = {'cache_write_input_tokens': 300, 'cache_write_1h_input_tokens': 100}
        self.assertEqual(apply_cache_ttl(native, '5m'), native)
