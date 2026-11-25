"""Real gateway HTTP boundary with synthetic Gemini API responses."""
import copy
from contextlib import asynccontextmanager
import json
import unittest
from unittest.mock import patch

import httpx
from test_history_roundtrip import Fragments
from test_request_policy import harness, request_body, route
from access_config import validate_access_routes
from access_selection import resolve_endpoint, resolve_routes
from gateway_google import normalize_usage, ResponseTranslator
from gateway_models import MODEL_PROVIDERS
from gateway_request_policy import validate_model_request


PROVIDER, OPERATION = "example-session", "chat/completions"
COUNTS = {"promptTokenCount": 100, "cachedContentTokenCount": 40,
          "candidatesTokenCount": 10, "thoughtsTokenCount": 20, "totalTokenCount": 130}
PARTS = [
    {"text": "Consider a candidate.", "thought": True, "thoughtSignature": "signed-thought=="},
    {"text": "Evaluate it.", "thoughtSignature": "signed-text=="},
    {"functionCall": {"name": "evaluate", "args": {"candidate": "local"}}, "thoughtSignature": "signed-call-one=="},
    {"functionCall": {"id": "native-two", "name": "read_result", "args": {}}},
    {"text": "", "thoughtSignature": "signed-empty-text=="},
]
RESULT = {"candidates": [{"index": 0, "content": {"role": "model", "parts": PARTS},
                          "finishReason": "STOP"}], "usageMetadata": COUNTS}


@asynccontextmanager
async def google_harness():
    async with harness() as (client, runtime, calls):
        config = {**MODEL_PROVIDERS[PROVIDER], "transport": "google-generate-content",
                  "authentication_method": "bearer", "upstream_default": "https://google.invalid/v1beta"}
        selection = {"endpoint": config["upstream_default"], "authentication": "bearer"}
        provider = resolve_endpoint({PROVIDER: config}, selection)
        config = resolve_routes({PROVIDER: config}, {provider: selection})[provider]
        with patch.dict(MODEL_PROVIDERS, {PROVIDER: config}):
            yield client, runtime, calls, config


def payload(**extra):
    return {**request_body(PROVIDER, OPERATION), "reasoning_effort": "high",
            "max_completion_tokens": 4096, "messages": [
                {"role": "system", "content": "Work locally."},
                {"role": "user", "content": "Evaluate a candidate."}],
            "tools": [{"type": "function", "function": {"name": name, "parameters": {"type": "object"}}}
                      for name in ("evaluate", "read_result")], **extra}


def accounting(runtime):
    return [item["data"] for item in map(json.loads, (runtime.ledger.directory / "events.jsonl").read_text().splitlines())
            if item["kind"] == "model.accounting"]


def stream_events():
    events = []
    for part in PARTS:
        events.append({"candidates": [{"content": {"role": "model", "parts": [part]}}]})
    events += [{"candidates": [{"finishReason": "STOP"}]}, {"usageMetadata": COUNTS},
               {"usageMetadata": COUNTS}]  # repeated cumulative receipt must not double charge
    return "".join("data: " + json.dumps(event) + "\r\n\r\n" for event in events).encode()


def collect_message(response):
    message = {"role": "assistant", "content": ""}
    for line in response.text.splitlines():
        if not line.startswith("data: ") or line == "data: [DONE]":
            continue
        event = json.loads(line[6:])
        for choice in event["choices"]:
            delta = choice["delta"]
            for key in ("content", "reasoning_content"):
                if key in delta:
                    message[key] = message.get(key, "") + delta[key]
            if "extra_content" in delta:
                message.setdefault("extra_content", {"google": {"parts": []}})["google"]["parts"].extend(
                    delta["extra_content"]["google"]["parts"])
            for call in delta.get("tool_calls", []):
                message.setdefault("tool_calls", []).append({k: v for k, v in call.items() if k != "index"})
    return message


class GoogleTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_json_and_fragmented_stream_roundtrip_and_meter_thoughts_once(self):
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                async with google_harness() as (client, runtime, _, config):
                    requests = []
                    def upstream(request):
                        requests.append(request)
                        if streaming:
                            return httpx.Response(200, headers={"content-type": "text/event-stream"},
                                                  stream=Fragments(stream_events()))
                        return httpx.Response(200, json=RESULT)
                    await runtime.client.aclose()
                    runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                    response = await client.post(route(PROVIDER, OPERATION), json=payload(stream=streaming),
                                                 headers={"authorization": "Bearer spoofed"})
                    self.assertEqual(response.status_code, 200, response.text)
                    message = collect_message(response) if streaming else response.json()["choices"][0]["message"]
                    self.assertEqual(message["extra_content"]["google"]["parts"], PARTS)
                    self.assertEqual(message["reasoning_content"], "Consider a candidate.")
                    validate_model_request(PROVIDER, OPERATION, payload(messages=[message]))
                    followup = payload(stream=streaming)
                    followup["messages"] += [message, *[
                        {"role": "tool", "tool_call_id": call["id"], "content": "valid candidate: 42"}
                        for call in message["tool_calls"]]]
                    response = await client.post(route(PROVIDER, OPERATION), json=followup)
                    self.assertEqual(response.status_code, 200, response.text)
                    for req in requests:
                        method = "streamGenerateContent" if streaming else "generateContent"
                        expected = config["upstream_default"] + "/models/example-model:" + method
                        self.assertEqual(str(req.url), expected + ("?alt=sse" if streaming else ""))
                        self.assertNotIn("spoofed", dict(req.headers).values())
                        self.assertEqual(req.headers["authorization"], "Bearer unused-session")
                        self.assertNotIn("unused-session", req.content.decode())
                        body = json.loads(req.content)
                        self.assertEqual(body["generationConfig"]["thinkingConfig"], {"thinkingLevel": "HIGH"})
                        self.assertEqual(body["generationConfig"]["maxOutputTokens"], 4096)
                        self.assertEqual(body["tools"][0]["functionDeclarations"][0]["name"], "evaluate")
                    body = json.loads(requests[1].content)
                    self.assertEqual(body["contents"][1], {"role": "model", "parts": PARTS})
                    self.assertEqual(body["contents"][2]["parts"][0]["functionResponse"]["name"], "evaluate")
                    self.assertNotIn("id", body["contents"][2]["parts"][0]["functionResponse"])
                    self.assertEqual(body["contents"][2]["parts"][1]["functionResponse"]["id"], "native-two")
                    receipts = accounting(runtime)
                    self.assertEqual(len(receipts), 2)
                    for receipt in receipts:
                        self.assertEqual(receipt["input_tokens"], 100)
                        self.assertEqual(receipt["cached_input_tokens"], 40)
                        self.assertEqual(receipt["output_tokens"], 30)
                        self.assertEqual(receipt["reasoning_tokens"], 20)
                        self.assertAlmostEqual(receipt["normalized_usd"], .00032)
                        self.assertIsNone(receipt["billed_usd"])
                    events = (runtime.ledger.directory / "events.jsonl").read_text()
                    self.assertNotIn("unused-session", events)

    async def test_unmapped_controls_and_hidden_server_tools_rejected_before_traffic(self):
        async with google_harness() as (client, runtime, calls, _):
            before = copy.deepcopy(runtime.ledger.counts)
            for extra in (
                {"logprobs": True}, {"n": 2}, {"parallel_tool_calls": False},
                {"model": "../account"}, {"temperature": "high"},
                {"max_completion_tokens": 2**4096},
                {"tools": [{"googleSearch": {}}]},
                {"extra_body": {"google": {"cached_content": "remote"}}},
                {"messages": [{"role": "assistant", "content": "", "extra_content": {"google": {"parts": [
                    {"functionCall": {"name": "evaluate", "args": {}}, "executableCode": {"code": "hidden"}}]}}}]},
                {"tools": [{"type": "function", "function": {"name": "evaluate", "strict": True}}]},
            ):
                with self.subTest(extra=extra):
                    response = await client.post(route(PROVIDER, OPERATION), json=payload(**extra))
                    self.assertEqual(response.status_code, 400, response.text)
            self.assertEqual(calls, [])
            self.assertEqual(runtime.ledger.counts, before)

    async def test_missing_or_invalid_usage_stops_further_model_admission(self):
        for counts in (None, {}, {**COUNTS, "totalTokenCount": 110}, {**COUNTS, "thoughtsTokenCount": "20"}):
            with self.subTest(counts=counts):
                async with google_harness() as (client, runtime, _, config):
                    requests = []
                    result = copy.deepcopy(RESULT)
                    result.pop("usageMetadata")
                    if counts is not None:
                        result["usageMetadata"] = counts
                    def upstream(request):
                        requests.append(request)
                        return httpx.Response(200, json=result)
                    await runtime.client.aclose()
                    runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                    response = await client.post(route(PROVIDER, OPERATION), json=payload())
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertNotIn("usage", response.json())
                    self.assertTrue(runtime.ledger.model_accounting_incomplete)
                    receipt = accounting(runtime)[0]
                    # Existing ledger totals sum known usage only; unavailable
                    # accounting is authoritative, not the zero added to totals.
                    self.assertNotIn("input_tokens", receipt)
                    self.assertEqual(receipt["accounting_basis"], "unavailable")
                    response = await client.post(route(PROVIDER, OPERATION), json=payload())
                    self.assertGreaterEqual(response.status_code, 400)
                    self.assertEqual(len(requests), 1)

    async def test_interrupted_stream_never_emits_completion_or_free_usage(self):
        async with google_harness() as (client, runtime, _, config):
            body = ("data: " + json.dumps({
                "candidates": [{"content": {"parts": [{"text": "partial"}]}}],
                "usageMetadata": COUNTS}) + "\n\n").encode()
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=Fragments(body, True))))
            response = await client.post(route(PROVIDER, OPERATION), json=payload(stream=True))
            self.assertEqual(response.status_code, 200)
            self.assertIn("partial", response.text)
            self.assertNotIn("[DONE]", response.text)
            self.assertNotIn("finish_reason", response.text)
            self.assertTrue(runtime.ledger.model_accounting_incomplete)
            self.assertEqual(accounting(runtime)[0]["accounting_basis"], "unavailable")

    async def test_final_usage_is_retained_when_connection_breaks_after_receipt(self):
        async with google_harness() as (client, runtime, _, config):
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=Fragments(stream_events(), True))))
            response = await client.post(route(PROVIDER, OPERATION), json=payload(stream=True))
            self.assertNotIn("[DONE]", response.text)
            self.assertNotIn("finish_reason", response.text)
            self.assertFalse(runtime.ledger.model_accounting_incomplete)
            self.assertEqual(accounting(runtime)[0]["status"], "stream_interrupted")
            self.assertEqual(accounting(runtime)[0]["output_tokens"], 30)
            self.assertAlmostEqual(accounting(runtime)[0]["normalized_usd"], .00032)

    async def test_upstream_authentication_error_is_sanitized_without_retry_or_fallback(self):
        async with google_harness() as (client, runtime, _, config):
            requests = []
            def upstream(request):
                requests.append(request)
                return httpx.Response(401, json={"error": {"message": "private account and token details"}})
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            response = await client.post(route(PROVIDER, OPERATION), json=payload())
            self.assertEqual(response.status_code, 401, response.text)
            self.assertNotIn("private account", response.text)
            self.assertEqual(len(requests), 1)
            self.assertTrue(runtime.ledger.model_accounting_incomplete)

    async def test_malformed_or_hosted_tool_responses_fail_without_exposing_raw_errors(self):
        for result in (
            b'{"private-provider-content":',
            json.dumps({"candidates": [{"content": {"parts": [
                {"executableCode": {"code": "private-provider-content"}}]}}]}).encode(),
        ):
            async with google_harness() as (client, runtime, _, config):
                await runtime.client.aclose()
                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(
                    lambda req: httpx.Response(200, content=result)))
                response = await client.post(route(PROVIDER, OPERATION), json=payload())
                self.assertEqual(response.status_code, 502, response.text)
                self.assertNotIn("private-provider-content", response.text)
                self.assertTrue(runtime.ledger.model_accounting_incomplete)

    async def test_native_response_size_limit_still_applies(self):
        async with google_harness() as (client, runtime, _, config):
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(
                lambda req: httpx.Response(200, json=RESULT)))
            with patch("gateway_google.MAX_RESPONSE_BYTES", 32):
                response = await client.post(route(PROVIDER, OPERATION), json=payload())
            self.assertEqual(response.status_code, 502, response.text)
            self.assertTrue(runtime.ledger.model_accounting_incomplete)


class GoogleUsageTests(unittest.TestCase):
    def test_counts_and_invalid_receipts(self):
        usage = normalize_usage(COUNTS)
        self.assertEqual(usage["output_tokens"], 30)
        self.assertEqual(usage["reasoning_tokens"], 20)
        self.assertEqual(normalize_usage({"promptTokenCount": 0, "totalTokenCount": 0})["output_tokens"], 0)
        for raw in (None, {}, {"totalTokenCount": 10}, {**COUNTS, "cachedContentTokenCount": 101},
                    {**COUNTS, "toolUsePromptTokenCount": 1}, {**COUNTS, "promptTokenCount": True},
                    {**COUNTS, "thoughtsTokenCount": -1}, {**COUNTS, "totalTokenCount": 2**54}):
            self.assertEqual(normalize_usage(raw), {})

    def test_earlier_usage_cannot_account_for_later_output_or_decreasing_counters(self):
        translator = ResponseTranslator("model", "request")
        translator.consume({"usageMetadata": COUNTS})
        translator.consume({"candidates": [{"content": {"parts": [{"text": "later"}]}, "finishReason": "STOP"}]})
        self.assertNotIn("usage", translator.finish())
        translator.consume({"usageMetadata": {"promptTokenCount": 1, "totalTokenCount": 1}})
        self.assertNotIn("usage", translator.finish())
        translator.consume({"usageMetadata": COUNTS})
        self.assertEqual(translator.finish()["usage"]["completion_tokens"], 30)

    def test_registry_rejects_removed_google_subscription_transport(self):
        config = {"authentication": {"sources": [{"headers": {"authorization": {"env": "GOOGLE_TOKEN", "prefix": "Bearer "}}}]},
                  "upstream_default": "https://google.invalid/v1beta", "upstream_env": "GOOGLE_UPSTREAM",
                  "routes": ["chat/completions", "models"], "auth": "gateway_secret", "billed": True,
                  "passthrough": [], "usage_parser": "openai", "transport": "google-generate-content"}
        self.assertEqual(validate_access_routes({"google-test": config})["google-test"]["transport"], "google-generate-content")
        for change in ({"transport": "google-code-assist"}, {"transport": "arbitrary"},
                       {"usage_parser": "anthropic"}, {"routes": ["responses"]}, {"project": "project-id"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_access_routes({"google-test": {**config, **change}})
