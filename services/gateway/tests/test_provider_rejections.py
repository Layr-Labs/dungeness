"""Provider rejections must not poison accounting or erase completed work."""
import asyncio
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway  # Configure an offline gateway before importing it.
import gateway
import gateway_pricing
from gateway_runtime import Gateway, pre_generation_rejection
from gateway_security import safe_provider_error

ERROR = {"type": "error", "error": {"type": "rate_limit_error", "message": "private-provider-message"},
         "request_id": "private-upstream-id"}


class RejectionContractTests(unittest.TestCase):
    def test_only_supported_complete_rejection_envelopes_settle_zero(self):
        for provider in ("anthropic", "claude-subscription"):
            for envelope in (ERROR, {"error": ERROR["error"]}):
                with self.subTest(provider=provider, envelope=envelope):
                    self.assertEqual(pre_generation_rejection(json.dumps(envelope).encode(),
                        "application/json; charset=utf-8", 429, provider), "provider_rate_limited")
        cases = [
            (200, ERROR, "application/json", "anthropic"),
            (500, ERROR, "application/json", "anthropic"),
            (429, ERROR, "text/event-stream", "anthropic"),
            *[(429, ERROR, "application/json", p) for p in ("openrouter", "openai", "openai-chatgpt", "unknown")],
            *[(429, {**ERROR, key: value}, "application/json", "anthropic") for key, value in (
                ("usage", {"input_tokens": 10}), ("content", []), ("output", []),
                ("type", "message"), ("request_id", {}), ("extension", True))],
            *[(429, {**ERROR, "error": e}, "application/json", "anthropic") for e in (
                "invalid", {"type": "api_error", "message": "failed"},
                {**ERROR["error"], "usage": {"output_tokens": 1}},
                {**ERROR["error"], "details": {"error_code": "unknown"}},
                {**ERROR["error"], "details": {"usage": 1}},
                {**ERROR["error"], "details": None}, {"type": "rate_limit_error", "message": None})],
        ]
        for status, body, mime, provider in cases:
            with self.subTest(status=status, body=body, mime=mime, provider=provider):
                self.assertIsNone(pre_generation_rejection(json.dumps(body).encode(), mime, status, provider))
        for body in (b'{"error":', b'null', b'[]', b'\xff', b'<html>429</html>'):
            self.assertIsNone(pre_generation_rejection(body, "application/json", 429, "anthropic"))

    def test_retry_delay_is_sanitized_and_requires_settled_retryable_error(self):
        for raw, expected in (("2", "2"), ("00030", "30"), ("0", "0"), ("604800", "604800"),
                              ("604801", None), ("-1", None), ("0.2", None), ("secret", None),
                              ("2\r\nx-secret: credential", None), ("9" * 10000, None), (None, None)):
            reply = safe_provider_error(429, "request-fixture", accounting_complete=True, retry_after=raw)
            self.assertEqual(reply.headers.get("retry-after"), expected)
        for complete, limited in ((False, False), (True, True)):
            reply = safe_provider_error(429, "request-fixture", accounting_complete=complete,
                                        retry_after="2", usage_limit_reached=limited)
            self.assertNotIn("retry-after", reply.headers)
            self.assertEqual(reply.headers["x-should-retry"], "false")


class ProviderRejectionIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, provider="claude-subscription", *, streaming=False, error=None,
                       status=429, interrupted=False, already_incomplete=False, max_requests=20):
        error = ERROR if error is None else error
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": tmp,
            "DUNGENESS_ALLOWED_MODELS": json.dumps([[provider, "claude-test"]]),
            "MAX_MODEL_REQUESTS": str(max_requests), "MAX_MODEL_TOKENS": "100000", "MAX_MODEL_USD": "1",
            "DUNGENESS_CREDENTIALS_FILE": str(Path(tmp) / "credentials.json"),
        }), patch.object(gateway_pricing, "MODEL_PRICING", [{
            "provider": provider, "request_models": ["claude-test"], "upstream_id": "anthropic/claude-test",
            "input_per_mtok": 5, "output_per_mtok": 25,
            "cached_read_per_mtok": .5, "cache_write_per_mtok": 6.25,
        }]):
            credentials = Path(tmp) / "credentials.json"
            credentials.write_text(json.dumps({"ANTHROPIC_API_KEY": "synthetic-private-token", "CLAUDE_ACCESS_TOKEN": "synthetic-private-token",
                                              "CLAUDE_ACCESS_TOKEN_EXPIRES_AT": "2030-01-01T00:00:00Z"}))
            credentials.chmod(0o600)
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []
            async def upstream(request):
                calls.append(request)
                if len(calls) == 2:
                    if already_incomplete:
                        runtime.ledger.model_accounting_incomplete = True
                    if interrupted:
                        class PartialError(httpx.AsyncByteStream):
                            async def __aiter__(self):
                                yield json.dumps(error).encode()
                                raise httpx.RemoteProtocolError("private-transport-message")
                        return httpx.Response(status, stream=PartialError(), headers={"content-type": "application/json"})
                    return httpx.Response(status, json=error, headers={"retry-after": "7", "x-private": "secret"})
                if streaming:
                    class Stream(httpx.AsyncByteStream):
                        async def __aiter__(self):
                            yield b'event: message_start\ndata: {"type":"message_start","message":{"usage":{"input_tokens":100,"output_tokens":0}}}\n\n'
                            await asyncio.sleep(0)
                            yield b'event: message_delta\ndata: {"type":"message_delta","usage":{"output_tokens":5}}\n\n'
                            yield b'event: message_stop\ndata: {"type":"message_stop"}\n\n'
                    return httpx.Response(200, stream=Stream(), headers={"content-type": "text/event-stream"})
                return httpx.Response(200, json={"type": "message", "content": [],
                                               "usage": {"input_tokens": 100, "output_tokens": 5}})
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app), base_url="http://gateway") as client:
                        payload = {"model": "claude-test", "max_tokens": 20, "stream": streaming,
                                   "messages": [{"role": "user", "content": "synthetic fixture"}]}
                        first = await client.post(f"/model/{provider}/v1/messages", json=payload)
                        self.assertEqual(first.status_code, 200, first.text)
                        rejected = await client.post(f"/model/{provider}/v1/messages", json=payload)
                        # No hidden inference retries, even for a confirmed rate limit.
                        self.assertEqual(len(calls), 2)
                        self.assertEqual(runtime.ledger.model_inflight, {})
                        self.assertEqual(runtime.ledger.model_token_inflight, {})
                        last = await client.post(f"/model/{provider}/v1/messages", json=payload)
                events = test_gateway.canonical_events(tmp, "model.accounting")
                summary = json.loads((Path(tmp) / "summary.json").read_text())
                self.assertGreater(events[0]["normalized_usd"], 0)
                self.assertNotIn("private-provider-message", rejected.text)
                self.assertNotIn("private-upstream-id", rejected.text)
                self.assertNotIn("private-transport-message", rejected.text)
                self.assertNotIn("x-private", rejected.headers)
                self.assertNotIn("synthetic-private-token", (Path(tmp) / "events.jsonl").read_text())
                return rejected, last, events, summary, len(calls)
            finally:
                await runtime.client.aclose()

    async def test_success_rate_limit_success_preserves_costs_json_and_streaming(self):
        for provider in ("anthropic", "claude-subscription"):
            for streaming in (False, True):
                with self.subTest(provider=provider, streaming=streaming):
                    reply, last, events, summary, calls = await self.exercise(provider, streaming=streaming)
                    self.assertEqual(reply.status_code, 429)
                    error = reply.json()["error"]
                    self.assertEqual(error["code"], "provider_rate_limited")
                    self.assertEqual(error["run_action"], "continue")
                    self.assertTrue(error["retryable"])
                    self.assertTrue(error["upstream_request_sent"])
                    self.assertTrue(error["accounting_complete"])
                    self.assertTrue(error["request_id"])
                    self.assertEqual(reply.headers["retry-after"], "7")
                    self.assertEqual(reply.headers["x-should-retry"], "true")
                    self.assertEqual(last.status_code, 200, last.text)
                    self.assertEqual(calls, 3)
                    self.assertEqual(len(events), 3)
                    self.assertEqual(events[1]["accounting_basis"], "provider_rejected_before_generation")
                    self.assertEqual(events[1]["status"], "provider_error")
                    self.assertEqual(events[1]["total_tokens"], 0)
                    self.assertEqual(events[1]["normalized_usd"], 0)
                    self.assertAlmostEqual(summary["usage"]["normalized_usd"],
                                           events[0]["normalized_usd"] + events[2]["normalized_usd"])
                    self.assertEqual(summary["usage"]["model_accounting_state"], "settled")

    async def test_ambiguous_and_partial_responses_still_stop_and_preserve_prior_cost(self):
        for options in ({"error": {"error": {"type": "api_error", "message": "unknown"}}},
                        {"status": 500}, {"interrupted": True}, {"already_incomplete": True}):
            with self.subTest(options=options):
                reply, last, events, summary, calls = await self.exercise(**options)
                diagnostic = reply.json().get("diagnostic", reply.json()["error"])
                self.assertEqual(diagnostic["run_action"], "stop")
                self.assertFalse(diagnostic["retryable"])
                self.assertEqual(reply.headers["x-should-retry"], "false")
                self.assertEqual(last.status_code, 429)
                self.assertEqual(calls, 2)
                self.assertEqual(summary["usage"]["model_accounting_state"], "incomplete")
                self.assertGreaterEqual(summary["usage"]["normalized_usd"], events[0]["normalized_usd"])

    async def test_explicit_provider_spend_cap_does_not_request_blind_retry(self):
        error = {**ERROR, "error": {**ERROR["error"], "details": {"error_code": "enforced_spend_limit_reached"}}}
        reply, last, events, summary, _ = await self.exercise(error=error)
        self.assertEqual(reply.json()["error"]["code"], "provider_usage_limit_reached")
        self.assertEqual(reply.json()["error"]["action"], "check_provider_limits")
        self.assertFalse(reply.json()["error"]["retryable"])
        self.assertEqual(events[1]["normalized_usd"], 0)
        self.assertEqual(summary["usage"]["model_accounting_state"], "settled")

    async def test_rate_limit_with_recorded_usage_keeps_the_charge(self):
        reply, last, events, summary, _ = await self.exercise(error={
            **ERROR, "usage": {"input_tokens": 20, "output_tokens": 5}})
        self.assertEqual(reply.status_code, 429)
        self.assertEqual(last.status_code, 200)
        self.assertEqual(events[1]["accounting_basis"], "provider_usage")
        self.assertGreater(events[1]["normalized_usd"], 0)
        self.assertAlmostEqual(summary["usage"]["normalized_usd"],
                               sum(event["normalized_usd"] for event in events))

    async def test_zero_cost_rejections_still_count_toward_request_limit(self):
        reply, last, events, summary, calls = await self.exercise(max_requests=2)
        self.assertEqual(reply.status_code, 429)
        self.assertTrue(reply.json()["error"]["accounting_complete"])
        self.assertEqual(last.status_code, 429)
        self.assertEqual(calls, 2)
        self.assertEqual(summary["usage"]["model_accounting_state"], "settled")
        diagnostic = last.json().get("diagnostic", last.json()["error"])
        self.assertEqual(diagnostic["run_action"], "stop")

    async def test_anthropic_validation_error_with_request_id_is_correctable(self):
        reply, last, events, summary, _ = await self.exercise(status=400, error={
            **ERROR, "error": {"type": "invalid_request_error", "message": "invalid input"}})
        self.assertEqual(reply.json()["error"]["run_action"], "continue")
        self.assertFalse(reply.json()["error"]["retryable"])
        self.assertEqual(last.status_code, 200)
        self.assertEqual(events[1]["accounting_basis"], "input_rejected_before_generation")
