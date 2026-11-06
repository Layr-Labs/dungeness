"""Fast failure/recovery scenarios: mocked upstream, no paid inference."""
import json
import os
import unittest
from unittest.mock import patch

import httpx
import test_gateway
from test_request_policy import harness, request_body, route
from gateway_security import safe_provider_error
from gateway_usage import BudgetExceeded
from gateway_errors import recovery


class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejected_history_can_be_corrected_in_same_run(self):
        for provider, operation, kind in (
            ('openrouter', 'responses', 'input_image'),
            ('openai', 'chat/completions', 'image_url'),
            ('anthropic', 'messages', 'image'),
        ):
            with self.subTest(provider=provider):
                async with harness() as (client, runtime, calls):
                    good = request_body(provider, operation)
                    self.assertEqual((await client.post(route(provider, operation), json=good)).status_code, 200)
                    spent = runtime.ledger.usd_spent
                    requests = runtime.ledger.counts['model_requests']
                    candidate = runtime.ledger.directory / 'saved-candidate.rs'
                    candidate.write_text('retained work')
                    bad = dict(good)
                    history = [{'role': 'user', 'content': [{'type': kind, 'url': 'private-canary'}]}]
                    bad['input' if operation == 'responses' else 'messages'] = history
                    response = await client.post(route(provider, operation), json=bad)
                    self.assertEqual(response.status_code, 400)
                    info = response.json()['diagnostic']
                    self.assertEqual(info['run_action'], 'continue')
                    self.assertFalse(info['retryable'])
                    self.assertFalse(info['upstream_request_sent'])
                    self.assertEqual(response.headers['x-should-retry'], 'false')
                    self.assertNotIn('private-canary', response.text)
                    self.assertEqual(len(calls), 1)
                    self.assertEqual(runtime.ledger.usd_spent, spent)
                    self.assertEqual(runtime.ledger.counts['model_requests'], requests)
                    self.assertFalse(runtime.ledger.model_accounting_incomplete)
                    self.assertEqual(candidate.read_text(), 'retained work')
                    self.assertEqual((await client.post(route(provider, operation), json=good)).status_code, 200)
                    self.assertEqual(len(calls), 2)

    async def test_nonfatal_does_not_enable_hosted_tools_or_models(self):
        async with harness() as (client, runtime, calls):
            for change in ({'tools': [{'type': 'web_search'}]}, {'model': 'unauthorized'},
                           {'private-secret-field': 'private-canary'}):
                body = {**request_body('openrouter', 'responses'), **change}
                response = await client.post(route('openrouter', 'responses'), json=body)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()['diagnostic']['run_action'], 'continue')
                self.assertFalse(response.json()['diagnostic']['retryable'])
                self.assertNotIn('private-secret-field', response.text)
                self.assertNotIn('private-canary', response.text)
            self.assertFalse(calls)
            self.assertEqual(runtime.ledger.counts['model_requests'], 0)

    async def test_budget_stop_vs_wait_vs_correct(self):
        async with harness() as (_, runtime, __):
            ledger = runtime.ledger
            ledger.usd_limit = 1
            ledger.admit_model('active', usd=.9)
            with self.assertRaises(BudgetExceeded) as wait:
                ledger.admit_model('wait', usd=.5)
            self.assertEqual(wait.exception.details['category'], 'retryable')
            with self.assertRaises(BudgetExceeded) as correct:
                ledger.admit_model('large', usd=2)
            self.assertEqual(correct.exception.details['run_action'], 'continue')
            self.assertFalse(correct.exception.details['retryable'])
            ledger.finish_model('active', accounted=True)
            ledger.usd_spent = 1
            with self.assertRaises(BudgetExceeded) as stop:
                ledger.admit_model('exhausted', usd=.1)
            self.assertEqual(stop.exception.details['run_action'], 'stop')
            self.assertFalse(stop.exception.details['retryable'])

    async def test_transport_retry_only_when_definitely_not_sent(self):
        for kind in (httpx.ConnectTimeout, httpx.ConnectError, httpx.PoolTimeout, httpx.ReadTimeout, httpx.WriteError):
            with self.subTest(kind=kind):
                async with harness() as (client, runtime, calls):
                    attempted = []
                    def fail(request):
                        attempted.append(request)
                        raise kind('private-provider-message', request=request)
                    await runtime.client.aclose()
                    runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
                    response = await client.post(route('openrouter', 'responses'), json=request_body('openrouter', 'responses'))
                    self.assertEqual(response.status_code, 502)
                    info = response.json()['diagnostic']
                    before_send = kind in (httpx.ConnectTimeout, httpx.ConnectError, httpx.PoolTimeout)
                    self.assertEqual(info['retryable'], before_send)
                    self.assertEqual(info['run_action'], 'continue' if before_send else 'stop')
                    self.assertEqual(runtime.ledger.model_accounting_incomplete, not before_send)
                    self.assertEqual(info['upstream_request_sent'], not before_send)
                    self.assertNotIn('private-provider-message', response.text)
                    self.assertEqual(len(attempted), 1)  # gateway never retries inference itself
                    self.assertFalse(runtime.ledger.model_inflight)

    async def test_missing_credentials_stop_without_provider_call(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            async with harness() as (client, runtime, calls):
                response = await client.post(route('openai', 'responses'), json=request_body('openai', 'responses'))
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()['diagnostic']['run_action'], 'stop')
                self.assertFalse(calls)
                self.assertEqual(runtime.ledger.counts['model_requests'], 0)

    async def test_auth_is_checked_once_before_reserving(self):
        import gateway_runtime
        async with harness() as (client, runtime, calls):
            original = gateway_runtime.provider_auth_headers
            count = 0
            def rotating_auth(*args, **kwargs):
                nonlocal count
                count += 1
                if count > 1:
                    raise ValueError('credentials changed after admission')
                return original(*args, **kwargs)
            with patch.object(gateway_runtime, 'provider_auth_headers', side_effect=rotating_auth):
                response = await client.post(route('openrouter', 'responses'), json=request_body('openrouter', 'responses'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(calls), 1)
            self.assertFalse(runtime.ledger.model_inflight)
            self.assertFalse(runtime.ledger.model_accounting_incomplete)

    def test_provider_error_needs_accounting_before_safe_retry(self):
        for status in (400, 401, 403, 404, 429, 500, 502, 503):
            for complete in (False, True):
                result = safe_provider_error(status, 'safe-id', accounting_complete=complete)
                info = json.loads(result.body)['error']
                stop = not complete or status in (401, 403)
                self.assertEqual(info['run_action'], 'stop' if stop else 'continue')
                self.assertEqual(info['retryable'], complete and status in (429, 500, 502, 503))

    def test_unrecognized_request_error_is_nonfatal_without_blind_retry(self):
        self.assertEqual(recovery('new_request_validation_error')['run_action'], 'continue')
        self.assertFalse(recovery('new_request_validation_error')['retryable'])
