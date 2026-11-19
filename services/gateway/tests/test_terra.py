"""Qualify Terra's bundled prices and Responses routes without paid calls."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway  # Establish the offline gateway environment before imports.
import gateway
from gateway_models import extract_usage
from gateway_pricing import pricing_for_request, request_pricing_rates, request_usd
from gateway_runtime import Gateway


MODEL = "gpt-6.1-terra"
RAW_USAGE = {
    "input_tokens": 1000,
    "input_tokens_details": {"cached_tokens": 200, "cache_write_tokens": 300},
    "output_tokens": 100,
    "output_tokens_details": {"reasoning_tokens": 75},
    "total_tokens": 1100,
}
# 500 ordinary + 200 cached + 300 written input tokens, then 100 output
# tokens (already including 75 reasoning tokens).
BASE_COST = 0.001385


class TerraPricingTests(unittest.TestCase):
    def test_json_and_sse_settle_cache_writes_and_reasoning_identically(self):
        response = {"model": MODEL, "usage": RAW_USAGE, "output": []}
        bodies = [
            (json.dumps(response).encode(), "application/json"),
            (("data: " + json.dumps({"type": "response.completed", "response": response})
              + "\n\n").encode(), "text/event-stream"),
        ]
        normalized = [extract_usage(body, mime) for body, mime in bodies]
        self.assertEqual(normalized[0], normalized[1])
        for provider in ("openai", "openai-chatgpt"):
            with self.subTest(provider=provider):
                pricing = pricing_for_request(provider, MODEL)
                for usage in normalized:
                    self.assertAlmostEqual(request_usd(usage, pricing), BASE_COST)

    def test_long_context_prices_the_whole_request_after_the_boundary(self):
        for provider in ("openai", "openai-chatgpt"):
            pricing = pricing_for_request(provider, MODEL)
            for inputs, tier, expected in (
                (272000, "base", 0.272385),
                (272001, "long_context", 0.544522),
            ):
                with self.subTest(provider=provider, inputs=inputs):
                    usage = {
                        "input_tokens": inputs, "cached_input_tokens": 200,
                        "cache_write_input_tokens": 300, "output_tokens": 100,
                        "reasoning_tokens": 75,
                    }
                    self.assertEqual(request_pricing_rates(usage, pricing)[1], tier)
                    self.assertAlmostEqual(request_usd(usage, pricing), expected)


class TerraGatewayTests(unittest.IsolatedAsyncioTestCase):
    model = MODEL
    base_cost = BASE_COST

    async def test_api_and_chatgpt_tool_history_and_accounting(self):
        for provider, route, host in (
            ("openai", "openai", "api.openai.com"),
            ("openai-chatgpt", "chatgpt", "chatgpt.com"),
        ):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
                "TESTBED_USAGE_DIR": temp,
                "DUNGENESS_ALLOWED_MODELS": json.dumps([[provider, self.model]]),
                "DUNGENESS_CHATGPT_AUTH_FILE": str(Path(temp) / "auth.json"),
                "OPENAI_API_KEY": "private-api-fixture",
                "MAX_MODEL_REQUESTS": "20", "MAX_MODEL_TOKENS": "100000",
                "MAX_MODEL_USD": "5",
            }):
                auth = Path(temp) / "auth.json"
                auth.write_text(json.dumps({"tokens": {
                    "access_token": "private-subscription-fixture", "account_id": "fixture-account",
                }}))
                auth.chmod(0o600)
                runtime = Gateway()
                await runtime.client.aclose()
                history = [
                    {"role": "user", "content": "Continue the evaluation."},
                    {"type": "reasoning", "id": "rs_fixture", "summary": [],
                     "encrypted_content": "opaque-reasoning-fixture"},
                    {"type": "function_call", "call_id": "call_fixture",
                     "name": "evaluate", "arguments": "{}"},
                    {"type": "function_call_output", "call_id": "call_fixture", "output": "42"},
                ]
                calls = []

                def upstream(request):
                    calls.append(request)
                    self.assertEqual(request.url.host, host)
                    self.assertTrue(request.url.path.endswith("/responses"))
                    token = ("private-api-fixture" if provider == "openai"
                             else "private-subscription-fixture")
                    self.assertEqual(request.headers["authorization"], f"Bearer {token}")
                    body = json.loads(request.content)
                    self.assertEqual(body["model"], self.model)
                    self.assertEqual(body["input"], history)
                    self.assertEqual(body["reasoning"], {"effort": "high"})
                    result = {"model": self.model, "usage": RAW_USAGE, "output": []}
                    if body.get("stream"):
                        return httpx.Response(200, content=(
                            "data: " + json.dumps({"type": "response.completed", "response": result})
                            + "\n\n").encode(), headers={"content-type": "text/event-stream"})
                    return httpx.Response(200, json=result)

                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                try:
                    with patch.object(gateway, "gateway", runtime):
                        async with httpx.AsyncClient(
                            transport=httpx.ASGITransport(app=gateway.app), base_url="http://gateway",
                        ) as client:
                            if provider == "openai":
                                catalog = await client.get(f"/model/{route}/v1/models")
                                self.assertEqual(catalog.status_code, 200, catalog.text)
                                self.assertEqual([item["id"] for item in catalog.json()["data"]], [self.model])
                                self.assertEqual(calls, [])
                            payload = {
                                "model": self.model, "input": history,
                                "reasoning": {"effort": "high"},
                                "tools": [{"type": "function", "name": "evaluate",
                                           "parameters": {"type": "object", "properties": {}}}],
                            }
                            for stream in (False, True):
                                reply = await client.post(f"/model/{route}/v1/responses",
                                    headers={"authorization": "Bearer testbed"},
                                    json={**payload, "stream": stream})
                                self.assertEqual(reply.status_code, 200, reply.text)
                            # A priced model must still be explicitly assigned to this run.
                            rejected = await client.post(f"/model/{route}/v1/responses",
                                json={**payload, "model": "gpt-6-astra"})
                            self.assertEqual(rejected.status_code, 400)
                    self.assertEqual(len(calls), 2)
                    contents = (Path(temp) / "events.jsonl").read_text()
                    receipts = [e["data"] for e in map(json.loads, contents.splitlines())
                                if e["kind"] == "model.accounting"]
                    self.assertEqual(len(receipts), 2)
                    for receipt in receipts:
                        self.assertEqual(receipt["provider"], provider)
                        self.assertEqual(receipt["model"], self.model)
                        self.assertEqual(receipt["accounting_method"], "gateway")
                        self.assertEqual(receipt["pricing_tier"], "base")
                        self.assertAlmostEqual(receipt["normalized_usd"], self.base_cost)
                        self.assertIsNone(receipt["billed_usd"])
                    for secret in ("private-api-fixture", "private-subscription-fixture"):
                        self.assertNotIn(secret, contents)
                finally:
                    await runtime.client.aclose()


class Terra56GatewayTests(TerraGatewayTests):
    model = "gpt-5.6-terra"
    base_cost = 0.00299


class Terra56PricingTests(unittest.TestCase):
    def test_versioned_prices_and_long_context_with_cache_writes(self):
        for provider in ("openai", "openai-chatgpt"):
            prices = pricing_for_request(provider, "gpt-5.6-terra")
            for inputs, expected in ((1000, 0.00299), (272000, 0.54499), (272001, 1.089384)):
                with self.subTest(provider=provider, inputs=inputs):
                    usage = {"input_tokens": inputs, "cached_input_tokens": 200,
                             "cache_write_input_tokens": 300, "output_tokens": 100}
                    self.assertAlmostEqual(request_usd(usage, prices), expected)
            self.assertNotEqual(prices, pricing_for_request(provider, "gpt-6.1-terra"))


class CompleteGptCatalogTests(TerraGatewayTests):
    async def test_api_and_chatgpt_tool_history_and_accounting(self):
        for model, cost in (("gpt-6.2-sol", .00277), ("gpt-6.2-astra", .01108),
                            ("gpt-6.1-sol", .00277), ("gpt-6-luna", .00014),
                            ("gpt-5.6-luna", .000299)):
            with self.subTest(model=model):
                self.model, self.base_cost = model, cost
                await super().test_api_and_chatgpt_tool_history_and_accounting()

    def test_supported_retention_and_exact_catalog_identity(self):
        from gateway_request_policy import validate_model_request
        models = ("gpt-6.2-sol", "gpt-6.2-astra", "gpt-6.1-sol", "gpt-6.1-terra",
                  "gpt-6-astra", "gpt-6-sol", "gpt-6-luna",
                  "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna")
        for model in models:
            for provider in ("openai", "openai-chatgpt"):
                self.assertEqual(pricing_for_request(provider, model)["upstream_id"], "openai/" + model)
        for model in ("gpt-6.2-sol", "gpt-6.2-astra", "gpt-6.1-sol", "gpt-6.1-terra",
                      "gpt-6-luna", "gpt-5.6-terra", "gpt-5.6-luna"):
            with self.assertRaisesRegex(ValueError, "cache retention"):
                validate_model_request("openai", "responses", {
                    "model": model, "input": "fixture", "prompt_cache_retention": "12h"})
