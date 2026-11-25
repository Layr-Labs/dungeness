"""Google-compatible wire shapes with a synthetic upstream."""
import copy
import json
import unittest

import httpx
from test_history_roundtrip import Fragments
from test_request_policy import harness, request_body, route
from gateway_request_policy import validate_model_request
from gateway_reservations import bounded_request


OPERATION = "chat/completions"
# A configured route deliberately has no vendor-specific name.
PROVIDER = "example-session"
THINKING = {"google": {"thinking_config": {"thinking_level": "high", "include_thoughts": True}}}
SIGNATURE = {"google": {"thought_signature": "opaque-synthetic-α=="}}
ASSISTANT = {
    "role": "assistant", "content": "Evaluate the candidate locally.",
    "extra_content": SIGNATURE,
    "tool_calls": [
        {"id": "call_one", "type": "function",
         "function": {"name": "evaluate", "arguments": '{"candidate":"local"}'},
         "extra_content": SIGNATURE},
        {"id": "call_two", "type": "function",
         "function": {"name": "read_result", "arguments": "{}"}},
    ],
}
# An OpenAI-compatible usage contract: reasoning is included in completion.
USAGE = {"prompt_tokens": 20, "completion_tokens": 7, "total_tokens": 27,
         "prompt_tokens_details": {"cached_tokens": 5},
         "completion_tokens_details": {"reasoning_tokens": 3}}


class GoogleThinkingTests(unittest.IsolatedAsyncioTestCase):
    async def test_thinking_and_tool_signatures_roundtrip_with_json_and_fragmented_sse(self):
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                async with harness() as (client, runtime, _):
                    captured = []
                    # Signatures can arrive on a late, otherwise empty delta.
                    first_delta = copy.deepcopy(ASSISTANT)
                    del first_delta["extra_content"]
                    del first_delta["tool_calls"][0]["extra_content"]
                    for index, call in enumerate(first_delta["tool_calls"]):
                        call["index"] = index
                    events = [
                        {"choices": [{"index": 0, "delta": first_delta}]},
                        {"choices": [{"index": 0, "delta": {
                            "extra_content": SIGNATURE,
                            "tool_calls": [{"index": 0, "extra_content": SIGNATURE}],
                        }}]},
                        {"choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]},
                        {"choices": [], "usage": USAGE},
                    ]
                    body = ("".join("data: " + json.dumps(e, ensure_ascii=False) + "\n\n"
                                    for e in events) + "data: [DONE]\n\n").encode()

                    def upstream(request):
                        captured.append(json.loads(request.content))
                        if streaming:
                            return httpx.Response(200, headers={"content-type": "text/event-stream"},
                                                  stream=Fragments(body))
                        return httpx.Response(200, json={
                            "choices": [{"index": 0, "message": ASSISTANT, "finish_reason": "tool_calls"}],
                            "usage": USAGE})

                    await runtime.client.aclose()
                    runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                    payload = {**request_body(PROVIDER, OPERATION), "extra_body": THINKING, "stream": streaming,
                               "tools": [{"type": "function", "function": {
                                   "name": name, "parameters": {"type": "object"}}}
                                   for name in ("evaluate", "read_result")]}
                    response = await client.post(route(PROVIDER, OPERATION), json=payload)
                    self.assertEqual(response.status_code, 200, response.text)
                    if streaming:
                        self.assertEqual(response.content, body)
                        chunks = [json.loads(line[6:]) for line in response.text.splitlines()
                                  if line.startswith("data: ") and line != "data: [DONE]"]
                        history = chunks[0]["choices"][0]["delta"]
                        late = chunks[1]["choices"][0]["delta"]
                        history["extra_content"] = late["extra_content"]
                        history["tool_calls"][0]["extra_content"] = late["tool_calls"][0]["extra_content"]
                        for call in history["tool_calls"]:
                            del call["index"]
                    else:
                        history = response.json()["choices"][0]["message"]
                    self.assertEqual(history, ASSISTANT)
                    followup = {**payload, "messages": payload["messages"] + [
                        history, {"role": "tool", "tool_call_id": "call_one", "content": "valid"},
                        {"role": "tool", "tool_call_id": "call_two", "content": "score: 42"}]}
                    response = await client.post(route(PROVIDER, OPERATION), json=followup)
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertEqual(captured[0]["extra_body"], THINKING)
                    self.assertEqual(captured[1]["messages"], followup["messages"])
                    accounting = [json.loads(line)["data"] for line in
                                  (runtime.ledger.directory / "events.jsonl").read_text().splitlines()
                                  if json.loads(line)["kind"] == "model.accounting"]
                    self.assertEqual(len(accounting), 2)
                    for event in accounting:
                        self.assertEqual(event["input_tokens"], 20)
                        self.assertEqual(event["cached_input_tokens"], 5)
                        self.assertEqual(event["output_tokens"], 7)
                        self.assertEqual(event["reasoning_tokens"], 3)

    async def test_thinking_cannot_enable_hosted_tools_or_remote_state(self):
        async with harness() as (client, runtime, calls):
            before = copy.deepcopy(runtime.ledger.counts)
            for extra in (
                {"google": {"thinking_config": {"thinking_level": "high"}, "tools": [{"google_search": {}}]}},
                {"google": {"thinking_config": {"tools": [{"code_execution": {}}]}}},
                {"google": {"cached_content": "cachedContents/hidden"}},
                {"google": {"url_context": {}}},
                {"tools": [{"type": "web_search"}]},
            ):
                response = await client.post(route(PROVIDER, OPERATION), json={
                    **request_body(PROVIDER, OPERATION), "extra_body": extra})
                self.assertEqual(response.status_code, 400, response.text)
            for location in ("message", "tool_call"):
                message = copy.deepcopy(ASSISTANT)
                target = message if location == "message" else message["tool_calls"][0]
                target["extra_content"]["google"]["secret-unknown-field"] = {"tools": [{"google_search": {}}]}
                response = await client.post(route(PROVIDER, OPERATION), json={
                    **request_body(PROVIDER, OPERATION), "messages": [message]})
                self.assertEqual(response.status_code, 400, response.text)
                self.assertNotIn("secret-unknown-field", response.text)
            for tool in ({"google_search": {}}, {"url_context": {}}, {"code_execution": {}},
                         {"type": "web_search"}, {"type": "mcp"}):
                response = await client.post(route(PROVIDER, OPERATION), json={
                    **request_body(PROVIDER, OPERATION), "extra_body": THINKING, "tools": [tool]})
                self.assertEqual(response.status_code, 400, response.text)
            self.assertEqual(calls, [])
            self.assertEqual(runtime.ledger.counts, before)


class GoogleThinkingSchemaTests(unittest.TestCase):
    def test_effort_budget_and_summary_controls_preserved(self):
        for config in (
            *({"thinking_level": level} for level in ("minimal", "low", "medium", "high", "xhigh")),
            *({"thinking_budget": budget} for budget in (-1, 0, 1024)),
            {"include_thoughts": False},
        ):
            payload = {**request_body(PROVIDER, OPERATION), "extra_body": {"google": {"thinking_config": config}}}
            before = copy.deepcopy(payload)
            validate_model_request(PROVIDER, OPERATION, payload)
            self.assertEqual(payload, before)
        for effort in ("none", "minimal", "low", "medium", "high", "xhigh"):
            payload = {**request_body(PROVIDER, OPERATION), "reasoning_effort": effort,
                       "extra_body": {"google": {"thinking_config": {"include_thoughts": True}}}}
            validate_model_request(PROVIDER, OPERATION, payload)

    def test_malformed_and_conflicting_controls_rejected(self):
        for config in (
            None, [], {"thinking_level": {}}, {"thinking_level": "unknown"},
            *({"thinking_budget": value} for value in (True, "1024", -2, 1.5, 2**31)),
            {"include_thoughts": 1}, {"include_thoughts": None},
            {"thinking_level": "high", "thinking_budget": 1024},
        ):
            with self.subTest(config=config), self.assertRaises(ValueError):
                validate_model_request(PROVIDER, OPERATION, {
                    **request_body(PROVIDER, OPERATION), "extra_body": {"google": {"thinking_config": config}}})
        for selector in ({"thinking_level": "high"}, {"thinking_budget": 1024}):
            with self.assertRaises(ValueError):
                validate_model_request(PROVIDER, OPERATION, {
                    **request_body(PROVIDER, OPERATION), "reasoning_effort": "low",
                    "extra_body": {"google": {"thinking_config": selector}}})

    def test_signature_is_assistant_chat_history_only_and_opaque_to_reservations(self):
        for location in ("message", "tool_call"):
            for invalid in (None, [], {"google": {}},
                            {"google": {"thought_signature": 123}}, {"google": {"thought_signature": ""}}):
                message = copy.deepcopy(ASSISTANT)
                (message if location == "message" else message["tool_calls"][0])["extra_content"] = invalid
                with self.assertRaises(ValueError):
                    validate_model_request(PROVIDER, OPERATION, {
                        **request_body(PROVIDER, OPERATION), "messages": [message]})
        for operation, role in (("messages", "assistant"), (OPERATION, "user"), (OPERATION, "tool")):
            with self.assertRaises(ValueError):
                validate_model_request(PROVIDER, operation, {
                    **request_body(PROVIDER, OPERATION), "messages": [{**ASSISTANT, "role": role}]})
        payload = {**request_body(PROVIDER, OPERATION), "messages": [ASSISTANT]}
        bounded, tokens, usd = bounded_request(payload, OPERATION, {})
        self.assertEqual(bounded["messages"], payload["messages"])
        self.assertIsNone(tokens)
        self.assertIsNone(usd)

    def test_openai_and_claude_thinking_are_unchanged(self):
        for provider, operation, settings in (
            ("openai", "responses", {"reasoning": {"effort": "high"}}),
            ("openai-chatgpt", "responses", {"reasoning": {"effort": "high"}}),
            ("anthropic", "messages", {"thinking": {"type": "enabled", "budget_tokens": 1024}}),
            ("claude-subscription", "messages", {"thinking": {"type": "adaptive"}, "output_config": {"effort": "high"}}),
        ):
            payload = {**request_body(provider, operation), **settings}
            before = copy.deepcopy(payload)
            validate_model_request(provider, operation, payload)
            self.assertEqual(payload, before)
