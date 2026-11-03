"""Model-free adversarial tests using synthetic credentials only."""
import asyncio
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway  # Offline import environment.
import gateway
import gateway_runtime
from gateway_runtime import Gateway
from gateway_security import SecretFilter, RequestBoundsMiddleware

KEY = 'synthetic-secret-key-abcdefghijklmnopqrstuvwxyz'
USAGE = {"input_tokens": 100, "output_tokens": 10}


class FilteringTests(unittest.TestCase):
    def test_every_transport_split_and_single_byte_chunks(self):
        raw = b'before ' + KEY.encode() + b' after ' + KEY.encode()
        expected = b'before [REDACTED] after [REDACTED]'
        for split in range(len(raw) + 1):
            f = SecretFilter({KEY})
            self.assertEqual(f.feed(raw[:split]) + f.feed(raw[split:]) + f.feed(b'', final=True), expected)
        f = SecretFilter({KEY})
        self.assertEqual(b''.join(f.feed(bytes([c])) for c in raw) + f.feed(b'', final=True), expected)

    def test_short_events_are_not_delayed_by_long_credentials(self):
        f = SecretFilter({'credential-' + 'a' * 8000})
        self.assertEqual(f.feed(b'data: {"delta":"hi"}\n\n'), b'data: {"delta":"hi"}\n\n')

    def test_json_escaped_secret_and_overlapping_values(self):
        secret = 'synthetic-"quoted"-\\-key'
        f = SecretFilter({secret, 'overlap', 'overlapping'})
        body = json.dumps({'message': secret + ' overlapping'}).encode()
        clean = f.feed(body, final=True)
        self.assertEqual(json.loads(clean)['message'], '[REDACTED] [REDACTED]')

    def test_hosted_gateway_refuses_missing_or_invalid_allowlist(self):
        with patch.dict(os.environ, {'DUNGENESS_REQUIRE_MODEL_ALLOWLIST': '1',
                                     'DUNGENESS_ALLOWED_MODELS': ''}):
            with self.assertRaisesRegex(ValueError, 'allowlist'):
                Gateway()
        for invalid in ('[]', '{}', '["model"]', '[["openai", null]]'):
            with patch.dict(os.environ, {'DUNGENESS_ALLOWED_MODELS': invalid}):
                with self.assertRaises(ValueError):
                    Gateway()


class BoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, handler, action, **environment):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            'TESTBED_USAGE_DIR': tmp, 'OPENAI_API_KEY': KEY,
            'DUNGENESS_ALLOWED_MODELS': '[["openai","gpt-5.6-sol"]]',
            'DUNGENESS_REQUIRE_MODEL_ALLOWLIST': '1', 'MAX_MODEL_REQUESTS': '100',
            'MAX_MODEL_TOKENS': '1000000', 'MAX_MODEL_USD': '100', **environment,
        }):
            runtime = Gateway()
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=False)
            try:
                with patch.object(gateway, 'gateway', runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url='http://gateway') as client:
                        await action(client, runtime)
                for p in Path(tmp).rglob('*'):
                    if p.is_file():
                        self.assertNotIn(KEY.encode(), p.read_bytes(), str(p))
            finally:
                await runtime.client.aclose()

    async def test_provider_error_is_structured_without_echoed_body_or_headers(self):
        calls = []
        def handler(request):
            calls.append(request)
            self.assertEqual(request.headers['authorization'], 'Bearer ' + KEY)
            return httpx.Response(401, json={'error': {'message': 'Invalid key: ' + KEY}},
                                  headers={'x-secret': KEY, 'content-type': 'text/' + KEY})
        async def action(client, runtime):
            reply = await client.post('/model/openai/v1/responses', json={'model':'gpt-5.6-sol','input':'fixture'})
            self.assertEqual(reply.status_code, 401)
            error = reply.json()['error']
            self.assertEqual(error['code'], 'provider_authentication_failed')
            self.assertFalse(error['retryable'])
            self.assertTrue(error['request_id'])
            self.assertNotIn(KEY, reply.text + str(reply.headers))
        await self.exercise(handler, action)
        self.assertEqual(len(calls), 1)

    async def test_successful_json_redacts_before_client_and_trace_without_losing_usage(self):
        def handler(request):
            return httpx.Response(200, json={'output_text': KEY, 'usage': USAGE})
        async def action(client, runtime):
            reply = await client.post('/model/openai/v1/responses', json={'model':'gpt-5.6-sol','input':'fixture'})
            self.assertEqual(reply.json()['output_text'], '[REDACTED]')
            self.assertGreater(runtime.ledger.status()['usage']['normalized_usd'], 0)
            self.assertFalse(runtime.ledger.model_accounting_incomplete)
        await self.exercise(handler, action)

    async def test_streamed_secret_split_across_bytes_is_redacted_and_usage_retained(self):
        wire = ('data: '+json.dumps({'type':'response.output_text.delta','delta':KEY})+'\n\n'
                +'data: '+json.dumps({'type':'response.completed','response':{'usage':USAGE}})+'\n\n').encode()
        class Stream(httpx.AsyncByteStream):
            async def __aiter__(self):
                for value in wire:
                    yield bytes([value])
        def handler(request):
            return httpx.Response(200, stream=Stream(), headers={'content-type':'text/event-stream'})
        async def action(client, runtime):
            reply = await client.post('/model/openai/v1/responses', json={'model':'gpt-5.6-sol','input':'fixture','stream':True})
            self.assertEqual(reply.status_code, 200)
            self.assertNotIn(KEY, reply.text)
            self.assertIn('[REDACTED]', reply.text)
            self.assertIn('response.completed', reply.text)
            self.assertFalse(runtime.ledger.model_accounting_incomplete)
            self.assertGreater(runtime.ledger.status()['usage']['normalized_usd'], 0)
        await self.exercise(handler, action)

    async def test_no_secret_read_routes_traversal_or_arbitrary_provider_destinations(self):
        def handler(request):
            self.fail('No provider call is authorized by these queries')
        async def action(client, runtime):
            paths = ['/healthz','/status','/metrics','/key','/credentials','/env','/debug',
                     '/model/openai/v1/models','/model/openai/v1/files',
                     '/model/openai/v1/../../credentials','/task/files/auth.json',
                     '/task/files/%2e%2e%2fauth.json']
            for path in paths:
                reply = await client.get(path)
                self.assertNotIn(KEY, reply.text + str(reply.headers))
                if path not in ['/healthz','/status','/metrics','/model/openai/v1/models']:
                    self.assertGreaterEqual(reply.status_code,400)
            for payload in ({'model':'not-declared','input':'fixture'},
                            {'model':'gpt-5.6-sol','input':'fixture','base_url':'https://attacker.invalid'}):
                reply = await client.post('/model/openai/v1/responses',json=payload)
                self.assertEqual(reply.status_code,400)
                self.assertNotIn(KEY,reply.text)
        await self.exercise(handler,action)

    async def test_redirect_does_not_forward_credentials(self):
        calls=[]
        def handler(request):
            calls.append(str(request.url))
            return httpx.Response(307,headers={'location':'https://attacker.invalid/'+KEY})
        async def action(client,runtime):
            reply=await client.post('/model/openai/v1/responses',json={'model':'gpt-5.6-sol','input':'fixture'})
            self.assertEqual(reply.status_code,502)
            self.assertNotIn('location',reply.headers)
            self.assertNotIn(KEY,reply.text)
        await self.exercise(handler,action)
        self.assertEqual(len(calls),1)

    async def test_oversized_response_fails_closed_on_accounting(self):
        def handler(request):return httpx.Response(200,content=b'x'*200)
        async def action(client,runtime):
            with patch.object(gateway_runtime,'MAX_RESPONSE_BYTES',100):
                reply=await client.post('/model/openai/v1/responses',json={'model':'gpt-5.6-sol','input':'fixture'})
            self.assertEqual(reply.status_code,502)
            self.assertEqual(reply.json()['error']['code'],'upstream_response_too_large')
            self.assertTrue(runtime.ledger.model_accounting_incomplete)
        await self.exercise(handler,action)

    async def test_disconnect_drains_more_than_one_queue_of_events(self):
        class Stream(httpx.AsyncByteStream):
            async def __aiter__(self):
                for _ in range(100):
                    yield b'data: {"type":"response.output_text.delta","delta":"fixture"}\n\n'
                yield ('data: '+json.dumps({'type':'response.completed',
                    'response':{'usage':USAGE}})+'\n\n').encode()
        def handler(request):
            return httpx.Response(200,stream=Stream(),headers={'content-type':'text/event-stream'})
        async def action(client,runtime):
            events=[{'type':'http.request','body':json.dumps({'model':'gpt-5.6-sol',
                     'input':'fixture','stream':True}).encode(),'more_body':False}]
            async def receive():
                return events.pop(0) if events else {'type':'http.disconnect'}
            async def send(message):pass
            await gateway.app({'type':'http','method':'POST','path':'/model/openai/v1/responses',
                'query_string':b'', 'headers':[(b'content-type',b'application/json')]},receive,send)
            tasks=list(gateway_runtime.BACKGROUND_TASKS)
            if tasks: await asyncio.wait_for(asyncio.gather(*tasks),5)
            self.assertFalse(runtime.ledger.model_accounting_incomplete)
            self.assertGreater(runtime.ledger.status()['usage']['normalized_usd'],0)
        await self.exercise(handler,action)

    async def test_slow_request_body_releases_capacity(self):
        async def app(scope,receive,send):raise AssertionError('Incomplete request reached app')
        middleware=RequestBoundsMiddleware(app)
        async def receive():await asyncio.sleep(10)
        sent=[]
        async def send(message):sent.append(message)
        with patch('gateway_security.REQUEST_BODY_TIMEOUT_SECONDS',0.001):
            await middleware({'type':'http','path':'/model/openai/v1/responses'},receive,send)
        self.assertEqual(sent[0]['status'],408)
        self.assertEqual(middleware.active,0)

    async def test_active_request_bound_rejects_before_reading_body(self):
        invoked=[]
        async def app(scope,receive,send):invoked.append(True)
        middleware=RequestBoundsMiddleware(app);middleware.active=8
        async def receive():raise AssertionError('Capacity rejection must not read body')
        sent=[]
        async def send(message):sent.append(message)
        await middleware({'type':'http','path':'/model/openai/v1/responses'},receive,send)
        self.assertEqual(sent[0]['status'],429)
        self.assertFalse(invoked)
        self.assertEqual(middleware.active,8)

    async def test_request_body_limit_counts_chunks_without_trusting_content_length(self):
        invoked=[]
        async def app(scope,receive,send):invoked.append(True)
        middleware=RequestBoundsMiddleware(app)
        messages=iter([{'type':'http.request','body':b'x'*60,'more_body':True},
                       {'type':'http.request','body':b'x'*60,'more_body':False}])
        sent=[]
        async def receive():return next(messages)
        async def send(message):sent.append(message)
        with patch('gateway_security.MAX_REQUEST_BYTES',100):
            await middleware({'type':'http','path':'/model/openai/v1/responses'},receive,send)
        self.assertEqual(sent[0]['status'],413)
        self.assertFalse(invoked)
        self.assertEqual(middleware.active,0)
