"""Real gateway routing/accounting with a deterministic upstream, no paid calls."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import httpx
import test_gateway
import gateway
import gateway_pricing
from gateway_runtime import Gateway
from configured_fixture import configured_profiles

class ConfiguredProviderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.enterContext(configured_profiles())

    async def test_protocol_rejection_releases_reservation_but_unknown_usage_blocks(self):
        rejection = (b'Failed to deserialize the JSON body into the target type: '
                     b'tools[0]: missing field `function` at line 1 column 6238')
        provider, name = 'example-session', 'example-model'
        reference = {'provider': provider, 'upstream_id': 'example/example-model', 'request_models': [name],
                     'input_per_mtok': 2, 'cached_read_per_mtok': .5, 'cache_write_per_mtok': 2,
                     'output_per_mtok': 6, 'text_only': True}
        for status, body, mime, recoverable in (
            (400, b'{"error": {"type": "invalid_request_error"}}', 'application/json', True),
            (422, rejection, 'text/plain; charset=utf-8', False),
            (422, b'Unprocessable entity', 'text/plain', False),
            (500, rejection, 'text/plain', False),
            (200, b'{"choices": []}', 'application/json', False),
        ):
            with self.subTest(status=status, body=body), tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
                'TESTBED_USAGE_DIR': temp, 'MAX_MODEL_REQUESTS': '20', 'MAX_MODEL_TOKENS': '1000000',
                'DUNGENESS_ALLOWED_MODELS': json.dumps([[provider, name]]),
                'EXAMPLE_SESSION_TOKEN': 'private-subscription-session',
                'EXAMPLE_SESSION_TOKEN_EXPIRES_AT': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
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
                            route = '/model/example-session/v1/chat/completions'
                            payload = {'model': name, 'messages': [{'role': 'user', 'content': 'solve'}]}
                            first = await client.post(route, json=payload)
                            self.assertEqual(first.status_code, status)
                            if status >= 400:
                                self.assertEqual(first.json()['error']['upstream_status'], status)
                                self.assertTrue(first.json()['error']['request_id'])
                                self.assertNotIn(rejection.decode(), first.text)
                            else:
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
                        self.assertEqual(receipts[0]['http_status'], 400)
                        self.assertEqual(receipts[0]['total_tokens'], 0)
                        self.assertEqual(receipts[0]['normalized_usd'], 0)
                        self.assertIsNone(receipts[0]['billed_usd'])
                        self.assertEqual(receipts[1]['accounting_basis'], 'provider_usage')
                        self.assertAlmostEqual(receipts[1]['normalized_usd'], .00026)
                    else:
                        self.assertEqual(receipts[0]['accounting_method'], 'unavailable')
                finally:
                    await runtime.client.aclose()

    async def test_configured_stream_auth_pinned_model_and_expiry(self):
        provider, name = 'example-session', 'example-model'
        reference = {'provider': provider, 'upstream_id': 'example/example-model', 'request_models': [name],
                     'input_per_mtok': 2, 'cached_read_per_mtok': .5, 'cache_write_per_mtok': 2,
                     'output_per_mtok': 6, 'text_only': True}
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            'TESTBED_USAGE_DIR': temp, 'MAX_MODEL_REQUESTS': '20', 'MAX_MODEL_TOKENS': '1000000',
            'DUNGENESS_ALLOWED_MODELS': json.dumps([[provider, name]]),
            'EXAMPLE_SESSION_TOKEN': 'private-subscription-session',
            'EXAMPLE_SESSION_TOKEN_EXPIRES_AT': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        }), patch.object(gateway_pricing, 'MODEL_PRICING', [reference]):
            runtime = Gateway(); await runtime.client.aclose(); calls = []
            def upstream(request):
                calls.append(request)
                self.assertEqual(str(request.url), 'https://session.example.invalid/v1/chat/completions')
                self.assertEqual(request.headers['authorization'], 'Bearer private-subscription-session')
                self.assertEqual(request.headers['user-agent'], 'dungeness-gateway/1')
                for header in ('x-untrusted-auth', 'x-auth-response',
                               'x-client-version', 'x-model-override'):
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
                        route = '/model/example-session/v1/chat/completions'
                        payload = {'model': name, 'messages': [{'role': 'user', 'content': 'solve'}], 'stream': True}
                        response = await client.post(route, json=payload, headers={
                            'authorization': 'Bearer agent-placeholder', 'x-model-override': 'unmapped-model-latest',
                            'x-untrusted-auth': 'spoofed',
                            'x-auth-response': 'authenticate-response',
                            'x-client-version': '1.0.62',
                            'user-agent': 'solver-cli'})
                        self.assertEqual(response.status_code, 200, response.text)
                        for extra in ({'search_parameters': {'mode': 'auto'}}, {'model': 'unmapped-model'},
                                      {'tools': [{'type': 'web_search'}]}, {'plugins': [{'id': 'web'}]}):
                            response = await client.post(route, json={**payload, **extra})
                            self.assertEqual(response.status_code, 400, response.text)
                        os.environ['EXAMPLE_SESSION_TOKEN_EXPIRES_AT'] = '2000-01-01T00:00:00Z'
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


class ProviderRegistryTests(unittest.TestCase):
    def test_default_registry_has_no_configured_providers(self):
        from provider_profiles import load_profiles
        self.assertEqual(load_profiles(), {})

    def test_fresh_gateway_loads_only_the_installed_operator_registry(self):
        from configured_fixture import FIXTURES
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for path in source.iterdir():
                if path.is_file() and path.suffix in {".py", ".json", ".yaml"}:
                    shutil.copy2(path, root / path.name)
            (root / "providers.json").write_text(json.dumps({"schema_version": 1, "providers": FIXTURES}))
            script = """
from provider_profiles import PROFILES
from gateway_models import MODEL_PROVIDERS
assert set(PROFILES) == {"example-api", "example-session"}
for name, profile in PROFILES.items():
    configured = MODEL_PROVIDERS[name]
    assert configured["upstream_default"] == profile["base_url"]
    assert configured["routes"] == set(profile["routes"])
assert MODEL_PROVIDERS["example-api"]["authentication"]["sources"][0]["headers"]["authorization"]["env"] == "EXAMPLE_API_KEY"
"""
            result = subprocess.run([sys.executable, "-c", script], cwd=root,
                                    env={**os.environ, "PYTHONPATH": str(root)},
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
