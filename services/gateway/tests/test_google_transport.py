"""Native Google HTTP/SSE forwarding, policy, and independent accounting."""
import copy
from contextlib import asynccontextmanager
import json
import os
import unittest
from unittest.mock import patch

import httpx
from test_history_roundtrip import Fragments
from test_request_policy import harness, route
from access_config import validate_access_routes
from access_selection import resolve_endpoint, resolve_routes
from gateway_google import normalize_usage, NativeReceipt, validate_request, extract_usage
from gateway_models import MODEL_PROVIDERS, gateway_provider_config
from gateway_reservations import bounded_request

PROVIDER = "example-session"
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
                  "usage_parser": "google", "routes": {"generateContent", "streamGenerateContent", "models"},
                  "authentication_method": "bearer", "upstream_default": "https://google.invalid/v1beta"}
        selection = {"endpoint": config["upstream_default"], "authentication": "bearer"}
        provider = resolve_endpoint({PROVIDER: config}, selection)
        config = gateway_provider_config(resolve_routes({PROVIDER: config}, {provider: selection})[provider])
        with patch.dict(MODEL_PROVIDERS, {PROVIDER: config}):
            yield client, runtime, calls, config


def payload(**extra):
    return {"contents": [{"role": "user", "parts": [{"text": "Evaluate a candidate."}]}],
            "systemInstruction": {"parts": [{"text": "Work locally."}]},
            "generationConfig": {"maxOutputTokens": 4096, "thinkingConfig": {"thinkingLevel": "HIGH"}},
            "tools": [{"functionDeclarations": [{"name": name, "parameters": {"type": "OBJECT"}}
                                                for name in ("evaluate", "read_result")]}], **extra}


def accounting(runtime):
    return [item["data"] for item in map(json.loads, (runtime.ledger.directory / "events.jsonl").read_text().splitlines())
            if item["kind"] == "model.accounting"]


def stream_events():
    events = [{"candidates": [{"content": {"role": "model", "parts": [part]}}]} for part in PARTS]
    events += [{"candidates": [{"finishReason": "STOP"}]}, {"usageMetadata": COUNTS}, {"usageMetadata": COUNTS}]
    return "".join("data: " + json.dumps(event) + "\r\n\r\n" for event in events).encode()


class GoogleTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_native_json_and_fragmented_sse_are_unchanged_with_tool_roundtrip(self):
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                async with google_harness() as (client, runtime, _, config):
                    requests = []
                    raw = stream_events() if streaming else json.dumps(RESULT, indent=2).encode()
                    def upstream(request):
                        requests.append(request)
                        return httpx.Response(200, headers={"content-type": "text/event-stream" if streaming else "application/json"},
                                              stream=Fragments(raw))
                    await runtime.client.aclose()
                    runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                    operation = "streamGenerateContent" if streaming else "generateContent"
                    path = route(PROVIDER, operation) + ("?alt=sse" if streaming else "")
                    body = payload()
                    for turn in range(2):
                        response = await client.post(path, json=body, headers={"authorization": "Bearer spoofed", "x-goog-api-key": "spoofed"})
                        self.assertEqual(response.status_code, 200, response.text)
                        self.assertEqual(response.content, raw)
                        request = requests[-1]
                        self.assertEqual(json.loads(request.content), body)
                        self.assertEqual(str(request.url), config["upstream_default"] + "/models/example-model:" + operation + ("?alt=sse" if streaming else ""))
                        self.assertEqual(request.headers["authorization"], "Bearer unused-session")
                        self.assertNotIn("spoofed", str(request.headers))
                        body = payload(contents=body["contents"] + [
                            {"role": "model", "parts": PARTS},
                            {"role": "user", "parts": [
                                {"functionResponse": {"name": "evaluate", "response": {"score": 42}}},
                                {"functionResponse": {"id": "native-two", "name": "read_result", "response": {"valid": True}}}]}])
                    self.assertEqual(len(requests), 2)
                    for receipt in accounting(runtime):
                        self.assertEqual(receipt["input_tokens"], 100)
                        self.assertEqual(receipt["cached_input_tokens"], 40)
                        self.assertEqual(receipt["output_tokens"], 30)
                        self.assertEqual(receipt["reasoning_tokens"], 20)
                        self.assertAlmostEqual(receipt["normalized_usd"], .00032)
                    self.assertNotIn("unused-session", (runtime.ledger.directory / "events.jsonl").read_text())

    async def test_hosted_tools_remote_state_and_invalid_fields_never_reach_provider(self):
        async with google_harness() as (client, runtime, calls, _):
            before = copy.deepcopy(runtime.ledger.counts)
            for extra in (
                {"model": "another"}, {"messages": []}, {"contents": []},
                {"generationConfig": {"candidateCount": 2}},
                {"generationConfig": {"maxOutputTokens": 2**4096}},
                {"generationConfig": {"temperature": "high"}},
                {"generationConfig": {"responseModalities": ["IMAGE"]}},
                {"tools": [{"googleSearch": {}}]}, {"tools": [{"codeExecution": {}}]},
                {"tools": [{"urlContext": {}}]}, {"tools": [{"googleMaps": {}}]},
                {"cachedContent": "cachedContents/remote"}, {"project": "unapproved"},
                {"contents": [{"parts": [{"fileData": {"fileUri": "https://unapproved.invalid"}}]}]},
                {"contents": [{"parts": [{"inlineData": {"data": "abc"}}]}]},
                {"contents": [{"parts": [{"executableCode": {"code": "print(1)"}}]}]},
            ):
                response = await client.post(route(PROVIDER, "generateContent"), json=payload(**extra))
                self.assertEqual(response.status_code, 400, (extra, response.text))
            for path in (route(PROVIDER, "chat/completions"),
                         f"/model/{PROVIDER}/v1beta/models/a%2Fb:generateContent",
                         f"/model/{PROVIDER}/v1beta/projects/another/models/example-model:generateContent"):
                response = await client.post(path, json=payload())
                self.assertEqual(response.status_code, 404, response.text)
            for query in ("?key=secret", "?alt=sse&alt=sse", "?alt=json", "?anything=true"):
                response = await client.post(route(PROVIDER, "streamGenerateContent") + query, json=payload())
                self.assertEqual(response.status_code, 400, response.text)
            self.assertFalse(calls)
            self.assertEqual(runtime.ledger.counts, before)

    async def test_missing_or_invalid_usage_stops_further_model_admission(self):
        for counts in (None, {}, {**COUNTS, "totalTokenCount": 110}, {**COUNTS, "thoughtsTokenCount": "20"}):
            async with google_harness() as (client, runtime, _, _):
                result = copy.deepcopy(RESULT)
                result.pop("usageMetadata")
                if counts is not None: result["usageMetadata"] = counts
                requests = []
                def upstream(request):
                    requests.append(request)
                    return httpx.Response(200, json=result)
                await runtime.client.aclose()
                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                response = await client.post(route(PROVIDER, "generateContent"), json=payload())
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json(), result)
                self.assertTrue(runtime.ledger.model_accounting_incomplete)
                self.assertEqual(accounting(runtime)[0]["accounting_basis"], "unavailable")
                response = await client.post(route(PROVIDER, "generateContent"), json=payload())
                self.assertGreaterEqual(response.status_code, 400)
                self.assertEqual(len(requests), 1)

    async def test_interrupted_stream_accounts_only_a_final_receipt(self):
        for final in (False, True):
            async with google_harness() as (client, runtime, _, _):
                raw = stream_events() if final else ("data: " + json.dumps({"candidates": [{"content": {"parts": [{"text": "partial"}]}}],
                                                                          "usageMetadata": COUNTS}) + "\n\n").encode()
                await runtime.client.aclose()
                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(
                    200, headers={"content-type": "text/event-stream"}, stream=Fragments(raw, True))))
                response = await client.post(route(PROVIDER, "streamGenerateContent") + "?alt=sse", json=payload())
                self.assertEqual(response.status_code, 200)
                self.assertEqual(runtime.ledger.model_accounting_incomplete, not final)
                self.assertEqual(accounting(runtime)[0]["status"], "stream_interrupted")
                if final: self.assertEqual(accounting(runtime)[0]["output_tokens"], 30)
                else: self.assertNotIn("finishReason", response.text)

    async def test_upstream_error_is_sanitized_without_retry_or_fallback(self):
        async with google_harness() as (client, runtime, _, _):
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(
                401, json={"error": {"message": "private account and token details"}})))
            response = await client.post(route(PROVIDER, "generateContent"), json=payload())
            self.assertEqual(response.status_code, 401)
            self.assertNotIn("private account", response.text)

    async def test_malformed_and_hosted_tool_responses_fail(self):
        for result in (b'{"private-provider-content":', json.dumps({"candidates": [{"content": {"parts": [
                {"executableCode": {"code": "private-provider-content"}}]}, "finishReason": "STOP"}]}).encode()):
            async with google_harness() as (client, runtime, _, _):
                await runtime.client.aclose()
                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(200, content=result)))
                response = await client.post(route(PROVIDER, "generateContent"), json=payload())
                self.assertEqual(response.status_code, 502, response.text)
                self.assertNotIn("private-provider-content", response.text)
                self.assertTrue(runtime.ledger.model_accounting_incomplete)

    async def test_size_limit_applies_to_native_response(self):
        async with google_harness() as (client, runtime, _, _):
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=RESULT)))
            with patch("gateway_google.MAX_RESPONSE_BYTES", 32):
                response = await client.post(route(PROVIDER, "generateContent"), json=payload())
            self.assertEqual(response.status_code, 502)
            self.assertTrue(runtime.ledger.model_accounting_incomplete)

    async def test_native_budgets_and_model_allowlist_are_enforced(self):
        with patch.dict(os.environ, {"DUNGENESS_BOUNDED_REQUESTS": "1"}):
            async with google_harness() as (client, runtime, calls, _):
                before = copy.deepcopy(runtime.ledger.counts)
                for path, body in (
                    (route(PROVIDER, "generateContent"), payload(generationConfig={"maxOutputTokens": 65537})),
                    (f"/model/{PROVIDER}/v1beta/models/unapproved:generateContent", payload()),
                ):
                    response = await client.post(path, json=body)
                    self.assertEqual(response.status_code, 400, response.text)
                self.assertFalse(calls)
                self.assertEqual(runtime.ledger.counts, before)


class GoogleUsageTests(unittest.TestCase):
    def test_native_usage_is_independent_of_wire_format(self):
        self.assertEqual(extract_usage(json.dumps(RESULT).encode(), "application/json"), normalize_usage(COUNTS))
        self.assertEqual(extract_usage(stream_events(), "text/event-stream"), normalize_usage(COUNTS))
        self.assertEqual(extract_usage(stream_events() + b'data: {', "text/event-stream"), {})
        self.assertEqual(normalize_usage(COUNTS)["output_tokens"], 30)
        for raw in (None, {}, {"totalTokenCount": 10}, {**COUNTS, "cachedContentTokenCount": 101},
                    {**COUNTS, "toolUsePromptTokenCount": 1}, {**COUNTS, "promptTokenCount": True}):
            self.assertEqual(normalize_usage(raw), {})

    def test_earlier_usage_cannot_cover_later_output_or_decreasing_counters(self):
        receipt = NativeReceipt()
        receipt.consume({"usageMetadata": COUNTS})
        receipt.consume({"candidates": [{"content": {"parts": [{"text": "later"}]}, "finishReason": "STOP"}]})
        self.assertEqual(receipt.usage, {})
        receipt.consume({"usageMetadata": {"promptTokenCount": 1, "totalTokenCount": 1}})
        self.assertEqual(receipt.usage, {})
        receipt.consume({"usageMetadata": COUNTS})
        self.assertEqual(receipt.usage["output_tokens"], 30)

    def test_native_thinking_history_preserved_and_budgeted_conservatively(self):
        for thinking in ({"thinkingLevel": "HIGH"}, {"thinkingBudget": 1024}, {"includeThoughts": True}):
            body = payload(generationConfig={"thinkingConfig": thinking, "maxOutputTokens": 1024},
                           contents=[{"role": "model", "parts": PARTS}])
            before = copy.deepcopy(body)
            validate_request(body)
            bounded, tokens, usd = bounded_request(body, "generateContent", {})
            self.assertEqual(body, before)
            self.assertEqual(bounded, body)
            self.assertIsNone(tokens)
            self.assertIsNone(usd)

    def test_native_field_aliases_do_not_bypass_policy_or_budget(self):
        prices = {"input_per_mtok": 2, "output_per_mtok": 6, "cached_read_per_mtok": .5}
        for settings_key in ("generationConfig", "generation_config"):
            for limit_key in ("maxOutputTokens", "max_output_tokens"):
                body = {"contents": [{"parts": [{"text": "42"}]}],
                        settings_key: {limit_key: 128, "thinking_config": {"thinking_level": "LOW"}}}
                before = copy.deepcopy(body)
                validate_request(body)
                bounded, tokens, usd = bounded_request(body, "generateContent", prices)
                self.assertEqual(body, before)
                self.assertEqual(bounded, before)
                self.assertGreater(tokens, 128)
                self.assertGreater(usd, 0)
                with self.assertRaises(ValueError):
                    bounded_request(body, "generateContent", prices, maximum=32)
        for extra in (
            {"generationConfig": {}, "generation_config": {}},
            {"generationConfig": {"maxOutputTokens": 32, "max_output_tokens": 128}},
            {"tools": [{"google_search": {}}]},
            {"cached_content": "cachedContents/remote"},
            {"generationConfig": {"thinkingConfig": {"thinkingLevel": []}}},
        ):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                validate_request(payload(**extra))

    def test_registry_requires_native_google_operations_and_usage(self):
        config = {k: v for k, v in MODEL_PROVIDERS["google"].items() if k != "extract_usage"}
        config["routes"] = list(config["routes"]); config["passthrough"] = list(config["passthrough"])
        validate_access_routes({"google": config})
        for change in ({"transport": "google-code-assist"}, {"routes": ["chat/completions"]}, {"usage_parser": "openai"}):
            with self.assertRaises(ValueError): validate_access_routes({"google": {**config, **change}})
