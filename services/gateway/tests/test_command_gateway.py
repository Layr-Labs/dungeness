"""Generic harness gateway tests against an in-process mock provider."""
import asyncio
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway  # Establish the same offline gateway environment.
import gateway
import gateway_pricing
from gateway_runtime import Gateway


class CommandGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_interrupted_stream_reports_safe_category_and_preserves_accounting_rules(self):
        for has_usage in (False, True):
            with self.subTest(has_usage=has_usage), tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
                "TESTBED_USAGE_DIR": temp, "DUNGENESS_ALLOWED_MODELS": '[["openai","gpt-5.6-sol"]]',
                "MAX_MODEL_REQUESTS": "20", "MAX_MODEL_TOKENS": "100000",
            }):
                runtime = Gateway()
                await runtime.client.aclose()
                class Stream(httpx.AsyncByteStream):
                    async def __aiter__(self):
                        yield b'data: {"type":"response.in_progress"}\n\n'
                        if has_usage:
                            yield b'data: {"type":"response.completed","response":{"usage":{"input_tokens":100,"output_tokens":10}}}\n\n'
                        raise httpx.RemoteProtocolError("private-token-canary at https://private-upstream")

                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(
                    lambda request: httpx.Response(200, stream=Stream(), headers={"content-type":"text/event-stream"})))
                try:
                    with patch.object(gateway, "gateway", runtime):
                        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                base_url="http://gateway") as client:
                            payload = {"model":"gpt-5.6-sol", "input":"fixture", "stream":True}
                            response = await client.post("/model/openai/v1/responses", json=payload)
                            self.assertEqual(response.status_code,200)
                            next_response = await client.post("/model/openai/v1/responses", json=payload)
                            self.assertEqual(next_response.status_code, 200 if has_usage else 429)
                    contents = (Path(temp)/"events.jsonl").read_text()
                    receipts = [e['data'] for e in map(json.loads,contents.splitlines()) if e['kind']=='model.accounting']
                    self.assertEqual(receipts[0]['failure_category'],'upstream_protocol_error')
                    self.assertEqual(receipts[0]['failure_stage'],'upstream_stream')
                    self.assertEqual(receipts[0]['status'],'stream_interrupted')
                    self.assertEqual(receipts[0]['accounting_method'],'gateway' if has_usage else 'unavailable')
                    self.assertEqual(runtime.ledger.model_accounting_incomplete,not has_usage)
                    summary = json.loads((Path(temp)/'summary.json').read_text())
                    self.assertEqual(summary['usage']['model_accounting_state'],
                                     'settled' if has_usage else 'incomplete')
                    self.assertNotIn('private-token-canary',contents)
                    self.assertNotIn('private-upstream',contents)
                finally:
                    await runtime.client.aclose()

    async def test_explicit_input_rejection_settles_zero_and_allows_corrected_request(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp, "DUNGENESS_ALLOWED_MODELS": '[["openai","gpt-5.6-sol"]]',
            "MAX_MODEL_REQUESTS": "20", "MAX_MODEL_TOKENS": "100000",
        }):
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []

            def upstream(request):
                body = json.loads(request.content)
                calls.append(body)
                if body["messages"][0]["content"] == "":
                    return httpx.Response(400, json={"error": {
                        "type": "invalid_request_error", "message": "system must not be empty"}})
                return httpx.Response(200, json={"choices": [], "usage": {
                    "prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110}})

            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        for text, expected in (("", 400), ("solve", 200)):
                            reply = await client.post("/model/openai/v1/chat/completions", json={
                                "model": "gpt-5.6-sol", "messages": [{"role": "system", "content": text}]})
                            self.assertEqual(reply.status_code, expected, reply.text)
                events = [json.loads(line) for line in (Path(temp) / "events.jsonl").read_text().splitlines()]
                receipts = [e["data"] for e in events if e["kind"] == "model.accounting"]
                self.assertEqual(len(calls), 2)
                self.assertEqual(receipts[0]["accounting_method"], "gateway")
                self.assertEqual(receipts[0]["accounting_basis"], "input_rejected_before_generation")
                self.assertEqual(receipts[0]["http_status"], 400)
                self.assertEqual(receipts[0]["normalized_usd"], 0)
                self.assertEqual(receipts[1]["accounting_basis"], "provider_usage")
                self.assertGreater(receipts[1]["normalized_usd"], 0)
                self.assertEqual(runtime.ledger.model_inflight, {})
            finally:
                await runtime.client.aclose()

    async def test_chatgpt_gateway_private_auth_stream_and_transport_error(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp,
            "DUNGENESS_ALLOWED_MODELS": '[["openai-chatgpt","gpt-6-astra"]]',
            "MAX_MODEL_REQUESTS": "20", "MAX_MODEL_TOKENS": "100000",
            "DUNGENESS_CHATGPT_AUTH_FILE": str(Path(temp) / "auth.json"),
        }):
            auth = Path(temp) / "auth.json"
            auth.write_text(json.dumps({"tokens": {"access_token": "private-test-token",
                                                  "account_id": "private-account"}}))
            auth.chmod(0o600)
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []

            def upstream(request):
                calls.append(request)
                self.assertEqual(request.headers["authorization"], "Bearer private-test-token")
                self.assertEqual(request.headers["chatgpt-account-id"], "private-account")
                if len(calls) == 2:
                    raise httpx.ConnectError("offline provider", request=request)
                response = {"type": "response.completed", "response": {
                    "usage": {"input_tokens": 100, "output_tokens": 10}, "output": []}}
                class Stream(httpx.AsyncByteStream):
                    async def __aiter__(self):
                        yield ("data: " + json.dumps(response) + "\n\n").encode()
                # ChatGPT's backend labels its SSE as JSON.
                return httpx.Response(200, stream=Stream(), headers={"content-type": "application/json"})

            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        payload = {"model": "gpt-6-astra", "input": "solve", "stream": True}
                        for expected in (200, 502, 429):
                            reply = await client.post("/model/chatgpt/v1/responses", json=payload,
                                headers={"authorization": "Bearer testbed", "chatgpt-account-id": "untrusted"})
                            self.assertEqual(reply.status_code, expected, reply.text)
                self.assertEqual(len(calls), 2)
                receipts = [json.loads(line)["data"] for line in (Path(temp) / "events.jsonl").read_text().splitlines()
                            if json.loads(line)["kind"] == "model.accounting"]
                self.assertEqual(receipts[0]["accounting_method"], "gateway")
                self.assertGreater(receipts[0]["normalized_usd"], 0)
                self.assertIsNone(receipts[0]["billed_usd"])
                self.assertEqual(receipts[1]["accounting_method"], "unavailable")
                self.assertNotIn("private-test-token", (Path(temp) / "events.jsonl").read_text())
            finally:
                await runtime.client.aclose()

    def test_ambiguous_errors_never_become_zero_cost_receipts(self):
        from gateway_runtime import rejected_before_generation
        error = {"error": {"type": "invalid_request_error", "message": "invalid"}}
        for status, body, mime in (
            (200, error, "application/json"), (500, error, "application/json"),
            (400, {**error, "choices": [{"text": "generated"}]}, "application/json"),
            (400, {"error": {"type": "server_error"}}, "application/json"),
            (400, error, "text/event-stream"),
        ):
            with self.subTest(status=status, body=body):
                self.assertFalse(rejected_before_generation(json.dumps(body).encode(), mime, status))

    async def test_sdk_chat_clients_use_api_and_new_catalog_model_with_trusted_prices(self):
        """No Codex client, provider-name spoofing, or model-specific agent."""
        model = "example/new-model"
        reference = {"provider": "openrouter", "upstream_id": model, "request_models": [model],
                     "input_per_mtok": 2, "cached_read_per_mtok": .2,
                     "cache_write_per_mtok": 2, "output_per_mtok": 6, "text_only": True}
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp, "MAX_MODEL_REQUESTS": "20", "MAX_MODEL_TOKENS": "100000",
            "DUNGENESS_ALLOWED_MODELS": json.dumps([["openai", "gpt-5.6-sol"], ["openrouter", model]]),
        }), patch.object(gateway_pricing, "MODEL_PRICING", [*gateway_pricing.MODEL_PRICING, reference]):
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []

            async def upstream(request):
                payload = json.loads(request.content)
                calls.append(payload)
                self.assertEqual(request.url.path, "/v1/chat/completions" if payload["model"] == "gpt-5.6-sol"
                                 else "/api/v1/chat/completions")
                self.assertEqual(request.headers["user-agent"], "dungeness-gateway/1")
                self.assertNotEqual(request.headers["authorization"], "Bearer testbed")
                self.assertTrue(payload["stream_options"]["include_usage"])
                response = {"id": "mock-response", "choices": [],
                            "usage": {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110}}
                class Stream(httpx.AsyncByteStream):
                    async def __aiter__(self):
                        yield ("data: " + json.dumps(response) + "\n\ndata: [DONE]\n\n").encode()
                return httpx.Response(200, stream=Stream(),
                                      headers={"content-type": "text/event-stream"})

            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        for provider, name in (("openai", "gpt-5.6-sol"), ("openrouter", model)):
                            reply = await client.post(f"/model/{provider}/v1/chat/completions",
                                headers={"Authorization": "Bearer testbed"},
                                json={"model": name, "messages": [{"role": "user", "content": "solve"}],
                                      "tools": [{"type": "function", "function": {"name": "evaluate",
                                                "parameters": {"type": "object"}}}],
                                      "stream": True, "stream_options": {"include_usage": False}})
                            self.assertEqual(reply.status_code, 200, reply.text)
                        for extra in (
                            {"models": ["example/other"]},
                            {"plugins": [{"id": "web"}]},
                            {"tools": [{"type": "web_search"}]},
                            {"messages": [{"role": "user", "content": [
                                {"type": "image_url", "image_url": {"url": "https://example.invalid/image"}}]}]},
                        ):
                            reply = await client.post("/model/openrouter/v1/chat/completions",
                                json={"model": model, "messages": [{"role": "user", "content": "solve"}], **extra})
                            self.assertEqual(reply.status_code, 400, reply.text)
                self.assertEqual(len(calls), 2)
                self.assertAlmostEqual(runtime.ledger.usd_spent, .00106)
                events = [json.loads(line) for line in (Path(temp) / "events.jsonl").read_text().splitlines()]
                accounting = [event["data"] for event in events if event["kind"] == "model.accounting"]
                self.assertEqual(len(accounting), 2)
                self.assertAlmostEqual(accounting[0]["billed_usd"], .0008)
                self.assertIsNone(accounting[1]["billed_usd"])
                self.assertEqual(runtime.ledger.model_inflight, {})
            finally:
                await runtime.client.aclose()

    async def test_missing_usage_on_generic_chat_blocks_more_inference(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp, "DUNGENESS_ALLOWED_MODELS": '[["openai","gpt-5.6-sol"]]',
        }):
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []

            def upstream(request):
                calls.append(request)
                return httpx.Response(200, json={"choices": [{"message": {"content": "no usage"}}]})

            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        payload = {"model": "gpt-5.6-sol", "messages": [{"role": "user", "content": "solve"}]}
                        await client.post("/model/openai/v1/chat/completions", json=payload)
                        denied = await client.post("/model/openai/v1/chat/completions", json=payload)
                        self.assertEqual(denied.status_code, 429)
                self.assertEqual(len(calls), 1)
            finally:
                await runtime.client.aclose()

    async def test_parallel_models_are_authorized_and_share_admission_and_actual_usage(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp, "MAX_MODEL_REQUESTS": "20", "MAX_MODEL_TOKENS": "100000",
            "DUNGENESS_MAX_PARALLEL_REQUESTS": "2", "DUNGENESS_REQUEST_RESERVATION_USD": ".5",
            "DUNGENESS_ALLOWED_MODELS": json.dumps([
                ["openai", "gpt-5.6-sol"], ["openai", "gpt-6-astra"]]),
        }):
            runtime = Gateway()
            await runtime.client.aclose()
            both_started, release = asyncio.Event(), asyncio.Event()
            calls = []

            async def provider(request):
                payload = json.loads(request.content)
                calls.append(payload["model"])
                if len(calls) == 2:
                    both_started.set()
                await release.wait()
                return httpx.Response(200, json={
                    "id": payload["model"], "usage": {"input_tokens": 100, "output_tokens": 10},
                    "output": []})

            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(provider))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        first = asyncio.create_task(client.post("/model/openai/v1/responses",
                            json={"model": "gpt-5.6-sol", "input": "worker one"}))
                        second = asyncio.create_task(client.post("/model/openai/v1/responses",
                            json={"model": "gpt-6-astra", "input": "worker two"}))
                        try:
                            await asyncio.wait_for(both_started.wait(), 5)
                            rejected = await client.post("/model/openai/v1/responses",
                                json={"model": "gpt-5.6-sol", "input": "third worker"})
                            self.assertEqual(rejected.status_code, 429)
                        finally:
                            release.set()
                        replies = await asyncio.gather(first, second)
                        self.assertEqual([r.status_code for r in replies], [200, 200])
                        unauthorized = await client.post("/model/openai/v1/responses",
                            json={"model": "unpriced-model", "input": "must not reach provider"})
                        self.assertEqual(unauthorized.status_code, 400)
                self.assertEqual(len(calls), 2)
                self.assertEqual(runtime.ledger.counts["model_requests"], 2)
                self.assertEqual(runtime.ledger.model_inflight, {})
                self.assertAlmostEqual(runtime.ledger.usd_spent, .0023)
                events = [json.loads(line) for line in (Path(temp) / "events.jsonl").read_text().splitlines()]
                receipts = [e for e in events if e["kind"] == "model.accounting"]
                self.assertEqual({e["data"]["model"] for e in receipts}, set(calls))
                self.assertTrue(all(e["data"]["accounting_method"] == "gateway" for e in receipts))
            finally:
                await runtime.client.aclose()


if __name__ == "__main__":
    unittest.main()
