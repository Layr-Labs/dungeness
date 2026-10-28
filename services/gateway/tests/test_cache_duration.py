"""Keep native cache TTL accounting distinct through streams and budget math."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx

import test_gateway  # Initialize the synthetic gateway environment.
from gateway_models import extract_anthropic_usage
from gateway_pricing import request_usd, request_budget_tokens, validate_pricing_rates
import gateway
import gateway_pricing
from gateway_runtime import Gateway

RATES = {"input_per_mtok": 4, "output_per_mtok": 20, "cached_read_per_mtok": .2,
         "cache_write_per_mtok": 5, "cache_write_1h_per_mtok": 8}
RAW = {"input_tokens": 500, "output_tokens": 100, "cache_read_input_tokens": 200,
       "cache_creation_input_tokens": 300,
       "cache_creation": {"ephemeral_5m_input_tokens": 200, "ephemeral_1h_input_tokens": 100}}


class CacheDurationTests(unittest.TestCase):
    def test_json_and_stream_have_identical_mixed_duration_cost(self):
        body = json.dumps({"usage": RAW}).encode()
        stream = ("data: " + json.dumps({"type": "message_start", "message": {"usage": {**RAW, "output_tokens": 0}}})
                  + "\n\ndata: " + json.dumps({"type": "message_delta", "usage": {"output_tokens": 100}}) + "\n\n").encode()
        values = [extract_anthropic_usage(body, "application/json"), extract_anthropic_usage(stream, "text/event-stream")]
        self.assertEqual(values[0], values[1])
        for usage in values:
            self.assertEqual(usage["input_tokens"], 1000)
            self.assertEqual(usage["cache_write_1h_input_tokens"], 100)
            self.assertAlmostEqual(request_usd(usage, RATES), .00584)
            self.assertEqual(request_budget_tokens(usage, RATES), 1060)

    def test_missing_duration_is_not_assumed_to_be_cheaper(self):
        raw = {k: v for k, v in RAW.items() if k != "cache_creation"}
        usage = extract_anthropic_usage(json.dumps({"usage": raw}).encode(), "application/json")
        with self.assertRaisesRegex(ValueError, "Missing cache-duration"):
            request_usd(usage, RATES)
        legacy = {k: v for k, v in RATES.items() if k != "cache_write_1h_per_mtok"}
        self.assertAlmostEqual(request_usd(usage, legacy), .00554)
        with self.assertRaisesRegex(ValueError, "Unpriced"):
            request_usd({**usage, "cache_write_1h_input_tokens": 100}, legacy)
        self.assertEqual(request_usd({}, RATES), 0)

    def test_malformed_breakdown_remains_unknown(self):
        for breakdown in ({}, [], {"ephemeral_5m_input_tokens": 201, "ephemeral_1h_input_tokens": 100},
                          {"ephemeral_5m_input_tokens": 300, "ephemeral_1h_input_tokens": False}):
            with self.subTest(breakdown=breakdown):
                self.assertEqual(extract_anthropic_usage(json.dumps({"usage": {**RAW, "cache_creation": breakdown}}).encode(),
                                                        "application/json"), {})

    def test_hour_rate_must_be_finite_nonnegative_number(self):
        for value in (None, True, -1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_pricing_rates({**RATES, "cache_write_1h_per_mtok": value}, path=Path("fixture"), context="test")


class CacheDurationSettlementTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_duration_blocks_further_requests_with_unknown_usage(self):
        reference = {**RATES, "provider": "anthropic", "upstream_id": "claude-test",
                     "request_models": ["claude-test"]}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
                "TESTBED_USAGE_DIR": tmp, "DUNGENESS_ALLOWED_MODELS": '[["anthropic","claude-test"]]',
                "MAX_MODEL_REQUESTS": "20", "MAX_MODEL_TOKENS": "100000", "MAX_MODEL_USD": "3",
                "DUNGENESS_CREDENTIALS_FILE": str(Path(tmp) / "credentials.json")}), \
                patch.object(gateway_pricing, "MODEL_PRICING", [reference]):
            credential = Path(tmp) / "credentials.json"
            credential.write_text(json.dumps({"ANTHROPIC_API_KEY": "synthetic-test-value"})); credential.chmod(0o600)
            runtime = Gateway(); await runtime.client.aclose(); calls = []
            def upstream(request):
                calls.append(request)
                return httpx.Response(200, json={"type": "message", "usage": {
                    k: v for k, v in RAW.items() if k != "cache_creation"}})
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app), base_url="http://gateway") as client:
                        payload = {"model": "claude-test", "max_tokens": 20, "messages": [{"role": "user", "content": "fixture"}]}
                        response = await client.post("/model/anthropic/v1/messages", json=payload)
                        self.assertEqual(response.status_code, 200, response.text)
                        self.assertEqual((await client.post("/model/anthropic/v1/messages", json=payload)).status_code, 429)
                self.assertEqual(len(calls), 1)
                receipts = [e["data"] for e in map(json.loads, (Path(tmp) / "events.jsonl").read_text().splitlines())
                            if e["kind"] == "model.accounting"]
                self.assertEqual(receipts[0]["accounting_method"], "unavailable")
                self.assertEqual(receipts[0]["accounting_basis"], "invalid_or_missing_cache_duration")
            finally:
                await runtime.client.aclose()
