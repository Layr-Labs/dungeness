import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_gateway
from gateway_reservations import bounded_request
from gateway_usage import UsageLedger, BudgetExceeded
from test_request_policy import harness, request_body, route

RATES = {'input_per_mtok': 2, 'cached_read_per_mtok': .5, 'output_per_mtok': 10}


class ReservationTests(unittest.TestCase):
    def test_offline_validator_covers_field_policy_and_output_reservations(self):
        from gateway_reservations import validate_generation, OutputLimitError
        payload = {'model': 'claude-opus-5-5', 'messages': [{'role': 'user', 'content': 'Synthetic probe'}], 'max_tokens': 64000}
        body, _, _ = validate_generation('claude-subscription', 'messages', payload, RATES)
        self.assertEqual(body['max_tokens'], 64000)
        with self.assertRaises(OutputLimitError):
            validate_generation('claude-subscription', 'messages', {**payload, 'max_tokens': 128000}, RATES)
        with self.assertRaises(ValueError):
            validate_generation('claude-subscription', 'messages', {**payload, 'unknown_control': True}, RATES)

    def test_zero_input_pricing_still_reserves_tokens(self):
        for output in (0, 10):
            with self.subTest(output=output):
                _, tokens, usd = bounded_request({'model':'example','input':'hello'}, 'responses',
                    {'input_per_mtok':0,'cached_read_per_mtok':0,'output_per_mtok':output})
                self.assertGreater(tokens, 16384)
                self.assertEqual(usd, 16384*output/1e6)

    def test_limit_and_explicit_history_required(self):
        for payload in ({'max_output_tokens': 65537}, {'max_output_tokens': True}, {'n': 2},
                        {'max_tokens': 8},
                        {'max_tokens': 8, 'max_completion_tokens': 9}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                bounded_request({'model': 'example', **payload}, 'responses', RATES)
        body, tokens, usd = bounded_request({'model': 'example', 'input': 'hello'}, 'responses', RATES)
        self.assertEqual(body['max_output_tokens'], 16384)
        self.assertGreater(tokens, 16384)
        self.assertGreater(usd, .16)

    def test_opaque_history_reserves_exclusively_without_dropping_it(self):
        payload = {'model': 'example', 'input': [{'type': 'reasoning', 'encrypted_content': 'opaque'}]}
        body, tokens, usd = bounded_request(payload, 'responses', RATES)
        self.assertEqual(body['input'], payload['input'])
        self.assertEqual(body['max_output_tokens'], 16384)
        self.assertIsNone(tokens); self.assertIsNone(usd)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'MAX_MODEL_REQUESTS':'100', 'MAX_MODEL_TOKENS': '100', 'MAX_MODEL_USD': '1'}):
            ledger = UsageLedger('test', Path(tmp))
            ledger.admit_model('visible', tokens=10, usd=.1)
            with self.assertRaises(BudgetExceeded): ledger.admit_model('opaque', exclusive=True)
            ledger.finish_model('visible', accounted=True)
            ledger.admit_model('opaque', exclusive=True)
            self.assertEqual(ledger.model_inflight['opaque'], 1)
            self.assertEqual(ledger.model_token_inflight['opaque'], 100)
            with self.assertRaises(BudgetExceeded): ledger.admit_model('other', tokens=1, usd=.01)
            ledger.add_model_usage(billed_tokens=10, normalized_usd=.1)
            ledger.finish_model('opaque', accounted=True)
            ledger.admit_model('next', tokens=10, usd=.1)

    def test_guard_preserves_codex_reasoning_history_through_http(self):
        async def run():
            with patch.dict(os.environ, {'DUNGENESS_BOUNDED_REQUESTS': '1'}):
                async with harness() as (client, runtime, calls):
                    body = request_body('openrouter', 'responses')
                    body['input'] = [{'type':'message', 'role':'user', 'content':body['input']},
                                     {'type':'reasoning', 'id':'r', 'summary':[], 'encrypted_content':'opaque'}]
                    reply = await client.post(route('openrouter', 'responses'), json=body)
                    self.assertEqual(reply.status_code, 200, reply.text)
                    self.assertEqual(calls[0][1]['input'], body['input'])
        asyncio.run(run())

    def test_concurrent_requests_cannot_overreserve_tokens_or_credits(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'MAX_MODEL_TOKENS': '100', 'MAX_MODEL_USD': '1'}):
            ledger = UsageLedger('test', Path(tmp))
            def reserve(i):
                try:
                    ledger.admit_model(str(i), tokens=60, usd=.6)
                    return str(i)
                except BudgetExceeded:
                    return None
            with ThreadPoolExecutor(max_workers=8) as pool:
                admitted = [x for x in pool.map(reserve, range(8)) if x is not None]
            self.assertEqual(len(admitted), 1)
            ledger.add_model_usage(billed_tokens=10, normalized_usd=.1)
            ledger.finish_model(admitted[0], accounted=True)
            ledger.admit_model('next', tokens=60, usd=.6)
            ledger.finish_model('next', accounted=False)
            with self.assertRaises(BudgetExceeded):
                ledger.admit_model('unknown-usage', tokens=1, usd=.01)

    def test_guard_injects_output_limit_and_rejects_before_network(self):
        async def run():
            with patch.dict(os.environ, {'DUNGENESS_BOUNDED_REQUESTS': '1'}):
                async with harness() as (client, runtime, calls):
                    body = request_body('openrouter', 'responses')
                    body['max_output_tokens'] = 65537
                    reply = await client.post(route('openrouter', 'responses'), json=body)
                    self.assertEqual(reply.status_code, 400)
                    self.assertFalse(calls)
                    del body['max_output_tokens']
                    reply = await client.post(route('openrouter', 'responses'), json=body)
                    self.assertEqual(reply.status_code, 200, reply.text)
                    self.assertEqual(calls[0][1]['max_output_tokens'], 16384)
        asyncio.run(run())

    def test_only_reachable_context_rates_are_reserved(self):
        rates = {**RATES, 'long_context': {**RATES, 'threshold_input_tokens': 2000,
                 'input_per_mtok': 20, 'output_per_mtok': 100}}
        short = {'model': 'example', 'input': 'hello'}
        self.assertEqual(bounded_request(short, 'responses', rates),
                         bounded_request(short, 'responses', RATES))
        long = {**short, 'input': 'x'*2000}
        self.assertGreater(bounded_request(long, 'responses', rates)[2],
                           bounded_request(long, 'responses', RATES)[2])

    def test_omitted_output_limit_fits_remaining_budget_but_explicit_is_preserved(self):
        payload = {'model': 'example', 'input': 'hello'}
        body, tokens, usd = bounded_request(payload, 'responses', RATES, available_usd=.05)
        self.assertLess(body['max_output_tokens'], 16384)
        self.assertGreater(body['max_output_tokens'], 1)
        self.assertLessEqual(usd, .05)
        explicit = {**payload, 'max_output_tokens': 16384}
        body, _, usd = bounded_request(explicit, 'responses', RATES, available_usd=.05)
        self.assertEqual(body['max_output_tokens'], 16384)
        self.assertGreater(usd, .05)

    def test_small_budget_reaches_provider_and_oversize_rejection_has_details(self):
        async def run():
            with patch.dict(os.environ, {'DUNGENESS_BOUNDED_REQUESTS': '1'}):
                async with harness() as (client, runtime, calls):
                    runtime.ledger.usd_limit = .05
                    body = request_body('openrouter', 'responses')
                    reply = await client.post(route('openrouter', 'responses'), json=body)
                    self.assertEqual(reply.status_code, 200, reply.text)
                    self.assertLess(calls[0][1]['max_output_tokens'], 16384)
                    body['max_output_tokens'] = 65536
                    reply = await client.post(route('openrouter', 'responses'), json=body)
                    self.assertEqual(reply.status_code, 429, reply.text)
                    error = reply.json()
                    self.assertEqual(error['code'], 'model_reservation_exceeds_remaining_budget')
                    self.assertFalse(error['upstream_request_sent'])
                    self.assertGreater(error['required_reservation_usd'], error['available_usd'])
                    self.assertEqual(len(calls), 1)
        asyncio.run(run())
