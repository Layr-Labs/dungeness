"""Security boundary tests: rejected requests never reach a provider."""
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway  # Shared offline credentials and test environment.
import gateway
import gateway_pricing
from gateway_models import MODEL_PROVIDERS
from configured_fixture import configured_profiles
from gateway_runtime import Gateway
from gateway_request_policy import validate_model_request


MODELS = {
    "openai": "gpt-5.6-sol",
    "anthropic": "claude-opus-5",
    "claude-subscription": "example-model",
    "openrouter": "openai/gpt-5.6-sol",
    "openai-chatgpt": "gpt-6-astra",
    "example-api": "example-model",
    "example-session": "example-model",
    "grok-subscription": "grok-4.7",
    "minimax-subscription": "MiniMax-M3.1-Flash",
}


def route(provider, operation):
    slug = "chatgpt" if provider == "openai-chatgpt" else provider
    return f"/model/{slug}/v1/{operation}"


def request_body(provider, operation):
    payload = {"model": MODELS[provider]}
    if operation.startswith("messages") or operation == "chat/completions":
        payload["messages"] = [{"role": "user", "content": "solve locally"}]
    elif operation == "completions":
        payload["prompt"] = "solve locally"
    else:
        payload["input"] = "solve locally"
    if operation.startswith("messages"):
        payload["max_tokens"] = 32
    return payload


@asynccontextmanager
async def harness(*, declared=True, web=False):
    """HTTP requests are mocked; no live credentials or traffic."""
    with configured_profiles(), tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
        "TESTBED_USAGE_DIR": temp,
        "DUNGENESS_ALLOWED_MODELS": json.dumps(list(MODELS.items())) if declared else "",
        "MAX_MODEL_REQUESTS": "100", "MAX_MODEL_TOKENS": "1000000", "MAX_MODEL_USD": "100",
        "MAX_SEARCHES": "2" if web else "0", "MAX_FETCHES": "2" if web else "0",
        "DUNGENESS_CHATGPT_AUTH_FILE": str(Path(temp) / "auth.json"),
        "CLAUDE_ACCESS_TOKEN": "unused-claude-access",
        "CLAUDE_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
        "EXAMPLE_API_KEY": "unused-example-key",
        "EXAMPLE_SESSION_TOKEN": "unused-session",
        "EXAMPLE_SESSION_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
        "GROK_SUBSCRIPTION_TOKEN": "unused-grok-session",
        "GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
        "MINIMAX_CODING_PLAN_KEY": "unused-minimax-plan-key",
    }), patch.object(gateway_pricing, "MODEL_PRICING", [*gateway_pricing.MODEL_PRICING, *[
        {"provider": p, "upstream_id": "example/example-model", "request_models": [MODELS[p]],
         "input_per_mtok": 2, "output_per_mtok": 6, "cached_read_per_mtok": .5,
         "cache_write_per_mtok": 2, "text_only": True} for p in ("example-api", "example-session", "claude-subscription", "grok-subscription", "minimax-subscription")]]):
        Path(temp, "auth.json").write_text(json.dumps({
            "tokens": {"access_token": "private-test-token", "account_id": "private-account"}}))
        calls = []
        response = {"id": "resp-test", "object": "response", "status": "completed",
                    "output": [], "choices": [], "usage": {
                        "input_tokens": 2, "output_tokens": 1, "total_tokens": 3,
                        "prompt_tokens": 2, "completion_tokens": 1, "cost": 0.00001}}


        def upstream(request):
            calls.append(("http", json.loads(request.content), request))
            return httpx.Response(200, json=response)

        runtime = Gateway()
        await runtime.client.aclose()
        runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        try:
            with patch.object(gateway, "gateway", runtime):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                             base_url="http://gateway") as client:
                    yield client, runtime, calls
        finally:
            await runtime.client.aclose()


class RequestBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_text_only_quote_excludes_media_and_counts_reasoning_once(self):
        reference = {
            "provider": "openrouter", "upstream_id": MODELS["openrouter"],
            "request_models": [MODELS["openrouter"]], "text_only": True,
            "input_per_mtok": 2, "output_per_mtok": 10,
            "cached_read_per_mtok": .1, "cache_write_per_mtok": .1875,
            "disabled_optional_charges": {"image": "0.000002", "audio": "0.000002",
                                          "input_audio_cache": "0.0000001", "web_search": "0.014"},
        }
        usage = {"prompt_tokens": 1000, "completion_tokens": 300, "total_tokens": 1300,
                 "prompt_tokens_details": {"cached_tokens": 200},
                 "completion_tokens_details": {"reasoning_tokens": 250}}
        async with harness() as (client, runtime, calls):
            await runtime.client.aclose()
            def upstream(request):
                calls.append(json.loads(request.content))
                if "plugins" in calls[-1]:
                    return httpx.Response(403, json={"error": {"message": "Workspace blocks server tools"}})
                data = {"choices": [], "usage": usage}
                class Stream(httpx.AsyncByteStream):
                    async def __aiter__(self):
                        yield ("data: " + json.dumps(data) + "\n\ndata: [DONE]\n\n").encode()
                return httpx.Response(200, stream=Stream(),
                                      headers={"content-type": "text/event-stream"})
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            with patch.object(gateway_pricing, "MODEL_PRICING", [reference]):
                url = route("openrouter", "chat/completions")
                payload = {**request_body("openrouter", "chat/completions"), "stream": True}
                reply = await client.post(url, json=payload)
                self.assertEqual(reply.status_code, 200, reply.text)
                self.assertEqual(calls[0]["stream_options"], {"include_usage": True})
                self.assertNotIn("plugins", calls[0])
                self.assertAlmostEqual(runtime.ledger.usd_spent, .00462)
                for block in (
                    {"type": "image_url", "image_url": {"url": "https://example.invalid/image"}},
                    {"type": "input_audio", "input_audio": {"data": "AAAA", "format": "wav"}},
                    {"type": "video_url", "video_url": {"url": "https://example.invalid/video"}},
                ):
                    reply = await client.post(url, json={**payload, "messages": [
                        {"role": "user", "content": [block]}]})
                    self.assertEqual(reply.status_code, 400, reply.text)
                for extra in ({"modalities": ["text", "audio"]},
                              {"audio": {"voice": "alloy", "format": "wav"}},
                              {"web_search_options": {}}, {"plugins": [{"id": "web"}]}):
                    reply = await client.post(url, json={**payload, **extra})
                    self.assertEqual(reply.status_code, 400, reply.text)
                self.assertEqual(len(calls), 1)
                self.assertEqual(runtime.ledger.counts["model_requests"], 1)
                self.assertAlmostEqual(runtime.ledger.usd_spent, .00462)

    async def test_retired_providers_reject_all_inference_before_upstream(self):
        async with harness() as (client, runtime, calls):
            for provider in ("moonshot", "kimi-code"):
                self.assertNotIn(provider, gateway.MODEL_PROVIDERS)
                for operation in ("responses", "chat/completions"):
                    reply = await client.post(route(provider, operation),
                        json={"model": "k3", "input": "solve"})
                    self.assertEqual(reply.status_code, 404, reply.text)
            self.assertEqual(calls, [])
            self.assertEqual(runtime.ledger.counts["model_requests"], 0)

    async def test_native_chat_preserves_harness_payload_and_accounts_usage(self):
        async with harness() as (client, runtime, calls):
            for provider in ("openai", "example-api"):
                payload = {
                    "model": MODELS[provider],
                    "messages": [{"role": "user", "content": "Use my own strategy."}],
                    "tools": [{"type": "function", "function": {
                        "name": "evaluate", "parameters": {"type": "object"}}}],
                    "tool_choice": {"type": "function", "function": {"name": "evaluate"}},
                }
                reply = await client.post(route(provider, "chat/completions"), json=payload)
                self.assertEqual(reply.status_code, 200, reply.text)
                self.assertEqual(calls[-1][1], payload)
                upstream = calls[-1][2]
                self.assertEqual(upstream.headers["user-agent"], "dungeness-gateway/1")
                self.assertEqual(upstream.url.host,
                    "api.openai.com" if provider == "openai" else "api.example.invalid")
                self.assertEqual(reply.json()["usage"]["total_tokens"], 3)
            self.assertEqual(len(calls), 2)
            self.assertEqual(runtime.ledger.counts["model_requests"], 2)
            self.assertEqual(runtime.ledger.counts["model_tokens"], 6)
            self.assertGreater(runtime.ledger.usd_spent, 0)

    async def test_openrouter_is_closed_without_trusted_account_configuration(self):
        for declared in (False, True):
            with patch.dict(os.environ, {"DUNGENESS_OPENROUTER_INFERENCE_ONLY": ""}):
                async with harness(declared=declared) as (client, runtime, calls):
                    for operation in MODEL_PROVIDERS["openrouter"]["routes"] - {"models"}:
                        reply = await client.post(route("openrouter", operation),
                            json=request_body("openrouter", operation),
                            headers={"DUNGENESS_OPENROUTER_INFERENCE_ONLY": "1"})
                        self.assertEqual(reply.status_code, 400, reply.text)
                        self.assertIn("operator", reply.json()["error"])
                    self.assertEqual(calls, [])
                    self.assertEqual(runtime.ledger.counts["model_requests"], 0)

    async def test_every_inference_route_rejects_controls_before_upstream_and_accounting(self):
        injections = [
            {"mcp_servers": [{"url": "https://example.invalid"}]},
            {"plugins": [{"id": "web"}]},
            {"web_search_options": {}},
            {"models": ["another-model"]},
            {"route": "fallback"},
            {"future_search_option": True},
            {"extra_body": {"tools": [{"type": "web_search"}]}},
        ]
        # Every route, with/without a model allowlist and with/without trusted
        # web access. A web budget never enables provider-side search.
        injections += [
            {"tools": [{"type": kind}]} for kind in (
                "web_search", "web_search_preview", "web_search_20250305",
                "web_fetch_20250910", "openrouter:web_search", "mcp",
                "code_interpreter", "code_execution_20250825", "computer",
                "file_search", "tool_search", "tool_search_tool_regex_20251119",
                "browser_20251022", "future_server_tool",
            )
        ] + [
            {"tools": [{"type": "namespace", "name": "x",
                        "tools": [{"type": "web_search"}]}]},
            {"tools": [{"type": "function", "name": "local", "server_url": "https://example.invalid"}]},
            {"tools": [{"type": "custom", "name": "local", "input_schema": {},
                        "allowed_callers": ["code_execution_20250825"]}]},
            {"tools": [{"type": "shell"}]},
            {"tools": [{"type": "shell", "environment": {"type": "container_auto"}}]},
            {"tools": [{"type": "tool_search", "execution": "server"}]},
            {"tool_choice": {"type": "web_search"}},
            {"tool_choice": {"type": "allowed_tools", "mode": "auto",
                             "tools": [{"type": "web_search"}]}},
            {"tool_choice": {"type": "function", "name": "x",
                             "tools": [{"type": "web_search"}]}},
        ]
        for declared in (False, True):
            for web in (False, True):
                async with harness(declared=declared, web=web) as (client, runtime, calls):
                    for provider, cfg in MODEL_PROVIDERS.items():
                        for operation in sorted(cfg["routes"] - {"models"}):
                            for extra in injections:
                                with self.subTest(provider=provider, operation=operation,
                                                  declared=declared, web=web, extra=extra):
                                    reply = await client.post(route(provider, operation),
                                        json={**request_body(provider, operation), **extra})
                                    self.assertEqual(reply.status_code, 400, reply.text)
                    self.assertEqual(calls, [])
                    self.assertEqual(runtime.ledger.counts["model_requests"], 0)
                    self.assertEqual(runtime.ledger.usd_spent, 0)
                    self.assertEqual(runtime.ledger.model_inflight, {})

    async def test_transport_and_malformed_inputs_fail_closed_on_every_route(self):
        async with harness(declared=False) as (client, runtime, calls):
            for provider, cfg in MODEL_PROVIDERS.items():
                for operation in sorted(cfg["routes"] - {"models"}):
                    url = route(provider, operation)
                    payload = request_body(provider, operation)
                    for query in ("?plugins=web", "?beta=true&beta=false", "?search=true"):
                        reply = await client.post(url + query, json=payload)
                        self.assertEqual(reply.status_code, 400, reply.text)
                    for headers in (
                        {"anthropic-beta": "web-search-2025-03-05"},
                        {"openai-beta": "unreviewed-feature"},
                        [("anthropic-beta", "prompt-caching-2024-07-31"),
                         ("anthropic-beta", "unreviewed-feature")],
                        {"anthropic-version": "future"},
                    ):
                        reply = await client.post(url, json=payload, headers=headers)
                        self.assertEqual(reply.status_code, 400, reply.text)
                    for body in (b"{", b"\xff", b"[]", b"null", b'{"model": {}}'):
                        reply = await client.post(url, content=body)
                        self.assertEqual(reply.status_code, 400, reply.text)
                    reply = await client.request("GET", url, json=payload)
                    self.assertIn(reply.status_code, (400, 405), reply.text)
                    reply = await client.post(url, json={**payload, "model": MODELS[provider] + ":online"})
                    self.assertEqual(reply.status_code, 400, reply.text)
                    reply = await client.post(url, json={**payload, "model": "@preset"})
                    self.assertEqual(reply.status_code, 400, reply.text)
            self.assertEqual(calls, [])
            self.assertEqual(runtime.ledger.counts["model_requests"], 0)

    async def test_explicit_history_cannot_inject_server_tools_or_hidden_state(self):
        bad_history = [
            {"type": "item_reference", "id": "remote"},
            {"type": "mcp_call", "name": "search"},
            {"type": "web_search_call", "id": "search"},
            {"type": "tool_search_output", "execution": "server", "tools": []},
            {"type": "tool_search_output", "execution": "client",
             "tools": [{"type": "namespace", "name": "hidden", "tools": [{"type": "web_search"}]}]},
            {"type": "shell_call", "environment": {"type": "container_reference", "container_id": "x"}},
            {"role": "user", "content": [{"type": "input_image", "image_url": "https://example.invalid"}]},
        ]
        async with harness() as (client, runtime, calls):
            for provider, cfg in MODEL_PROVIDERS.items():
                for operation in cfg["routes"] & {"responses", "responses/compact"}:
                    for extra in ([{"input": [item]} for item in bad_history] + [
                        {"previous_response_id": "remote"}, {"conversation": "remote"},
                        {"prompt": {"id": "remote"}}, {"background": True},
                    ]):
                        reply = await client.post(route(provider, operation),
                            json={**request_body(provider, operation), **extra})
                        self.assertEqual(reply.status_code, 400, reply.text)
            for provider in ("anthropic", "openrouter"):
                for block in (
                    {"type": "server_tool_use", "name": "web_search", "input": {}},
                    {"type": "mcp_tool_use", "name": "web_search"},
                    {"type": "document", "source": {"type": "url", "url": "https://example.invalid"}},
                ):
                    reply = await client.post(route(provider, "messages"), json={
                        **request_body(provider, "messages"),
                        "messages": [{"role": "assistant", "content": [block]}]})
                    self.assertEqual(reply.status_code, 400, reply.text)
            self.assertEqual(calls, [])

    async def test_supported_protocols_work_for_legacy_and_arbitrary_command_harnesses(self):
        for declared in (False, True):
            async with harness(declared=declared) as (client, runtime, calls):
                expected = 0
                for provider, cfg in MODEL_PROVIDERS.items():
                    for operation in sorted(cfg["routes"] - {"models"}):
                        payload = request_body(provider, operation)
                        if operation in ("responses", "chat/completions"):
                            payload["tools"] = [{"type": "function", "name": "search_local_files",
                                                 "parameters": {"type": "object"}}] if operation == "responses" else [
                                {"type": "function", "function": {"name": "search_local_files",
                                                                 "parameters": {"type": "object"}}}]
                        elif operation.startswith("messages"):
                            payload["tools"] = [{"name": "local_evaluate", "input_schema": {"type": "object"}}]
                        suffix = "?beta=true" if operation.startswith("messages") else ""
                        reply = await client.post(route(provider, operation) + suffix, json=payload,
                            headers={"x-untrusted-search": "true"})
                        self.assertEqual(reply.status_code, 200, (provider, operation, reply.text))
                        expected += 1
                        if provider == "openrouter":
                            self.assertNotIn("plugins", calls[-1][1])
                        if calls[-1][0] == "http":
                            self.assertNotIn("x-untrusted-search", calls[-1][2].headers)
                self.assertEqual(len(calls), expected)
                self.assertEqual(runtime.ledger.counts["model_requests"], expected)
                self.assertEqual(runtime.ledger.model_inflight, {})

    async def test_codex_and_claude_local_tool_round_trips(self):
        responses = {
            "model": MODELS["openai"], "store": False, "include": ["reasoning.encrypted_content"],
            "reasoning": {"effort": "high", "summary": "auto"},
            "tools": [
                {"type": "namespace", "name": "local", "description": "Local tools", "tools": [
                    {"type": "function", "name": "web_search", "parameters": {"type": "object"}},
                    {"type": "custom", "name": "patch", "format": {"type": "text"}}]},
                {"type": "shell", "environment": {"type": "local"}},
                {"type": "tool_search", "execution": "client", "parameters": {"type": "object"}},
            ],
            "input": [
                {"role": "user", "content": "Search our bundled papers using local files."},
                {"type": "reasoning", "id": "r", "summary": [], "encrypted_content": "opaque"},
                {"type": "function_call", "call_id": "c", "name": "web_search", "arguments": '{"mcp_servers": []}'},
                {"type": "function_call_output", "call_id": "c", "output": "Local results"},
                {"type": "shell_call_output", "call_id": "s", "output": [
                    {"stdout": "ok", "stderr": "", "outcome": {"type": "exit", "exit_code": 0}}]},
                {"type": "tool_search_output", "execution": "client", "call_id": "ts", "tools": [
                    {"type": "function", "name": "read_file", "defer_loading": True, "parameters": {}}]},
            ],
        }
        messages = {
            "model": MODELS["anthropic"], "max_tokens": 128,
            "system": [{"type": "text", "text": "Use local tools", "cache_control": {"type": "ephemeral"}}],
            "thinking": {"type": "enabled", "budget_tokens": 1024},
            "tools": [{"name": "evaluate", "input_schema": {"type": "object"}},
                      {"type": "bash_20250124", "name": "bash"}],
            "tool_choice": {"type": "auto", "disable_parallel_tool_use": True},
            "messages": [
                {"role": "user", "content": "evaluate"},
                {"role": "assistant", "content": [
                    {"type": "thinking", "thinking": "Use the local evaluator", "signature": "sig"},
                    {"type": "tool_use", "id": "c", "name": "evaluate",
                     "caller": {"type": "direct"},
                     "input": {"type": {"arbitrary": "data"}, "image_url": "local filename", "plugins": []}}]},
                {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": "c", "content": "ok"}]},
            ],
        }
        async with harness() as (client, runtime, calls):
            for provider, operation, payload in (
                ("openai", "responses", responses), ("anthropic", "messages", messages)
            ):
                reply = await client.post(route(provider, operation), json=payload)
                self.assertEqual(reply.status_code, 200, reply.text)
                self.assertEqual(calls[-1][1], payload)
            self.assertEqual(len(calls), 2)

    async def test_model_discovery_is_local_and_filters_declared_models(self):
        async with harness() as (client, runtime, calls):
            for provider in ("openai", "openrouter"):
                url = route(provider, "models")
                reply = await client.get(url)
                self.assertEqual(reply.status_code, 200)
                self.assertEqual([item["id"] for item in reply.json()["data"]], [MODELS[provider]])
                for method, target, body in (("POST", url, {}), ("GET", url + "?search=true", None),
                                              ("GET", url, {"tools": [{"type": "web_search"}]})):
                    reply = await client.request(method, target, json=body)
                    self.assertEqual(reply.status_code, 400, reply.text)
            self.assertEqual(calls, [])
            self.assertEqual(runtime.ledger.counts["model_requests"], 0)

    async def test_disabled_web_budget_rejects_search_and_fetch_without_upstream(self):
        async with harness() as (client, runtime, calls):
            for path, payload in (
                ("/web/search", {"query": "paper"}),
                ("/web/fetch", {"url": "https://example.invalid/paper"}),
            ):
                reply = await client.post(path, json=payload)
                self.assertEqual(reply.status_code, 410, reply.text)
            self.assertEqual(calls, [])


class PolicyShapeTests(unittest.TestCase):
    def test_embedding_and_completion_inputs_cannot_carry_remote_envelopes(self):
        for operation, field in (("embeddings", "input"), ("completions", "prompt")):
            for value in ({"url": "https://example.invalid"}, [{"type": "web_search"}]):
                with self.subTest(operation=operation, value=value), self.assertRaises(ValueError):
                    validate_model_request("openai", operation, {"model": MODELS["openai"], field: value})
            for value in ("text", ["text", "other text"], [1, 2], [[1, 2], [3]]):
                validate_model_request("openai", operation, {"model": MODELS["openai"], field: value})

    def test_bad_control_shapes_raise_value_error_not_internal_errors(self):
        for extra in (
            {"tools": {}}, {"tools": [None]}, {"tools": [{"type": {}}]},
            {"tool_choice": {"type": {}}}, {"tool_choice": []},
            {"input": [{"type": {}}]}, {"input": [{"role": {}}]},
            {"text": []}, {"text": {"format": {"type": {}}}},
            {"reasoning": {"future_control": True}},
            {"include": {}}, {"include": [{}]},
            {"context_management": {"edits": [{"type": {}}]}},
            {"provider": {"sort": {"future_control": True}}},
        ):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                validate_model_request("openrouter", "responses", {"model": MODELS["openrouter"], **extra})


if __name__ == "__main__":
    unittest.main()
