"""Official xAI route exercised through the gateway with synthetic responses."""
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

MODEL = "grok-4.7"
PAYLOAD = {"model": MODEL, "input": "Return 42 using the local tool.",
           "store": False, "max_output_tokens": 512, "reasoning": {"effort": "high"}}
REASONING = {"id": "rs-1", "type": "reasoning", "summary": [],
             "encrypted_content": "opaque-native-reasoning"}
FUNCTION = {"id": "fc-1", "type": "function_call", "call_id": "call-1",
            "name": "answer", "arguments": '{"value":42}', "status": "completed"}


def result(input_tokens=100, cached=40):
    return {"id": "resp-1", "object": "response", "status": "completed", "model": MODEL,
            "output": [REASONING, FUNCTION],
            "usage": {"input_tokens": input_tokens, "input_tokens_details": {"cached_tokens": cached},
                      "output_tokens": 30, "output_tokens_details": {"reasoning_tokens": 20},
                      "total_tokens": input_tokens + 30, "cost_in_usd_ticks": 3200000}}


class Fragments(httpx.AsyncByteStream):
    def __init__(self, body):
        self.body = body

    async def __aiter__(self):
        for offset in range(0, len(self.body), 13):
            yield self.body[offset:offset + 13]


@asynccontextmanager
async def grok_gateway(responses, *, values=None, budget="20"):
    with tempfile.TemporaryDirectory() as temp:
        private = Path(temp) / "credentials.json"
        private.write_text(json.dumps({"XAI_API_KEY": "synthetic-xai-secret"} if values is None else values))
        private.chmod(0o600)
        with patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": str(Path(temp) / "usage"), "TESTBED_RUN_ID": "grok-api",
            "DUNGENESS_CREDENTIALS_FILE": str(private),
            "DUNGENESS_ALLOWED_MODELS": json.dumps([["xai", MODEL]]),
            "DUNGENESS_REQUIRE_MODEL_ALLOWLIST": "1",
            "MAX_MODEL_REQUESTS": "10", "MAX_MODEL_TOKENS": "2000000", "MAX_MODEL_USD": budget,
            "MAX_SEARCHES": "0", "MAX_FETCHES": "0",
        }, clear=True):
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []
            remaining = iter(responses)

            def upstream(request):
                calls.append(request)
                return next(remaining)

            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream), follow_redirects=False)
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        yield client, runtime, calls
            finally:
                await runtime.client.aclose()


class GrokRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_responses_tool_history_stream_and_usage_are_preserved(self):
        first = result()
        final = {**result(), "id": "resp-2", "output": [
            {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "42"}]}]}
        wire = ('event: response.completed\ndata: ' +
                json.dumps({"type": "response.completed", "response": final}) + '\n\n').encode()
        responses = [httpx.Response(200, json=first),
                     httpx.Response(200, stream=Fragments(wire), headers={"content-type": "text/event-stream"})]
        async with grok_gateway(responses) as (client, runtime, calls):
            listing = await client.get("/model/xai/v1/models")
            self.assertEqual([m["id"] for m in listing.json()["data"]], [MODEL])
            self.assertFalse(calls)
            response = await client.post("/model/xai/v1/responses", json=PAYLOAD,
                                         headers={"authorization": "Bearer testbed", "x-api-key": "not-upstream"})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json(), first)
            continuation = {**PAYLOAD, "stream": True, "input": [
                {"role": "user", "content": PAYLOAD["input"]}, *first["output"],
                {"type": "function_call_output", "call_id": "call-1", "output": "42"}]}
            streamed = await client.post("/model/xai/v1/responses", json=continuation)
            self.assertEqual(streamed.status_code, 200, streamed.text)
            self.assertEqual(streamed.content, wire)
            self.assertEqual(json.loads(calls[0].content), PAYLOAD)
            self.assertEqual(json.loads(calls[1].content), continuation)
            for request in calls:
                self.assertEqual(str(request.url), "https://api.x.ai/v1/responses")
                self.assertEqual(request.headers["authorization"], "Bearer synthetic-xai-secret")
                self.assertNotIn("x-api-key", request.headers)
            receipts = canonical_events(runtime.ledger.directory, "model.accounting")
            self.assertEqual(len(receipts), 2)
            for receipt in receipts:
                self.assertEqual(receipt["cached_input_tokens"], 40)
                self.assertEqual(receipt["reasoning_tokens"], 20)
                self.assertEqual(receipt["output_tokens"], 30)  # Reasoning is already included.
                self.assertEqual(receipt["accounting_basis"], "provider_usage")
                self.assertAlmostEqual(receipt["normalized_usd"], .000320)
                self.assertIsNone(receipt["billed_usd"])
            self.assertNotIn("synthetic-xai-secret", (runtime.ledger.directory / "events.jsonl").read_text())

    async def test_chat_completions_stream_accounts_final_usage_once(self):
        usage = {"prompt_tokens": 100, "prompt_tokens_details": {"cached_tokens": 40},
                 "completion_tokens": 30, "completion_tokens_details": {"reasoning_tokens": 20},
                 "total_tokens": 130, "cost_in_usd_ticks": 3200000}
        wire = ('data: {"choices":[{"index":0,"delta":{"content":"42"},"finish_reason":null}]}\n\n'
                'data: ' + json.dumps({"choices": [], "usage": usage}) + '\n\ndata: [DONE]\n\n').encode()
        async with grok_gateway([httpx.Response(200, stream=Fragments(wire),
                                 headers={"content-type": "text/event-stream"})]) as (client, runtime, calls):
            payload = {"model": MODEL, "messages": [{"role": "user", "content": "Return 42"}],
                       "max_tokens": 512, "stream": True, "stream_options": {"include_usage": True}}
            response = await client.post("/model/xai/v1/chat/completions", json=payload,
                                         headers={"x-grok-conv-id": "local-conversation"})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.content, wire)
            self.assertEqual(str(calls[0].url), "https://api.x.ai/v1/chat/completions")
            self.assertEqual(calls[0].headers["x-grok-conv-id"], "local-conversation")
            receipt, = canonical_events(runtime.ledger.directory, "model.accounting")
            self.assertAlmostEqual(receipt["normalized_usd"], .000320)

    async def test_whole_request_price_changes_at_exactly_200000_input_tokens(self):
        for tokens, tier, usd in ((199999, "base", .400118), (200000, "long_context", .800240),
                                  (200001, "long_context", .800244)):
            with self.subTest(tokens=tokens):
                async with grok_gateway([httpx.Response(200, json=result(tokens))]) as (client, runtime, _):
                    response = await client.post("/model/xai/v1/responses", json=PAYLOAD)
                    self.assertEqual(response.status_code, 200, response.text)
                    receipt, = canonical_events(runtime.ledger.directory, "model.accounting")
                    self.assertEqual(receipt["pricing_tier"], tier)
                    self.assertAlmostEqual(receipt["normalized_usd"], usd)

    async def test_unapproved_models_remote_tools_and_server_history_never_reach_upstream(self):
        async with grok_gateway([]) as (client, runtime, calls):
            before = dict(runtime.ledger.counts)
            cases = [{"model": "grok-4.7-fast"}, {"model": "unapproved"},
                     {"previous_response_id": "remote-history"}, {"background": True}]
            cases += [{"tools": [{"type": tool}]} for tool in
                      ("web_search", "x_search", "code_interpreter", "code_execution", "mcp")]
            for patch_body in cases:
                response = await client.post("/model/xai/v1/responses", json={**PAYLOAD, **patch_body})
                self.assertGreaterEqual(response.status_code, 400, response.text)
            for path in ("files", "responses/remote-history", "batches"):
                response = await client.get(f"/model/xai/v1/{path}")
                self.assertGreaterEqual(response.status_code, 400)
            self.assertFalse(calls)
            self.assertEqual(runtime.ledger.counts, before)

    async def test_missing_credentials_budget_exhaustion_and_redirects(self):
        async with grok_gateway([], values={}) as (client, runtime, calls):
            before = dict(runtime.ledger.counts)
            response = await client.post("/model/xai/v1/responses", json=PAYLOAD)
            self.assertEqual(response.json()["diagnostic"]["code"], "provider_credentials_unavailable")
            self.assertFalse(calls)
            self.assertEqual(runtime.ledger.counts, before)
        async with grok_gateway([], budget="0") as (client, _, calls):
            response = await client.post("/model/xai/v1/responses", json=PAYLOAD)
            self.assertGreaterEqual(response.status_code, 400)
            self.assertFalse(calls)
        async with grok_gateway([httpx.Response(307, headers={"location": "https://unapproved.invalid"})]) as (client, _, calls):
            response = await client.post("/model/xai/v1/responses", json=PAYLOAD)
            self.assertEqual(response.status_code, 502)
            self.assertEqual(len(calls), 1)
            self.assertNotIn("location", response.headers)

    async def test_missing_usage_stays_unknown_and_stops_followup_calls(self):
        response_body = result()
        del response_body["usage"]
        async with grok_gateway([httpx.Response(200, json=response_body)]) as (client, runtime, calls):
            await client.post("/model/xai/v1/responses", json=PAYLOAD)
            receipt, = canonical_events(runtime.ledger.directory, "model.accounting")
            self.assertEqual(receipt["accounting_basis"], "unavailable")
            followup = await client.post("/model/xai/v1/responses", json=PAYLOAD)
            self.assertGreaterEqual(followup.status_code, 400)
            self.assertEqual(len(calls), 1)
