"""Installed profiles: auth isolation, streaming usage, expiry and spend caps."""
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
from provider_profiles import PROFILES


class LocalSubscriptionProfilesTests(unittest.IsolatedAsyncioTestCase):
    def test_frozen_grok_reference_includes_the_long_context_tier(self):
        schedule = json.loads((Path(__file__).resolve().parents[3] /
            'docs/examples/local-subscription-pricing-20261030.json').read_text())
        price = next(p for p in schedule['entries'] if p['provider'] == 'grok-subscription')
        for count, expected in ((200000, .400006), (200001, .800016), (500000, 2.000012)):
            self.assertAlmostEqual(gateway_pricing.request_usd(
                {'input_tokens': count, 'output_tokens': 1}, price), expected)

    async def test_installed_routes_preserve_requests_and_meter_subscription_usage(self):
        for provider in ('grok-subscription', 'minimax-subscription'):
            profile = PROFILES[provider]
            model = next(iter(profile['models']))
            rates = {'provider': provider, 'upstream_id': profile['models'][model]['catalog'],
                     'request_models': [model], 'input_per_mtok': 2,
                     'cached_read_per_mtok': .5, 'output_per_mtok': 6}
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as folder:
                env = {'TESTBED_USAGE_DIR': folder, 'MAX_MODEL_USD': '.0001',
                       'MAX_MODEL_REQUESTS': '10', 'MAX_MODEL_TOKENS': '1000000',
                       'DUNGENESS_ALLOWED_MODELS': json.dumps([[provider, model]]),
                       profile['credential_env']: 'synthetic-private-provider-token',
                       profile['credential_env'] + '_EXPIRES_AT':
                           (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}
                with patch.dict(os.environ, env), patch.object(gateway_pricing, 'MODEL_PRICING', [rates]):
                    runtime = Gateway()
                    await runtime.client.aclose()
                    calls = []

                    def upstream(request):
                        calls.append(request)
                        self.assertEqual(str(request.url), profile['base_url'] + '/chat/completions')
                        self.assertEqual(request.headers['authorization'], 'Bearer synthetic-private-provider-token')
                        self.assertEqual(request.headers['user-agent'], 'dungeness-gateway/1')
                        self.assertNotIn('cookie', request.headers)
                        self.assertNotIn('x-client-version', request.headers)
                        body = json.loads(request.content)
                        self.assertEqual(body['model'], model)
                        self.assertEqual(body['reasoning_effort'], 'high')
                        self.assertTrue(body['stream_options']['include_usage'])
                        return httpx.Response(200, headers={'content-type': 'text/event-stream'}, content=
                            b'data: {"choices":[],"usage":{"prompt_tokens":100,"completion_tokens":10,"prompt_tokens_details":{"cached_tokens":20}}}\n\ndata: [DONE]\n\n')

                    runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                    try:
                        with patch.object(gateway, 'gateway', runtime):
                            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app), base_url='http://gateway') as client:
                                route = f'/model/{provider}/v1/chat/completions'
                                body = {'model': model, 'messages': [{'role': 'user', 'content': 'test'}],
                                        'reasoning_effort': 'high', 'stream': True}
                                if profile['credential_kind'] == 'session-token':
                                    with patch.dict(os.environ, {profile['credential_env'] + '_EXPIRES_AT': '2000-01-01T00:00:00Z'}):
                                        rejected = await client.post(route, json=body)
                                        self.assertEqual(rejected.status_code, 400)
                                        self.assertEqual(calls, [])
                                reply = await client.post(route, json=body, headers={'authorization': 'Bearer testbed', 'cookie': 'private=not-forwarded'})
                                self.assertEqual(reply.status_code, 200, reply.text)
                                exhausted = await client.post(route, json=body)
                                self.assertEqual(exhausted.status_code, 429, exhausted.text)
                        self.assertEqual(len(calls), 1)
                        raw = (Path(folder) / 'events.jsonl').read_text()
                        self.assertNotIn('synthetic-private-provider-token', raw)
                        accounting = [e['data'] for e in map(json.loads, raw.splitlines()) if e['kind'] == 'model.accounting']
                        self.assertEqual(len(accounting), 1)
                        self.assertAlmostEqual(accounting[0]['normalized_usd'], .00023)
                        self.assertIsNone(accounting[0]['billed_usd'])
                    finally:
                        await runtime.client.aclose()
