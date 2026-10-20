"""Real gateway routing/accounting with a deterministic upstream, no paid calls."""
from datetime import datetime, timedelta, timezone
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
from gateway_runtime import Gateway

class ConfiguredProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_grok_rejection_releases_reservation_but_unknown_usage_blocks(self):
        rejection = (b'Failed to deserialize the JSON body into the target type: '
                     b'tools[0]: missing field `function` at line 1 column 6238')
        provider, name = 'grok-subscription', 'grok-4.7'
        reference = {'provider': provider, 'upstream_id': 'x-ai/grok-4.7', 'request_models': [name],
                     'input_per_mtok': 2, 'cached_read_per_mtok': .5, 'cache_write_per_mtok': 2,
                     'output_per_mtok': 6, 'text_only': True}
        for status, body, mime, recoverable in (
            (422, rejection, 'text/plain; charset=utf-8', True),
            (422, b'Unprocessable entity', 'text/plain', False),
            (500, rejection, 'text/plain', False),
            (200, b'{"choices": []}', 'application/json', False),
        ):
            with self.subTest(status=status, body=body), tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
                'TESTBED_USAGE_DIR': temp, 'MAX_MODEL_REQUESTS': '20', 'MAX_MODEL_TOKENS': '1000000',
                'DUNGENESS_ALLOWED_MODELS': json.dumps([[provider, name]]),
                'GROK_SUBSCRIPTION_TOKEN': 'private-subscription-session',
                'GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            }), patch.object(gateway_pricing, 'MODEL_PRICING', [reference]):
                runtime = Gateway(); await runtime.client.aclose(); calls = []
                def upstream(request):
                    calls.append(request)
                    if len(calls) == 1:
                        return httpx.Response(status, content=body, headers={'content-type': mime})
                    return httpx.Response(200, json={'choices': [], 'usage': {
                        'prompt_tokens': 100, 'completion_tokens': 10, 'total_tokens': 110}})
                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                try:
                    with patch.object(gateway, 'gateway', runtime):
                        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app), base_url='http://gateway') as client:
                            route = '/model/grok-subscription/v1/chat/completions'
                            payload = {'model': name, 'messages': [{'role': 'user', 'content': 'solve'}]}
                            first = await client.post(route, json=payload)
                            self.assertEqual(first.status_code, status)
                            self.assertEqual(first.content, body)
                            self.assertEqual(runtime.ledger.model_inflight, {})
                            second = await client.post(route, json=payload)
                            self.assertEqual(second.status_code, 200 if recoverable else 429, second.text)
                    receipts = [e['data'] for e in map(json.loads, (Path(temp) / 'events.jsonl').read_text().splitlines())
                                if e['kind'] == 'model.accounting']
                    self.assertEqual(len(calls), 2 if recoverable else 1)
                    # Even a free, rejected request consumes the request-count limit.
                    self.assertEqual(runtime.ledger.counts['model_requests'], len(calls))
                    self.assertEqual(runtime.ledger.model_accounting_incomplete, not recoverable)
                    if recoverable:
                        self.assertEqual(receipts[0]['accounting_basis'], 'input_rejected_before_generation')
                        self.assertEqual(receipts[0]['accounting_method'], 'gateway')
                        self.assertEqual(receipts[0]['http_status'], 422)
                        self.assertEqual(receipts[0]['total_tokens'], 0)
                        self.assertEqual(receipts[0]['normalized_usd'], 0)
                        self.assertIsNone(receipts[0]['billed_usd'])
                        self.assertEqual(receipts[1]['accounting_basis'], 'provider_usage')
                        self.assertAlmostEqual(receipts[1]['normalized_usd'], .00026)
                    else:
                        self.assertEqual(receipts[0]['accounting_method'], 'unavailable')
                finally:
                    await runtime.client.aclose()

    def test_grok_zero_usage_requires_exact_provider_status_and_decoder_error(self):
        from gateway_runtime import rejected_before_generation
        body = (b'Failed to deserialize the JSON body into the target type: '
                b'tools[0]: missing field `function` at line 1 column 6238')
        self.assertTrue(rejected_before_generation(body, 'text/plain', 422, provider='grok-subscription'))
        for provider, status, mime, response in (
            ('xai', 422, 'text/plain', body),
            ('openrouter', 422, 'text/plain', body),
            ('grok-subscription', 200, 'text/plain', body),
            ('grok-subscription', 422, 'text/event-stream', body),
            ('grok-subscription', 422, 'application/json', body),
            ('grok-subscription', 422, 'text/plain', body + b'\ngenerated output'),
            ('grok-subscription', 422, 'text/plain', body + b' ' * 4096),
            ('grok-subscription', 422, 'text/plain', b'\xff'),
        ):
            with self.subTest(provider=provider, status=status, mime=mime):
                self.assertFalse(rejected_before_generation(response, mime, status, provider=provider))

    async def test_grok_subscription_stream_auth_pinned_model_and_expiry(self):
        provider, name = 'grok-subscription', 'grok-4.7'
        reference = {'provider': provider, 'upstream_id': 'x-ai/grok-4.7', 'request_models': [name],
                     'input_per_mtok': 2, 'cached_read_per_mtok': .5, 'cache_write_per_mtok': 2,
                     'output_per_mtok': 6, 'text_only': True}
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            'TESTBED_USAGE_DIR': temp, 'MAX_MODEL_REQUESTS': '20', 'MAX_MODEL_TOKENS': '1000000',
            'DUNGENESS_ALLOWED_MODELS': json.dumps([[provider, name]]),
            'GROK_SUBSCRIPTION_TOKEN': 'private-subscription-session',
            'GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        }), patch.object(gateway_pricing, 'MODEL_PRICING', [reference]):
            runtime = Gateway(); await runtime.client.aclose(); calls = []
            def upstream(request):
                calls.append(request)
                self.assertEqual(str(request.url), 'https://cli-chat-proxy.grok.com/v1/chat/completions')
                self.assertEqual(request.headers['authorization'], 'Bearer private-subscription-session')
                self.assertEqual(request.headers['user-agent'], 'dungeness-gateway/1')
                for header in ('x-xai-token-auth', 'x-authenticateresponse',
                               'x-grok-client-version', 'x-grok-model-override'):
                    self.assertNotIn(header, request.headers)
                payload = json.loads(request.content)
                self.assertEqual(payload['model'], name)
                self.assertTrue(payload['stream_options']['include_usage'])
                class Stream(httpx.AsyncByteStream):
                    async def __aiter__(self):
                        yield b'data: {"choices":[],"usage":{"prompt_tokens":100,"completion_tokens":10}}\n\ndata: [DONE]\n\n'
                return httpx.Response(200, stream=Stream(), headers={'content-type': 'text/event-stream'})
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, 'gateway', runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app), base_url='http://gateway') as client:
                        route = '/model/grok-subscription/v1/chat/completions'
                        payload = {'model': name, 'messages': [{'role': 'user', 'content': 'solve'}], 'stream': True}
                        response = await client.post(route, json=payload, headers={
                            'authorization': 'Bearer agent-placeholder', 'x-grok-model-override': 'grok-build-latest',
                            'x-xai-token-auth': 'spoofed',
                            'x-authenticateresponse': 'authenticate-response',
                            'x-grok-client-version': '1.0.62',
                            'user-agent': 'solver-cli'})
                        self.assertEqual(response.status_code, 200, response.text)
                        for extra in ({'search_parameters': {'mode': 'auto'}}, {'model': 'grok-build'},
                                      {'tools': [{'type': 'web_search'}]}, {'plugins': [{'id': 'web'}]}):
                            response = await client.post(route, json={**payload, **extra})
                            self.assertEqual(response.status_code, 400, response.text)
                        os.environ['GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT'] = '2000-01-01T00:00:00Z'
                        response = await client.post(route, json=payload)
                        self.assertEqual(response.status_code, 400, response.text)
                        self.assertIn('expired', response.text)
                self.assertEqual(len(calls), 1)
                events = (Path(temp) / 'events.jsonl').read_text()
                self.assertNotIn('private-subscription-session', events)
                receipts = [event['data'] for event in map(json.loads, events.splitlines()) if event['kind'] == 'model.accounting']
                self.assertEqual(len(receipts), 1)
                self.assertAlmostEqual(receipts[0]['normalized_usd'], .00026)
                self.assertIsNone(receipts[0]['billed_usd'])
            finally: await runtime.client.aclose()
