from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from starlette.testclient import TestClient


_IMPORT_USAGE = tempfile.TemporaryDirectory()
os.environ.update(
    {
        "TESTBED_RUN_ID": "unit-test",
        "MAX_SEARCHES": "2",
        "MAX_FETCHES": "2",
        "MAX_MODEL_REQUESTS": "2",
        "MAX_MODEL_TOKENS": "100",
        "EXA_END_PUBLISHED_DATE": "2026-07-05T23:59:59.999Z",
        "TESTBED_USAGE_DIR": _IMPORT_USAGE.name,
        "EXA_API_KEY": "unused",
        "OPENAI_API_KEY": "unused",
        "OPENROUTER_API_KEY": "unused",
        "DUNGENESS_OPENROUTER_INFERENCE_ONLY": "1",
        "ANTHROPIC_API_KEY": "unused",
        "MOONSHOT_API_KEY": "unused",
        "KIMI_CODE_API_KEY": "membership-unused",
        "MAX_MODEL_USD": "1.0",
    }
)

import gateway as gateway_module
from gateway import (
    app,
    BudgetExceeded,
    gateway,
    MODEL_PROVIDERS,
    Metrics,
    UsageLedger,
    bounded_model_name,
    drain_background_tasks,
    approve_historical_result,
    extract_usage,
    historical_date_evidence,
    immutable_historical_url,
    instrumentation_route,
    is_sse_body,
    log_event,
    make_search_payload,
    mutable_url_reason,
    parse_utc,
    safe_request_id,
)


def canonical_events(
    directory: str | Path,
    *kinds: str,
) -> list[dict]:
    path = Path(directory) / "events.jsonl"
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    selected = [
        record
        for record in records
        if not kinds or record.get("kind") in kinds
    ]
    flattened = []
    for record in selected:
        data = record.get("data")
        event = dict(data) if isinstance(data, dict) else {}
        event.update(
            {
                key: record[key]
                for key in (
                    "run_id",
                    "sequence",
                    "kind",
                    "observed_at",
                    "event_id",
                    "request_id",
                )
                if key in record
            }
        )
        event["event_source"] = record.get("source")
        if "usage" in record:
            event["cumulative_usage"] = record["usage"]
        flattened.append(event)
    return flattened


def canonical_event(directory: str | Path, kind: str) -> dict:
    events = canonical_events(directory, kind)
    if len(events) != 1:
        raise AssertionError(
            f"expected exactly one {kind} event, found {len(events)}"
        )
    return events[0]


class ModuleLayoutTests(unittest.TestCase):
    def test_entrypoint_reexports_split_gateway_modules(self) -> None:
        import gateway_models
        import gateway_pricing
        import gateway_runtime
        import gateway_usage
        import gateway_web

        self.assertIs(gateway_module.MODEL_PROVIDERS, gateway_models.MODEL_PROVIDERS)
        self.assertIs(gateway_module.Gateway, gateway_runtime.Gateway)
        self.assertIs(
            gateway_module._BACKGROUND_TASKS,
            gateway_runtime.BACKGROUND_TASKS,
        )
        self.assertIs(gateway_module.UsageLedger, gateway_usage.UsageLedger)
        self.assertIs(
            gateway_module.pricing_for_request,
            gateway_pricing.pricing_for_request,
        )
        self.assertIs(
            gateway_module.approve_historical_result,
            gateway_web.approve_historical_result,
        )

    def test_gateway_image_copies_every_runtime_module(self) -> None:
        dockerfile = (
            Path(__file__).resolve().parents[1] / "Dockerfile"
        ).read_text(encoding="utf-8")
        for filename in (
            "gateway.py",
            "gateway_models.py",
            "gateway_auth.py",
            "gateway_request_policy.py",
            "gateway_pricing.py",
            "gateway_runtime.py",
            "gateway_usage.py",
            "gateway_web.py",
        ):
            self.assertIn(f"COPY {filename} /app/{filename}", dockerfile)


class SearchPolicyTests(unittest.TestCase):
    def test_responses_preserve_harness_prompt_without_controller_calls(self) -> None:
        payload = {
            "model": "gpt-5.6-sol",
            "input": [
                {"role": "developer", "content": "Use my own research strategy."},
                {"role": "user", "content": "Evaluate when useful, then finish."},
            ],
        }
        requests = []

        async def upstream(request):
            requests.append(request.url.path)
            self.assertEqual(request.url.path, "/v1/responses")
            self.assertEqual(json.loads(request.content), payload)
            return httpx.Response(200, json={
                "output": [], "usage": {"input_tokens": 11, "output_tokens": 4, "total_tokens": 15},
            })

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("no-controller", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            with (
                patch.object(gateway, "client", model_client),
                patch.object(gateway, "ledger", ledger),
                # A stale environment from an older deployment must not mutate prompts.
                patch.dict(os.environ, {"DUNGENESS_RESEARCH_STATE_URL": "http://retired.invalid"}),
                TestClient(app) as client,
            ):
                response = client.post("/model/openai/v1/responses", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(requests, ["/v1/responses"])
            self.assertEqual(ledger.counts["model_tokens"], 15)
            self.assertEqual(canonical_event(directory, "model.request")["request"], payload)


    def test_exa_date_only_metadata_is_accepted_as_utc(self) -> None:
        self.assertLess(
            parse_utc("2023-11-16"), parse_utc("2026-07-05T23:59:59.999Z")
        )

    def test_publication_cutoff_and_cache_only_are_forced(self) -> None:
        payload = make_search_payload(
            "world map contact graph",
            {"num_results": 100, "contents": {"highlights": True}},
            max_results=25,
            end_published_date="2026-07-05T23:59:59.999Z",
        )
        self.assertEqual(payload["numResults"], 25)
        self.assertEqual(
            payload["endPublishedDate"], "2026-07-05T23:59:59.999Z"
        )
        self.assertNotIn("endCrawlDate", payload)
        self.assertEqual(payload["contents"]["maxAgeHours"], -1)

    def test_categories_without_date_filter_support_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not apply date filters"):
            make_search_payload(
                "mapping company",
                {"category": "company"},
                max_results=25,
                end_published_date="2026-07-05T23:59:59.999Z",
            )

    def test_undated_result_is_rejected(self) -> None:
        approval, reason = approve_historical_result(
            {"url": "https://example.com/research"},
            parse_utc("2026-04-13T23:59:59.999Z"),
        )
        self.assertIsNone(approval)
        self.assertEqual(reason, "missing_date")

    def test_nested_post_cutoff_date_is_rejected(self) -> None:
        approval, reason = approve_historical_result(
            {
                "url": "https://arxiv.org/html/2606.02235",
                "publishedDate": None,
                "entities": [{"properties": {"date": "2026-06-01"}}],
            },
            parse_utc("2026-04-13T23:59:59.999Z"),
        )
        self.assertIsNone(approval)
        self.assertEqual(reason, "post_cutoff")

    def test_arxiv_identifier_is_independent_post_cutoff_evidence(self) -> None:
        evidence = historical_date_evidence(
            {
                "url": "https://arxiv.org/html/2606.02235",
                "publishedDate": "2026-01-01",
            }
        )
        self.assertIn(
            ("url.arxiv_identifier", parse_utc("2026-06-01")),
            evidence,
        )

    def test_mutable_source_control_urls_are_rejected(self) -> None:
        self.assertEqual(
            mutable_url_reason(
                "https://github.com/ecdsafail/ecdsafail-challenge/blob/main/src/point_add.rs"
            ),
            "mutable_git_ref",
        )
        self.assertEqual(
            mutable_url_reason("https://github.com/trailofbits/trailmix"),
            "mutable_git_url",
        )
        self.assertEqual(
            mutable_url_reason(
                "https://github.com/org/repo/blob/"
                "0123456789abcdef0123456789abcdef01234567/src/lib.rs"
            ),
            None,
        )

    def test_only_version_pinned_urls_are_content_eligible(self) -> None:
        cutoff = parse_utc("2026-04-13T23:59:59.999Z")
        self.assertTrue(
            immutable_historical_url(
                "https://github.com/org/repo/blob/"
                "0123456789abcdef0123456789abcdef01234567/src/lib.rs",
                cutoff,
            )
        )
        self.assertTrue(
            immutable_historical_url(
                "https://web.archive.org/web/20260401120000/https://example.com/",
                cutoff,
            )
        )
        self.assertFalse(
            immutable_historical_url(
                "https://web.archive.org/web/20260501120000/https://example.com/",
                cutoff,
            )
        )
        self.assertFalse(
            immutable_historical_url("https://example.com/old-paper", cutoff)
        )


class UsageTests(unittest.TestCase):
    def test_openrouter_supports_responses_api(self) -> None:
        self.assertIn("responses", MODEL_PROVIDERS["openrouter"]["routes"])

    def test_openrouter_supports_anthropic_messages_api(self) -> None:
        # Claude Code speaks the Anthropic Messages API; OpenRouter serves it at
        # /api/v1/messages and returns Anthropic-shaped usage.
        from gateway import extract_anthropic_usage, usage_extractor

        cfg = MODEL_PROVIDERS["openrouter"]
        self.assertIn("messages", cfg["routes"])
        self.assertNotIn("messages/count_tokens", cfg["routes"])
        self.assertIs(usage_extractor(cfg, "messages"), extract_anthropic_usage)
        self.assertIs(usage_extractor(cfg, "responses"), extract_usage)
        self.assertIn("anthropic-beta", cfg["passthrough"])
        self.assertIn("anthropic-version", cfg["passthrough"])

    def test_openrouter_messages_route_bills_anthropic_usage(self) -> None:
        # Same split as the direct Anthropic route: input+cache in message_start,
        # output in message_delta. total input 140, output 25, total 165;
        # billed = 165 - 0.9*40 (cache read) = 129.
        stream = (
            b'event: message_start\n'
            b'data: {"type":"message_start","message":{"usage":'
            b'{"input_tokens":100,"cache_read_input_tokens":40,'
            b'"cache_creation_input_tokens":0,"output_tokens":1}}}\n\n'
            b'event: message_delta\n'
            b'data: {"type":"message_delta","usage":{"output_tokens":25}}\n\n'
        )

        class OneChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream

        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api/v1/messages")
            self.assertEqual(request.headers["authorization"], "Bearer unused")
            self.assertNotIn("x-api-key", request.headers)
            self.assertEqual(request.headers["anthropic-beta"], "prompt-caching-2024-07-31")
            self.assertEqual(request.headers["anthropic-version"], "2023-06-01")
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=OneChunkStream(),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("openrouter-messages-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/openrouter/v1/messages",
                        json={"model": "anthropic/claude-opus-5", "stream": True},
                        headers={
                            # Claude Code's placeholder credential must never
                            # reach OpenRouter; the gateway swaps in its own.
                            "x-api-key": "testbed",
                            "anthropic-beta": "prompt-caching-2024-07-31",
                            "anthropic-version": "2023-06-01",
                        },
                    )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, stream)
                self.assertEqual(ledger.counts["model_tokens"], 129)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["provider"], "openrouter")
                self.assertEqual(event["model"], "anthropic/claude-opus-5")
                self.assertEqual(event["input_tokens"], 140)
                self.assertEqual(event["cached_input_tokens"], 40)
                self.assertEqual(event["output_tokens"], 25)
                self.assertEqual(event["billed_tokens"], 129)
                from gateway import pricing_for_request

                pricing = pricing_for_request("openrouter", "anthropic/claude-opus-5")
                self.assertEqual(pricing["output_per_mtok"], 25.0)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_summary_tracks_usage_without_a_completed_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = UsageLedger("unfinished-test", root)

            initial = json.loads((root / "summary.json").read_text())
            self.assertEqual(initial["usage"]["model_requests"], 0)
            self.assertEqual(initial["usage"]["normalized_usd"], 0.0)

            ledger.reserve("model_requests")
            ledger.add_model_tokens(42)
            ledger.add_model_usd(0.25)

            summary = json.loads((root / "summary.json").read_text())
            self.assertEqual(summary["usage"]["model_requests"], 1)
            self.assertEqual(summary["usage"]["model_tokens"], 42)
            self.assertEqual(summary["usage"]["normalized_usd"], 0.25)
            self.assertEqual(summary["usage"]["billed_usd"], 0.25)

    def test_shutdown_drain_flushes_cancelled_accounting_task(self) -> None:
        from gateway import _BACKGROUND_TASKS

        async def exercise(ledger: UsageLedger) -> None:
            async def pending_accounting() -> None:
                try:
                    await asyncio.Event().wait()
                finally:
                    ledger.add_model_tokens(17)
                    ledger.add_model_usd(0.125)

            task = asyncio.create_task(pending_accounting())
            _BACKGROUND_TASKS.add(task)
            task.add_done_callback(_BACKGROUND_TASKS.discard)
            await asyncio.sleep(0)
            await drain_background_tasks(timeout_seconds=0)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = UsageLedger("shutdown-test", root)
            asyncio.run(exercise(ledger))

            summary = json.loads((root / "summary.json").read_text())
            self.assertEqual(summary["usage"]["model_tokens"], 17)
            self.assertEqual(summary["usage"]["normalized_usd"], 0.125)
            self.assertEqual(summary["usage"]["billed_usd"], 0.125)

    def test_chatgpt_subscription_forwards_auth_and_normalizes_cost(self) -> None:
        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/backend-api/codex/responses")
            self.assertEqual(
                request.headers["authorization"],
                "Bearer subscription-access-token",
            )
            self.assertEqual(request.headers["chatgpt-account-id"], "account-1")
            self.assertEqual(
                request.headers["x-codex-turn-metadata"],
                "turn-metadata",
            )
            return httpx.Response(
                200,
                json={
                    "usage": {
                        "input_tokens": 10,
                        "output_tokens": 5,
                        "total_tokens": 15,
                    }
                },
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("chatgpt-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/chatgpt/v1/responses",
                        headers={
                            "authorization": "Bearer subscription-access-token",
                            "chatgpt-account-id": "account-1",
                            "x-codex-turn-metadata": "turn-metadata",
                        },
                        json={"model": "gpt-5.6-sol", "input": "test"},
                    )
                self.assertEqual(response.status_code, 200)
                event = canonical_event(directory, "model.accounting")
                summary = json.loads(
                    (Path(directory) / "summary.json").read_text()
                )
                self.assertEqual(event["provider"], "openai-chatgpt")
                self.assertIsNone(event["billed_usd"])
                self.assertGreater(event["normalized_usd"], 0)
                self.assertIsNone(summary["usage"]["billed_usd"])
                self.assertEqual(summary["usage"]["accounting_method"], "gateway")
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_chatgpt_subscription_rejects_missing_auth(self) -> None:
        async def upstream(_request: httpx.Request) -> httpx.Response:
            self.fail("unauthenticated subscription request reached upstream")

        model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        original_client = gateway.client
        gateway.client = model_client
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/model/chatgpt/v1/responses",
                    json={"model": "gpt-5.6-sol", "input": "test"},
                )
            self.assertEqual(response.status_code, 400)
            self.assertIn("authentication", response.json()["error"])
        finally:
            gateway.client = original_client


    def test_openai_usage_is_normalized(self) -> None:
        body = json.dumps(
            {
                "usage": {
                    "input_tokens": 20,
                    "input_tokens_details": {
                        "cached_tokens": 5,
                        "cache_write_tokens": 4,
                    },
                    "output_tokens": 7,
                    "output_tokens_details": {"reasoning_tokens": 3},
                    "total_tokens": 27,
                }
            }
        ).encode()
        self.assertEqual(
            extract_usage(body, "application/json"),
            {
                "input_tokens": 20,
                "cached_input_tokens": 5,
                "cache_write_input_tokens": 4,
                "output_tokens": 7,
                "reasoning_tokens": 3,
                "total_tokens": 27,
            },
        )

    def test_mislabeled_sse_usage_is_detected(self) -> None:
        stream = (
            b'event: response.completed\n'
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":20,"input_tokens_details":{"cached_tokens":5,'
            b'"cache_write_tokens":4},'
            b'"output_tokens":7,"output_tokens_details":{"reasoning_tokens":3},'
            b'"total_tokens":27}}}\n\n'
        )
        self.assertTrue(is_sse_body(stream, "application/json"))
        self.assertEqual(
            extract_usage(stream, "application/json"),
            {
                "input_tokens": 20,
                "cached_input_tokens": 5,
                "cache_write_input_tokens": 4,
                "output_tokens": 7,
                "reasoning_tokens": 3,
                "total_tokens": 27,
            },
        )

    def test_chatgpt_mislabeled_sse_is_streamed_and_accounted(self) -> None:
        stream = (
            b'event: response.created\n'
            b'data: {"type":"response.created","response":{"status":"in_progress"}}\n\n'
            b'event: response.completed\n'
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":20,"input_tokens_details":{"cached_tokens":5},'
            b'"output_tokens":7,"output_tokens_details":{"reasoning_tokens":3},'
            b'"total_tokens":27}}}\n\n'
        )

        class OneChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream

        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/backend-api/codex/responses")
            self.assertEqual(request.headers.get("authorization"), "Bearer subscription")
            return httpx.Response(
                200,
                # This reproduces the ChatGPT subscription response observed in
                # a real run: SSE framing with an application/json header.
                headers={"content-type": "application/json"},
                stream=OneChunkStream(),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("chatgpt-stream-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client = gateway.client
            original_ledger = gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/chatgpt/v1/responses",
                        headers={"authorization": "Bearer subscription"},
                        json={
                            "model": "gpt-5.6-sol",
                            "stream": True,
                        },
                    )
                self.assertEqual(response.content, stream)
                self.assertTrue(
                    response.headers["content-type"].startswith("text/event-stream")
                )
                # 27 total - 90% of 5 cached tokens = 22.5, rounded to 22.
                self.assertEqual(ledger.counts["model_tokens"], 22)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["accounting_method"], "gateway")
                self.assertEqual(event["provider"], "openai-chatgpt")
                self.assertEqual(event["total_tokens"], 27)
                self.assertEqual(event["cached_input_tokens"], 5)
                self.assertIsNone(event["billed_usd"])
                self.assertGreater(event["normalized_usd"], 0)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_streamed_model_response_is_forwarded_and_accounted(self) -> None:
        stream = (
            b'data: {"type":"response.reasoning_summary_text.delta",'
            b'"summary_index":0,"delta":"Checked the "}\n\n'
            b'data: {"type":"response.reasoning_summary_text.done",'
            b'"summary_index":0,"text":"Checked the constraints."}\n\n'
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":11,"output_tokens":4,"total_tokens":15}}}\n\n'
            b"data: [DONE]\n\n"
        )

        class OneChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream

        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/v1/responses")
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=OneChunkStream(),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("stream-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client = gateway.client
            original_ledger = gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/openai/v1/responses",
                        json={"model": "gpt-5.6-sol", "stream": True},
                    )
                self.assertEqual(response.content, stream)
                self.assertEqual(ledger.counts["model_tokens"], 15)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["accounting_method"], "gateway")
                self.assertEqual(event["total_tokens"], 15)
                self.assertEqual(event["status"], "success")
                timeline = canonical_events(
                    directory,
                    "model.request",
                    "model.reasoning",
                    "model.response",
                )
                self.assertEqual(
                    [event["kind"] for event in timeline],
                    ["model.request", "model.reasoning", "model.response"],
                )
                self.assertEqual(
                    [event["sequence"] for event in timeline],
                    sorted(event["sequence"] for event in timeline),
                )
                self.assertEqual(
                    timeline[0]["request"]["model"],
                    "gpt-5.6-sol",
                )
                self.assertEqual(
                    timeline[1]["text"],
                    "Checked the constraints.",
                )
                self.assertEqual(
                    timeline[2]["response"][0]["type"],
                    "response.reasoning_summary_text.delta",
                )
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_openrouter_kimi_reasoning_setting_is_preserved_and_logged(self) -> None:
        stream = (
            b'data: {"type":"response.reasoning.delta","delta":"Inspect "}\n\n'
            b'data: {"type":"response.reasoning.delta","delta":"the circuit."}\n\n'
            b'data: {"type":"response.output_text.delta","delta":"Done"}\n\n'
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":10,"output_tokens":5,"total_tokens":15}}}\n\n'
            b"data: [DONE]\n\n"
        )

        class OneChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream

        async def upstream(request: httpx.Request) -> httpx.Response:
            payload = json.loads(request.content)
            self.assertEqual(payload["model"], "moonshotai/kimi-k3")
            self.assertEqual(payload["reasoning"], {"effort": "high", "exclude": True})
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=OneChunkStream(),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("kimi-openrouter-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client = gateway.client
            original_ledger = gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/openrouter/v1/responses",
                        json={
                            "model": "moonshotai/kimi-k3",
                            "reasoning": {"effort": "high", "exclude": True},
                            "stream": True,
                        },
                    )
                self.assertEqual(response.content, stream)
                timeline = canonical_events(
                    directory,
                    "model.request",
                    "model.reasoning",
                    "model.response",
                )
                reasoning = [
                    event
                    for event in timeline
                    if event["kind"] == "model.reasoning"
                ]
                self.assertEqual(len(reasoning), 1)
                self.assertEqual(
                    reasoning[0]["source"],
                    "response.reasoning.delta",
                )
                self.assertEqual(reasoning[0]["text"], "Inspect the circuit.")
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_visible_reasoning_ignores_non_string_type_fields(self) -> None:
        events = gateway_module.extract_visible_reasoning_events(
            {
                "type": {"unexpected": "object"},
                "nested": {
                    "reasoning_content": "provider-visible reasoning",
                },
            }
        )
        self.assertEqual(
            events,
            [
                {
                    "source": "reasoning_content",
                    "text": "provider-visible reasoning",
                }
            ],
        )

    def test_openrouter_kimi_usage_survives_client_disconnect(self) -> None:
        stream = (
            b'data: {"type":"response.reasoning.delta","delta":"Inspect"}\n\n'
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":10,"output_tokens":5,"total_tokens":15}}}\n\n'
            b"data: [DONE]\n\n"
        )

        class TwoChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream[:70]
                yield stream[70:]

        async def upstream(request: httpx.Request) -> httpx.Response:
            payload = json.loads(request.content)
            self.assertEqual(payload["model"], "moonshotai/kimi-k3")
            self.assertNotIn("reasoning", payload)
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=TwoChunkStream(),
            )

        from gateway import _BACKGROUND_TASKS

        async def drive() -> None:
            scope = {
                "type": "http",
                "method": "POST",
                "path": "/model/openrouter/v1/responses",
                "headers": [(b"content-type", b"application/json")],
                "query_string": b"",
            }
            body = json.dumps(
                {"model": "moonshotai/kimi-k3", "stream": True}
            ).encode()
            events = [
                {"type": "http.request", "body": body, "more_body": False},
                {"type": "http.disconnect"},
            ]

            async def receive():
                return events.pop(0) if events else {"type": "http.disconnect"}

            async def send(_message):
                pass

            await app(scope, receive, send)
            for task in list(_BACKGROUND_TASKS):
                await task

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = UsageLedger("kimi-disconnect-test", root)
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                asyncio.run(drive())
                summary = json.loads((root / "summary.json").read_text())
                self.assertEqual(summary["usage"]["model_requests"], 1)
                self.assertEqual(summary["usage"]["model_tokens"], 15)
                self.assertGreater(summary["usage"]["billed_usd"], 0)
                event = canonical_event(root, "model.accounting")
                self.assertEqual(event["provider"], "openrouter")
                self.assertEqual(event["model"], "moonshotai/kimi-k3")
                self.assertEqual(event["total_tokens"], 15)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_openrouter_responses_route_uses_openrouter_upstream(self) -> None:
        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api/v1/responses")
            self.assertEqual(request.headers["authorization"], "Bearer unused")
            return httpx.Response(
                200,
                json={
                    "usage": {
                        "input_tokens": 8,
                        "output_tokens": 3,
                        "total_tokens": 11,
                    }
                },
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("openrouter-responses-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client = gateway.client
            original_ledger = gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/openrouter/v1/responses",
                        json={"model": "openai/gpt-5.6-sol", "input": "test"},
                    )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(ledger.counts["model_tokens"], 11)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["provider"], "openrouter")
                self.assertEqual(event["model"], "openai/gpt-5.6-sol")
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_unpriced_model_is_rejected_before_upstream(self) -> None:
        async def upstream(_request: httpx.Request) -> httpx.Response:
            self.fail("unpriced model request reached the upstream provider")

        model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        original_client = gateway.client
        gateway.client = model_client
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/model/openrouter/v1/responses",
                    json={"model": "vendor/unpriced-model", "input": "test"},
                )
            self.assertEqual(response.status_code, 400)
            self.assertIn("trusted pricing policy", response.json()["error"])
        finally:
            gateway.client = original_client

    def test_cached_input_is_discounted_from_the_budget(self) -> None:
        # total 110 with 90 cached -> billed 110 - 0.9*90 = 29 charged to budget,
        # but the event still records the full raw usage for observability.
        stream = (
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":100,"input_tokens_details":{"cached_tokens":90},'
            b'"output_tokens":10,"total_tokens":110}}}\n\n'
            b"data: [DONE]\n\n"
        )

        class OneChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream

        async def upstream(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=OneChunkStream(),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("cache-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client = gateway.client
            original_ledger = gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    client.post(
                        "/model/openai/v1/responses",
                        json={"model": "gpt-5.6-sol", "stream": True},
                    )
                self.assertEqual(ledger.counts["model_tokens"], 29)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["total_tokens"], 110)
                self.assertEqual(event["cached_input_tokens"], 90)
                self.assertEqual(event["billed_tokens"], 29)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_astra_proxy_records_cache_write_and_long_context_tier(self) -> None:
        stream = (
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":300000,"input_tokens_details":'
            b'{"cached_tokens":100000,"cache_write_tokens":50000},'
            b'"output_tokens":20000,"output_tokens_details":'
            b'{"reasoning_tokens":8000},"total_tokens":320000}}}\n\n'
            b"data: [DONE]\n\n"
        )

        class OneChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream

        async def upstream(request: httpx.Request) -> httpx.Response:
            payload = json.loads(request.content)
            self.assertEqual(payload["model"], "gpt-6-astra")
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=OneChunkStream(),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("astra-accounting-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client = gateway.client
            original_ledger = gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/openai/v1/responses",
                        json={
                            "model": "gpt-6-astra",
                            "input": "test",
                            "stream": True,
                        },
                    )
                self.assertEqual(response.status_code, 200)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["cache_write_input_tokens"], 50_000)
                self.assertEqual(event["reasoning_tokens"], 8_000)
                self.assertEqual(event["pricing_tier"], "long_context")
                self.assertEqual(event["normalized_usd"], 5.95)
                self.assertEqual(event["billed_tokens"], 242_500)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_search_query_is_logged_to_web_events(self) -> None:
        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/search")
            return httpx.Response(200, json={"results": []})

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("search-log-test", Path(directory))
            web_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            gateway.client = web_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/web/search", json={"query": "Cuccaro adder Toffoli count"}
                    )
                self.assertEqual(response.status_code, 200)
                event = canonical_event(directory, "web.accounting")
                self.assertEqual(event["operation"], "search")
                self.assertEqual(event["query"], "Cuccaro adder Toffoli count")
                timeline = canonical_events(
                    directory,
                    "web.search.request",
                    "web.search.response",
                )
                self.assertEqual(
                    [item["kind"] for item in timeline],
                    ["web.search.request", "web.search.response"],
                )
                self.assertEqual(
                    timeline[0]["query"],
                    "Cuccaro adder Toffoli count",
                )
                self.assertEqual(timeline[1]["response"]["results"], [])
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_search_filters_leaked_future_and_mutable_results(self) -> None:
        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/search")
            payload = json.loads(request.content)
            self.assertEqual(
                payload["endPublishedDate"], "2026-07-05T23:59:59.999Z"
            )
            self.assertNotIn("endCrawlDate", payload)
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "url": "https://example.com/old-paper",
                            "publishedDate": "2025-01-10",
                            "title": "Allowed",
                            "highlights": ["body may have changed"],
                        },
                        {
                            "url": "https://github.com/trailofbits/trailmix",
                            "publishedDate": None,
                            "title": "Mutable repository",
                        },
                        {
                            "url": "https://arxiv.org/html/2608.12345",
                            "publishedDate": None,
                            "entities": [
                                {"properties": {"date": "2026-08-01"}}
                            ],
                            "title": "Future paper",
                        },
                    ]
                },
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("historical-filter-test", Path(directory))
            web_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            original_targets = gateway.allowed_fetch_targets
            gateway.client = web_client
            gateway.ledger = ledger
            gateway.allowed_fetch_targets = {}
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/web/search", json={"query": "historical research"}
                    )
                self.assertEqual(response.status_code, 200)
                body = response.json()
                self.assertEqual(
                    [item["url"] for item in body["results"]],
                    ["https://example.com/old-paper"],
                )
                self.assertNotIn("highlights", body["results"][0])
                self.assertEqual(
                    body["results"][0]["testbedHistorical"]["contentAccess"],
                    "metadata-only",
                )
                self.assertEqual(
                    body["testbedPolicy"]["rejectedResults"],
                    {"mutable_git_url": 1, "post_cutoff": 1},
                )
                self.assertNotIn(
                    "https://example.com/old-paper",
                    gateway.allowed_fetch_targets,
                )
                rejections = canonical_events(directory, "web.rejection")
                self.assertEqual(
                    {item["reason"] for item in rejections},
                    {"mutable_git_url", "post_cutoff"},
                )
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger
                gateway.allowed_fetch_targets = original_targets

    def test_fetch_revalidates_approved_result(self) -> None:
        url = (
            "https://github.com/org/repo/blob/"
            "0123456789abcdef0123456789abcdef01234567/src/lib.rs"
        )

        async def upstream(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/search":
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {
                                "url": url,
                                "publishedDate": "2025-01-10",
                                "title": "Allowed",
                            }
                        ]
                    },
                )
            self.assertEqual(request.url.path, "/contents")
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "url": url,
                            "publishedDate": "2025-01-10",
                            "text": "Historical content",
                        }
                    ]
                },
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("historical-fetch-test", Path(directory))
            web_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            original_targets = gateway.allowed_fetch_targets
            gateway.client = web_client
            gateway.ledger = ledger
            gateway.allowed_fetch_targets = {}
            try:
                with TestClient(app) as client:
                    search = client.post("/web/search", json={"query": "old paper"})
                    self.assertEqual(search.status_code, 200)
                    fetched = client.post("/web/fetch", json={"url": url})
                self.assertEqual(fetched.status_code, 200)
                policy = fetched.json()["testbedPolicy"]
                self.assertEqual(policy["mode"], "strict-historical")
                self.assertRegex(policy["contentSha256"], r"^[0-9a-f]{64}$")
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger
                gateway.allowed_fetch_targets = original_targets

    def test_fetch_rejects_changed_publication_metadata(self) -> None:
        url = (
            "https://github.com/org/repo/blob/"
            "0123456789abcdef0123456789abcdef01234567/src/lib.rs"
        )

        async def upstream(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/search":
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {"url": url, "publishedDate": "2025-01-10"}
                        ]
                    },
                )
            return httpx.Response(
                200,
                json={
                    "results": [
                        {"url": url, "publishedDate": "2025-01-11", "text": "changed"}
                    ]
                },
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("historical-fetch-change-test", Path(directory))
            web_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            original_targets = gateway.allowed_fetch_targets
            gateway.client = web_client
            gateway.ledger = ledger
            gateway.allowed_fetch_targets = {}
            try:
                with TestClient(app) as client:
                    self.assertEqual(
                        client.post(
                            "/web/search", json={"query": "old paper"}
                        ).status_code,
                        200,
                    )
                    fetched = client.post("/web/fetch", json={"url": url})
                self.assertEqual(fetched.status_code, 400)
                self.assertIn(
                    "publication metadata differs",
                    fetched.json()["error"],
                )
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger
                gateway.allowed_fetch_targets = original_targets

    def test_anthropic_stream_usage_is_merged_and_billed(self) -> None:
        # Anthropic splits usage across events: input+cache in message_start,
        # output in message_delta. total input = 100+40 = 140, output = 25,
        # total = 165; billed = 165 - 0.9*40(cache_read) = 129.
        stream = (
            b'event: message_start\n'
            b'data: {"type":"message_start","message":{"usage":'
            b'{"input_tokens":100,"cache_read_input_tokens":40,'
            b'"cache_creation_input_tokens":0,"output_tokens":1}}}\n\n'
            b'event: message_delta\n'
            b'data: {"type":"message_delta","usage":{"output_tokens":25}}\n\n'
        )

        class OneChunkStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream

        async def upstream(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/v1/messages")
            self.assertEqual(request.headers.get("x-api-key"), "unused")
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=OneChunkStream(),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("anthropic-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/model/anthropic/v1/messages",
                        json={"model": "claude-opus-5", "stream": True},
                    )
                self.assertEqual(response.content, stream)
                self.assertEqual(ledger.counts["model_tokens"], 129)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["provider"], "anthropic")
                self.assertEqual(event["input_tokens"], 140)
                self.assertEqual(event["cached_input_tokens"], 40)
                self.assertEqual(event["output_tokens"], 25)
                self.assertEqual(event["total_tokens"], 165)
                self.assertEqual(event["billed_tokens"], 129)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_usage_captured_when_client_disconnects_midstream(self) -> None:
        # The usage event is the LAST chunk. Simulate the agent disconnecting
        # immediately; the pump must still drain upstream and account the tokens.
        stream = (
            b'data: {"type":"response.output_text.delta","delta":"hi"}\n\n'
            b'data: {"type":"response.completed","response":{"usage":'
            b'{"input_tokens":10,"output_tokens":5,"total_tokens":15}}}\n\n'
            b"data: [DONE]\n\n"
        )

        class TwoChunk(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield stream[:60]
                yield stream[60:]

        async def upstream(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=TwoChunk(),
            )

        from gateway import _BACKGROUND_TASKS

        async def drive() -> None:
            scope = {
                "type": "http",
                "method": "POST",
                "path": "/model/openai/v1/responses",
                "headers": [(b"content-type", b"application/json")],
                "query_string": b"",
            }
            body = json.dumps({"model": "gpt-5.6-sol", "stream": True}).encode()
            events = [
                {"type": "http.request", "body": body, "more_body": False},
                {"type": "http.disconnect"},
            ]

            async def receive():
                return events.pop(0) if events else {"type": "http.disconnect"}

            async def send(_message):  # agent disconnected; drop everything
                pass

            await app(scope, receive, send)
            for task in list(_BACKGROUND_TASKS):  # let the pump finish accounting
                await task

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("disconnect-test", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                asyncio.run(drive())
                # 15 total, no cache -> billed 15, captured despite the disconnect.
                self.assertEqual(ledger.counts["model_tokens"], 15)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["total_tokens"], 15)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_anthropic_usage_captured_when_client_disconnects(self) -> None:
        # Anthropic sends output tokens LATE (message_delta), so a partial
        # capture on disconnect would lose them. The pump must drain both events.
        stream = (
            b'event: message_start\n'
            b'data: {"type":"message_start","message":{"usage":'
            b'{"input_tokens":100,"cache_read_input_tokens":0,'
            b'"cache_creation_input_tokens":0,"output_tokens":1}}}\n\n'
            b'event: message_delta\n'
            b'data: {"type":"message_delta","usage":{"output_tokens":20}}\n\n'
        )

        class TwoChunk(httpx.AsyncByteStream):
            async def __aiter__(self):
                half = stream.index(b"event: message_delta")
                yield stream[:half]
                yield stream[half:]

        async def upstream(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=TwoChunk(),
            )

        from gateway import _BACKGROUND_TASKS

        async def drive() -> None:
            scope = {
                "type": "http",
                "method": "POST",
                "path": "/model/anthropic/v1/messages",
                "headers": [(b"content-type", b"application/json")],
                "query_string": b"",
            }
            body = json.dumps({"model": "claude-opus-5", "stream": True}).encode()
            events = [
                {"type": "http.request", "body": body, "more_body": False},
                {"type": "http.disconnect"},
            ]

            async def receive():
                return events.pop(0) if events else {"type": "http.disconnect"}

            async def send(_message):
                pass

            await app(scope, receive, send)
            for task in list(_BACKGROUND_TASKS):
                await task

        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("anthropic-disconnect", Path(directory))
            model_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            original_client, original_ledger = gateway.client, gateway.ledger
            gateway.client = model_client
            gateway.ledger = ledger
            try:
                asyncio.run(drive())
                # input 100 + output 20 = 120, captured despite the disconnect.
                self.assertEqual(ledger.counts["model_tokens"], 120)
                event = canonical_event(directory, "model.accounting")
                self.assertEqual(event["provider"], "anthropic")
                self.assertEqual(event["output_tokens"], 20)
                self.assertEqual(event["total_tokens"], 120)
            finally:
                gateway.client = original_client
                gateway.ledger = original_ledger

    def test_gzipped_anthropic_usage_is_decoded(self) -> None:
        # The real bug: a gzip-compressed SSE body parsed to zero tokens.
        # extract_anthropic_usage must decompress it.
        import gzip as _gzip
        from gateway import extract_anthropic_usage

        sse = (
            b'event: message_start\n'
            b'data: {"type":"message_start","message":{"usage":'
            b'{"input_tokens":50,"cache_read_input_tokens":10,'
            b'"cache_creation_input_tokens":0,"output_tokens":1}}}\n\n'
            b'event: message_delta\n'
            b'data: {"type":"message_delta","usage":{"output_tokens":7}}\n\n'
        )
        usage = extract_anthropic_usage(_gzip.compress(sse), "text/event-stream")
        self.assertEqual(usage["input_tokens"], 60)  # 50 + 10 cache
        self.assertEqual(usage["cached_input_tokens"], 10)
        self.assertEqual(usage["output_tokens"], 7)
        self.assertEqual(usage["total_tokens"], 67)

    def test_usd_cost_and_budget_cap(self) -> None:
        from gateway import pricing_for_request, request_usd

        pricing = pricing_for_request("anthropic", "claude-opus-5")

        # prices: input $5/M, cached $0.5/M, output $25/M
        self.assertAlmostEqual(
            request_usd({"input_tokens": 1_000_000, "cached_input_tokens": 0,
                         "output_tokens": 0}, pricing), 5.0, places=6)
        # 200k non-cached input @5 + 800k cache @0.5 + 40k output @25 (per M)
        # = 1.0 + 0.4 + 1.0 = 2.4
        self.assertAlmostEqual(
            request_usd({"input_tokens": 1_000_000, "cached_input_tokens": 800_000,
                         "output_tokens": 40_000}, pricing), 2.4, places=6)
        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("usd-test", Path(directory))  # usd_limit=1.0 (env)
            ledger.reserve("model_requests")          # ok: $0 spent
            ledger.add_model_usd(1.0)                 # reach the cap
            with self.assertRaises(BudgetExceeded):
                ledger.reserve("model_requests")      # over the USD cap

    def test_astra_cache_write_and_long_context_accounting(self) -> None:
        from gateway import (
            pricing_for_request,
            request_budget_tokens,
            request_pricing_rates,
            request_usd,
        )

        pricing = pricing_for_request("openai", "gpt-6-astra")
        subscription_pricing = pricing_for_request(
            "openai-chatgpt",
            "gpt-6-astra",
        )
        base_usage = {
            "input_tokens": 200_000,
            "cached_input_tokens": 80_000,
            "cache_write_input_tokens": 20_000,
            "output_tokens": 10_000,
            "reasoning_tokens": 4_000,
            "total_tokens": 210_000,
        }
        # 100k ordinary @ $10/M + 80k cache read @ $1/M
        # + 20k cache write @ $12.50/M + 10k output @ $50/M.
        self.assertAlmostEqual(request_usd(base_usage, pricing), 1.83, places=6)
        self.assertAlmostEqual(
            request_usd(base_usage, subscription_pricing),
            1.83,
            places=6,
        )
        self.assertEqual(request_pricing_rates(base_usage, pricing)[1], "base")

        long_usage = {
            "input_tokens": 300_000,
            "cached_input_tokens": 100_000,
            "cache_write_input_tokens": 50_000,
            "output_tokens": 20_000,
            "reasoning_tokens": 8_000,
            "total_tokens": 320_000,
        }
        # The entire request uses Astra's >272k tier:
        # 150k @ $20/M + 100k @ $2/M + 50k @ $25/M + 20k @ $75/M.
        self.assertAlmostEqual(request_usd(long_usage, pricing), 5.95, places=6)
        self.assertEqual(
            request_pricing_rates(long_usage, pricing)[1],
            "long_context",
        )
        self.assertEqual(
            request_pricing_rates({"input_tokens": 272_000}, pricing)[1],
            "base",
        )
        self.assertEqual(
            request_pricing_rates({"input_tokens": 272_001}, pricing)[1],
            "long_context",
        )

        # Cost-proxy tokens use relative input rates: ordinary 20 + cached 6
        # + cache writes 25 + output 10 = 61.
        self.assertEqual(
            request_budget_tokens(
                {
                    "input_tokens": 100,
                    "cached_input_tokens": 60,
                    "cache_write_input_tokens": 20,
                    "output_tokens": 10,
                    "total_tokens": 110,
                },
                pricing,
            ),
            61,
        )

    def test_request_budget_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("budget-test", Path(directory))
            ledger.reserve("searches")
            ledger.reserve("searches")
            with self.assertRaises(BudgetExceeded):
                ledger.reserve("searches")

    def test_status_reports_used_limits_and_remaining_budgets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("status-test", Path(directory))
            ledger.reserve("searches")
            ledger.reserve("model_requests")
            ledger.add_model_tokens(20)
            ledger.add_model_usd(0.25)
            status = ledger.status()
            self.assertEqual(status["usage"]["searches"], 1)
            self.assertEqual(status["limits"]["searches"], 2)
            self.assertEqual(status["remaining"]["searches"], 1)
            self.assertEqual(status["remaining"]["model_tokens"], 80)
            self.assertEqual(status["remaining"]["normalized_usd"], 0.75)

    def test_usage_event_and_summary_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = UsageLedger("logging-test", root)
            ledger.reserve("fetches")
            ledger.record(
                "web",
                {"operation": "fetch", "duration_ms": 5, "status": "success"},
            )
            event = canonical_event(root, "web.accounting")
            summary = json.loads((root / "summary.json").read_text())
            self.assertEqual(event["run_id"], "logging-test")
            self.assertEqual(summary["usage"]["fetches"], 1)

    def test_internal_event_is_authenticated_and_snapshots_usage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = UsageLedger("collector-test", root)
            ledger.add_model_usd(0.75)
            token = ledger.event_token
            original_ledger = gateway.ledger
            gateway.ledger = ledger
            try:
                document = {
                    "run_id": "collector-test",
                    "source": "evaluator",
                    "kind": "evaluation.completed",
                    "observed_at": "2026-09-05T01:02:03Z",
                    "event_id": "evaluation:1",
                    "data": {
                        "operation": "score",
                        "status": "ok",
                        "score": 42,
                        "best_score": 42,
                        "submissions_used": 1,
                        "submissions_limit": 10,
                    },
                }
                with TestClient(app) as client:
                    denied = client.post("/internal/events", json=document)
                    accepted = client.post(
                        "/internal/events",
                        headers={"x-dungeness-event-token": token},
                        json=document,
                    )
                    duplicate = client.post(
                        "/internal/events",
                        headers={"x-dungeness-event-token": token},
                        json=document,
                    )
                self.assertEqual(denied.status_code, 403)
                self.assertTrue(accepted.json()["accepted"])
                self.assertTrue(duplicate.json()["duplicate"])
                event = canonical_event(root, "evaluation.completed")
                self.assertEqual(event["cumulative_usage"]["normalized_usd"], 0.75)
                summary = json.loads((root / "summary.json").read_text())
                self.assertEqual(summary["evaluation"]["best_score"], 42)
                self.assertEqual(summary["evaluation"]["submissions_used"], 1)
                self.assertFalse((root / ".event-token").exists())
            finally:
                gateway.ledger = original_ledger

    def test_token_limit_blocks_the_next_model_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("token-test", Path(directory))
            ledger.add_model_tokens(101)
            with self.assertRaises(BudgetExceeded):
                ledger.reserve("model_requests")


class InstrumentationTests(unittest.TestCase):
    def test_agent_controlled_model_name_is_bounded(self) -> None:
        self.assertEqual(len(bounded_model_name("x" * 1000)), 256)
        self.assertEqual(bounded_model_name({"not": "a string"}), "unknown")

    def test_request_ids_are_bounded_and_sanitized(self) -> None:
        self.assertEqual(safe_request_id("agent-request_1"), "agent-request_1")
        generated = safe_request_id("contains spaces and ?query=data")
        self.assertRegex(generated, r"^[a-f0-9]{32}$")

    def test_metrics_have_bounded_labels_and_budget_gauges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = UsageLedger("metrics-test", Path(directory))
            registry = Metrics()
            registry.observe_http("GET", "/healthz", 200, 0.125)
            rendered = registry.render(ledger)
            self.assertIn("testbed_gateway_http_requests_total", rendered)
            self.assertIn('route="/healthz"', rendered)
            self.assertIn("testbed_gateway_budget_limit", rendered)

    def test_dynamic_paths_do_not_become_metric_labels(self) -> None:
        self.assertEqual(
            instrumentation_route("/model/openai/v1/agent-controlled"),
            "/model/openai/v1/{operation}",
        )
        self.assertEqual(instrumentation_route("/arbitrary/agent/path"), "unmatched")

    def test_operational_events_are_persisted_as_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"TESTBED_USAGE_DIR": directory}):
                log_event("unit_test_event", request_id="request-1")
            event = canonical_event(directory, "gateway.unit_test_event")
            self.assertEqual(event["request_id"], "request-1")


if __name__ == "__main__":
    unittest.main()
