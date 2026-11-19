"""Google API wire/accounting contract with synthetic keys and no network."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
from gateway_models import extract_google_usage
from gateway_request_policy import validate_model_request
from gateway_runtime import Gateway
from provider_profiles import PROFILES


MODEL = "gemini-4-carbon"
SIGNATURE = {"google": {"thought_signature": "synthetic-signature+/=="}}
CALL = {"id": "call-1", "type": "function",
        "function": {"name": "calculate", "arguments": '{"x": 2}'},
        "extra_content": SIGNATURE}
TOOLS = [{"type": "function", "function": {
    "name": "calculate", "parameters": {"type": "object", "properties": {"x": {"type": "number"}}}}}]
USAGE = {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 140,
         "prompt_tokens_details": {"cached_tokens": 20},
         "completion_tokens_details": {"reasoning_tokens": 30}}


def request(model=MODEL):
    return {"model": model, "messages": [
        {"role": "system", "content": "You are Codex; preserve this exact instruction."},
        {"role": "user", "content": "Calculate 2 + 2"}],
        "tools": copy.deepcopy(TOOLS), "reasoning_effort": "high", "max_tokens": 256}


class GoogleUsageTests(unittest.TestCase):
    def test_thinking_counts_in_both_compatibility_formats(self):
        expected = {"input_tokens": 100, "cached_input_tokens": 20,
                    "cache_write_input_tokens": 0, "output_tokens": 40,
                    "reasoning_tokens": 30, "total_tokens": 140}
        for raw in (USAGE, {**USAGE, "completion_tokens": 40},
                    {key: value for key, value in USAGE.items() if key != "completion_tokens_details"}):
            with self.subTest(raw=raw):
                wire = json.dumps({"usage": raw}).encode()
                self.assertEqual(extract_google_usage(wire, "application/json"), expected)
                sse = b"data: " + wire + b"\n\ndata: " + wire + b"\n\ndata: [DONE]\n\n"
                self.assertEqual(extract_google_usage(sse, "text/event-stream"), expected)

    def test_invalid_or_incomplete_usage_never_becomes_free(self):
        cases = [{}, None, {"prompt_tokens": 100},
                 {**USAGE, "total_tokens": 105},
                 {**USAGE, "prompt_tokens": True},
                 {**USAGE, "completion_tokens": -1},
                 {**USAGE, "total_tokens": "140"},
                 {**USAGE, "prompt_tokens_details": {"cached_tokens": 101}},
                 {**USAGE, "prompt_tokens_details": None},
                 {**USAGE, "completion_tokens_details": {"reasoning_tokens": 25}},
                 {**USAGE, "completion_tokens_details": {"reasoning_tokens": 30, "audio_tokens": 1}}]
        for raw in cases:
            with self.subTest(raw=raw):
                self.assertEqual(extract_google_usage(json.dumps({"usage": raw}).encode(),
                                                     "application/json"), {})
        prefix = b"data: " + json.dumps({"usage": USAGE}).encode() + b"\n\n"
        self.assertEqual(extract_google_usage(prefix, "text/event-stream"), {})
        for ending in (b'data: {broken}\n\ndata: [DONE]\n\n',
                       b'data: {"choices":[]}\n\ndata: [DONE]\n\n'):
            self.assertEqual(extract_google_usage(prefix + ending, "text/event-stream"), {})
        # Never fall back to earlier valid usage after a malformed final receipt.
        self.assertEqual(extract_google_usage(prefix + b'data: {"usage":{}}\n\ndata: [DONE]\n\n',
                                             "text/event-stream"), {})

    def test_omitted_cache_detail_receives_no_discount(self):
        raw = {key: value for key, value in USAGE.items() if key != "prompt_tokens_details"}
        self.assertEqual(extract_google_usage(json.dumps({"usage": raw}).encode(), "application/json")[
            "cached_input_tokens"], 0)


class GoogleHistoryTests(unittest.TestCase):
    def test_assistant_signatures_round_trip_without_mutation(self):
        payload = request()
        payload["messages"] += [
            {"role": "assistant", "content": None, "tool_calls": [copy.deepcopy(CALL)]},
            {"role": "tool", "tool_call_id": "call-1", "content": "4"},
            {"role": "assistant", "content": "Four", "extra_content": copy.deepcopy(SIGNATURE)}]
        before = copy.deepcopy(payload)
        validate_model_request("google-api", "chat/completions", payload)
        self.assertEqual(payload, before)
        for provider in ("openai", "openrouter", "grok-subscription"):
            with self.subTest(provider=provider), self.assertRaises(ValueError):
                validate_model_request(provider, "chat/completions", payload)

    def test_opaque_signature_requires_exclusive_budget_reservation(self):
        from gateway_reservations import validate_generation
        from gateway_pricing import pricing_for_request
        payload = request()
        payload["messages"].append({"role": "assistant", "content": None, "tool_calls": [CALL]})
        result, tokens, usd = validate_generation("google-api", "chat/completions", payload,
                                                 pricing_for_request("google-api", MODEL))
        self.assertEqual(result, payload)
        self.assertIsNone(tokens)
        self.assertIsNone(usd)

    def test_signature_extension_cannot_carry_provider_controls(self):
        for metadata in (None, {}, {"google": {}}, {"google": {"thought_signature": 42}},
                         {"google": {"thought_signature": "x", "tools": [{"google_search": {}}]}},
                         {"google": {"thought_signature": "x"}, "base_url": "https://example.invalid"},
                         {"google": {"thought_signature": "x" * 131073}}):
            for on_call in (True, False):
                payload = request()
                assistant = {"role": "assistant", "content": None}
                if on_call:
                    assistant["tool_calls"] = [{**CALL, "extra_content": metadata}]
                else:
                    assistant["extra_content"] = metadata
                payload["messages"].append(assistant)
                with self.subTest(on_call=on_call, metadata_type=type(metadata)), self.assertRaises(ValueError):
                    validate_model_request("google-api", "chat/completions", payload)
        for key in ("extra_body", "extra_content"):
            payload = {**request(), key: SIGNATURE}
            with self.assertRaises(ValueError):
                validate_model_request("google-api", "chat/completions", payload)
        payload = request()
        payload["messages"][0]["extra_content"] = SIGNATURE
        with self.assertRaises(ValueError):
            validate_model_request("google-api", "chat/completions", payload)


class GoogleGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_installed_models_auth_tools_streaming_and_accounting(self):
        for model in PROFILES["google-api"]["models"]:
            with self.subTest(model=model), tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
                "TESTBED_USAGE_DIR": temp, "DUNGENESS_ALLOWED_MODELS": json.dumps([["google-api", model]]),
                "MAX_MODEL_REQUESTS": "10", "MAX_MODEL_TOKENS": "1000000", "MAX_MODEL_USD": "10",
                "DUNGENESS_CREDENTIALS_FILE": str(Path(temp) / "credentials.json"),
            }):
                credential = Path(temp) / "credentials.json"
                credential.write_text(json.dumps({"GEMINI_API_KEY": "private-google-api-key"}))
                credential.chmod(0o600)
                runtime = Gateway()
                await runtime.client.aclose()
                calls = []
                def upstream(req):
                    payload = json.loads(req.content)
                    calls.append(payload)
                    self.assertEqual(str(req.url),
                                     "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions")
                    self.assertEqual(req.headers["authorization"], "Bearer private-google-api-key")
                    self.assertNotIn("x-goog-api-key", req.headers)
                    self.assertEqual(payload["model"], model)
                    self.assertEqual(payload["messages"][:2], request(model)["messages"])
                    self.assertEqual(payload["tools"], TOOLS)
                    self.assertEqual(payload["reasoning_effort"], "high")
                    if len(calls) == 1:
                        return httpx.Response(200, json={
                            "model": model, "choices": [{"index": 0, "finish_reason": "tool_calls",
                                "message": {"role": "assistant", "content": None, "tool_calls": [CALL]}}],
                            "usage": USAGE})
                    self.assertEqual(payload["messages"][2]["tool_calls"][0], CALL)
                    self.assertTrue(payload["stream_options"]["include_usage"])
                    wire = ("data: " + json.dumps({"model": model, "choices": [
                        {"index": 0, "delta": {"content": "4"}, "finish_reason": "stop"}]}) +
                        "\n\ndata: " + json.dumps({"choices": [], "usage": USAGE}) + "\n\ndata: [DONE]\n\n").encode()
                    class Stream(httpx.AsyncByteStream):
                        async def __aiter__(self):
                            yield wire[:17]
                            yield wire[17:]
                    return httpx.Response(200, stream=Stream(), headers={"content-type": "text/event-stream"})
                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                try:
                    with patch.object(gateway, "gateway", runtime):
                        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                     base_url="http://gateway") as client:
                            route = "/model/google-api/v1/chat/completions"
                            payload = request(model)
                            first = await client.post(route, json=payload, headers={"authorization": "Bearer placeholder"})
                            self.assertEqual(first.status_code, 200, first.text)
                            payload["messages"] += [first.json()["choices"][0]["message"],
                                                    {"role": "tool", "tool_call_id": "call-1", "content": "4"}]
                            streamed = await client.post(route, json={**payload, "stream": True})
                            self.assertEqual(streamed.status_code, 200, streamed.text)
                            self.assertIn("data: [DONE]", streamed.text)
                            for change in ({"model": "gemini-unmapped"},
                                           {"tools": [{"type": "web_search"}]},
                                           {"extra_body": {"google": {"tools": [{"google_search": {}}]}}}):
                                blocked = await client.post(route, json={**payload, **change})
                                self.assertEqual(blocked.status_code, 400, blocked.text)
                            # No credential fallback after the configured private file disappears.
                            credential.unlink()
                            denied = await client.post(route, json=payload)
                            self.assertEqual(denied.status_code, 400)
                    self.assertEqual(len(calls), 2)
                    events = Path(temp, "events.jsonl").read_text()
                    self.assertNotIn("private-google-api-key", events)
                    receipts = [e["data"] for e in map(json.loads, events.splitlines())
                                if e["kind"] == "model.accounting"]
                    self.assertEqual(len(receipts), 2)
                    self.assertFalse(runtime.ledger.model_accounting_incomplete)
                    from gateway_pricing import pricing_for_request
                    price = pricing_for_request("google-api", model)
                    expected = round((80 * price["input_per_mtok"] + 20 * price["cached_read_per_mtok"]
                                      + 40 * price["output_per_mtok"]) / 1e6, 6)
                    for receipt in receipts:
                        self.assertAlmostEqual(receipt["normalized_usd"], expected)
                        self.assertIsNone(receipt["billed_usd"])
                finally:
                    await runtime.client.aclose()

    async def test_missing_usage_blocks_follow_up_admission(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp, "GEMINI_API_KEY": "synthetic-google-key",
            "DUNGENESS_ALLOWED_MODELS": json.dumps([["google-api", MODEL]]),
        }):
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []
            def upstream(req):
                calls.append(req)
                return httpx.Response(200, json={"choices": [], "usage": {"prompt_tokens": 100}})
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        route = "/model/google-api/v1/chat/completions"
                        first = await client.post(route, json=request())
                        self.assertEqual(first.status_code, 200, first.text)
                        second = await client.post(route, json=request())
                        self.assertEqual(second.status_code, 429, second.text)
                self.assertEqual(len(calls), 1)
                self.assertTrue(runtime.ledger.model_accounting_incomplete)
            finally:
                await runtime.client.aclose()
