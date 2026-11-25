"""Selected authentication retains the real gateway's request and accounting policy."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
import gateway_models
from gateway_runtime import Gateway
from access_selection import resolve_routes
from model_access import DEFAULT_MODEL_ACCESS
from test_gateway import canonical_events


class SelectedAccessGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_subscription_recipe_under_existing_endpoint_preserves_metering_and_rejections(self):
        config = resolve_routes(DEFAULT_MODEL_ACCESS, {
            "anthropic": {"endpoint": "https://api.anthropic.com/v1",
                          "authentication": "claude-subscription"}})["anthropic"]
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": tmp, "TESTBED_RUN_ID": "selected-access",
            "DUNGENESS_ALLOWED_MODELS": '[["anthropic","claude-opus-5"]]',
            "MAX_MODEL_REQUESTS": "4", "MAX_MODEL_TOKENS": "10000", "MAX_MODEL_USD": "1",
            "MAX_SEARCHES": "0", "MAX_FETCHES": "0",
            "DUNGENESS_CREDENTIALS_FILE": str(Path(tmp) / "credentials.json"),
        }, clear=True), patch.dict(gateway_models.MODEL_PROVIDERS, {
            "anthropic": gateway_models.gateway_provider_config(config)}):
            private = Path(tmp) / "credentials.json"
            values = {"CLAUDE_ACCESS_TOKEN": "selected-secret",
                      "CLAUDE_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z"}
            private.write_text(json.dumps(values))
            private.chmod(0o600)
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []
            def upstream(request):
                calls.append(request)
                self.assertEqual(str(request.url), "https://api.anthropic.com/v1/messages")
                self.assertEqual(request.headers["authorization"], "Bearer selected-secret")
                self.assertNotIn("x-api-key", request.headers)
                return httpx.Response(200, json={"id": "msg-1", "type": "message", "role": "assistant",
                    "model": "claude-opus-5", "content": [{"type": "text", "text": "42"}],
                    "stop_reason": "end_turn", "usage": {"input_tokens": 100, "output_tokens": 5,
                    "cache_read_input_tokens": 20, "cache_creation_input_tokens": 0}})
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream), follow_redirects=False)
            payload = {"model": "claude-opus-5", "max_tokens": 32,
                       "messages": [{"role": "user", "content": "Return 42"}]}
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        response = await client.post("/model/anthropic/v1/messages", json=payload,
                                                     headers={"authorization": "Bearer placeholder"})
                        self.assertEqual(response.status_code, 200, response.text)
                        for body in ({**payload, "model": "unapproved"},
                                     {**payload, "tools": [{"type": "web_search_20250305", "name": "web_search"}]}):
                            self.assertGreaterEqual((await client.post(
                                "/model/anthropic/v1/messages", json=body)).status_code, 400)
                        private.write_text(json.dumps({**values, "CLAUDE_ACCESS_TOKEN_EXPIRES_AT": "2000-01-01T00:00:00Z"}))
                        self.assertGreaterEqual((await client.post(
                            "/model/anthropic/v1/messages", json=payload)).status_code, 400)
                self.assertEqual(len(calls), 1)
                receipt, = canonical_events(runtime.ledger.directory, "model.accounting")
                self.assertEqual(receipt["accounting_basis"], "provider_usage")
                self.assertEqual(receipt["cached_input_tokens"], 20)
                self.assertGreater(receipt["normalized_usd"], 0)
                self.assertIsNone(receipt["billed_usd"])
                self.assertNotIn("selected-secret", (Path(tmp) / "events.jsonl").read_text())
            finally:
                await runtime.client.aclose()
