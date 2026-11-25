"""Real registered routes; synthetic HTTPS responses, never live credentials."""
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
from gateway_runtime import Gateway
from test_gateway import canonical_events
from access_selection import resolve_endpoint
from model_access import DEFAULT_MODEL_ACCESS

MODEL = "gemini-4-carbon"
PAYLOAD = {"model": MODEL, "messages": [{"role": "user", "content": "Return 42"}],
           "max_completion_tokens": 512, "reasoning_effort": "low"}
RESULT = {
    "candidates": [{"content": {"role": "model", "parts": [{"text": "42"}]}, "finishReason": "STOP"}],
    "usageMetadata": {"promptTokenCount": 100, "cachedContentTokenCount": 40,
                      "candidatesTokenCount": 10, "thoughtsTokenCount": 20, "totalTokenCount": 130},
}


@asynccontextmanager
async def registered_route(provider, values=None, redirect=False):
    with tempfile.TemporaryDirectory() as temp:
        private = Path(temp) / "credentials.json"
        private.write_text(json.dumps(values if values is not None else {
            "GEMINI_API_KEY": "synthetic-api-key", "VERTEX_ACCESS_TOKEN": "synthetic-access-token",
            "VERTEX_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z", "VERTEX_PROJECT_ID": "sample-project"}))
        private.chmod(0o600)
        with patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": str(Path(temp) / "usage"), "TESTBED_RUN_ID": "google-routes",
            "DUNGENESS_CREDENTIALS_FILE": str(private),
            "DUNGENESS_ALLOWED_MODELS": json.dumps([[provider, MODEL]]),
            "DUNGENESS_REQUIRE_MODEL_ALLOWLIST": "1",
            "MAX_MODEL_REQUESTS": "4", "MAX_MODEL_TOKENS": "8192", "MAX_MODEL_USD": "1",
            "MAX_SEARCHES": "0", "MAX_FETCHES": "0",
        }, clear=True):
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []

            def upstream(request):
                calls.append(request)
                if redirect:
                    return httpx.Response(307, headers={"location": "https://unapproved.invalid/steal"})
                return httpx.Response(200, json=RESULT)

            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream), follow_redirects=False)
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        yield client, runtime, calls
            finally:
                await runtime.client.aclose()


class RegisteredGoogleRoutesTests(unittest.IsolatedAsyncioTestCase):
    async def test_routes_use_private_credentials_fixed_destinations_and_bundled_prices(self):
        for selection in (
            {"endpoint": "https://generativelanguage.googleapis.com/v1beta", "authentication": "api-key"},
            {"endpoint": "https://aiplatform.googleapis.com/v1", "authentication": "bearer"},
        ):
            provider = resolve_endpoint(DEFAULT_MODEL_ACCESS, selection)
            with self.subTest(provider=provider):
                async with registered_route(provider) as (client, runtime, calls):
                    listing = await client.get(f"/model/{provider}/v1/models")
                    self.assertEqual([entry["id"] for entry in listing.json()["data"]], [MODEL])
                    self.assertFalse(calls)
                    response = await client.post(f"/model/{provider}/v1/chat/completions",
                        json=PAYLOAD, headers={"authorization": "Bearer harness-placeholder"})
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertEqual(response.json()["choices"][0]["message"]["content"], "42")
                    self.assertEqual(len(calls), 1)
                    request = calls[0]
                    if provider == "google":
                        self.assertEqual(str(request.url),
                            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent")
                        self.assertEqual(request.headers["x-goog-api-key"], "synthetic-api-key")
                        self.assertNotIn("authorization", request.headers)
                    else:
                        self.assertEqual(str(request.url), "https://aiplatform.googleapis.com/v1/projects/"
                            f"sample-project/locations/global/publishers/google/models/{MODEL}:generateContent")
                        self.assertEqual(request.headers["authorization"], "Bearer synthetic-access-token")
                        self.assertEqual(request.headers["x-goog-user-project"], "sample-project")
                    self.assertNotIn("harness-placeholder", str(request.headers))
                    receipt, = canonical_events(runtime.ledger.directory, "model.accounting")
                    self.assertEqual(receipt["output_tokens"], 30)
                    self.assertEqual(receipt["reasoning_tokens"], 20)
                    self.assertAlmostEqual(receipt["normalized_usd"], .000424)
                    events = (runtime.ledger.directory / "events.jsonl").read_text()
                    self.assertNotIn("synthetic-access-token", events)
                    self.assertNotIn("synthetic-api-key", events)

    async def test_missing_expired_and_path_injection_inputs_fail_before_admission(self):
        base = {"VERTEX_ACCESS_TOKEN": "synthetic-access-token",
                "VERTEX_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
                "VERTEX_PROJECT_ID": "sample-project"}
        cases = [{}, {**base, "VERTEX_ACCESS_TOKEN_EXPIRES_AT": "2000-01-01T00:00:00Z"}]
        cases += [{**base, "VERTEX_PROJECT_ID": value} for value in
                  ("../escape", "https://unapproved.invalid", "project?key=private-sentinel",
                   "project%2fescape", "project/../../escape", "project\\escape", "")]
        for values in cases:
            async with registered_route("google-vertex", values) as (client, runtime, calls):
                before = dict(runtime.ledger.counts)
                response = await client.post("/model/google-vertex/v1/chat/completions", json=PAYLOAD)
                self.assertEqual(response.json()["diagnostic"]["code"], "provider_credentials_unavailable")
                self.assertNotIn("private-sentinel", response.text)
                self.assertFalse(calls)
                self.assertEqual(runtime.ledger.counts, before)

    async def test_redirects_do_not_forward_credentials(self):
        for provider in ("google", "google-vertex"):
            async with registered_route(provider, redirect=True) as (client, _, calls):
                response = await client.post(f"/model/{provider}/v1/chat/completions", json=PAYLOAD)
                self.assertEqual(response.status_code, 502)
                self.assertEqual(len(calls), 1)
                self.assertNotIn("location", response.headers)

    async def test_harness_cannot_override_project_or_enable_remote_tools(self):
        async with registered_route("google-vertex") as (client, runtime, calls):
            before = dict(runtime.ledger.counts)
            for extra in ({"project": "another-project"}, {"tools": [{"googleSearch": {}}]}):
                response = await client.post("/model/google-vertex/v1/chat/completions",
                                             json={**PAYLOAD, **extra})
                self.assertEqual(response.status_code, 400)
            self.assertFalse(calls)
            self.assertEqual(runtime.ledger.counts, before)
