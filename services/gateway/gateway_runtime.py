"""Run-scoped gateway implementation for model traffic."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
import json
from provider_profiles import PROFILES, upstream_model
import os
from pathlib import Path
import time
from typing import Any

import httpx
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from gateway_models import (
    CHATGPT_ROUTES,
    MODEL_PROVIDERS,
    capture_prompt,
    decode_response_documents,
    extract_reasoning_summaries,
    extract_visible_reasoning_events,
    is_sse_body,
    prompt_profile,
    provider_auth_headers,
    usage_extractor,
)
from gateway_security import SecretFilter, ResponseLimitExceeded, MAX_RESPONSE_BYTES, safe_provider_error
import gateway_pricing
from gateway_pricing import (
    CACHED_TOKEN_WEIGHT,
    pricing_for_request,
    request_budget_tokens,
    request_pricing_rates,
    request_usd,
)
from gateway_request_policy import validate_model_headers, validate_model_request, validate_model_transport
from gateway_usage import (
    METRICS,
    UsageLedger,
    bounded_model_name,
    log_event,
    set_active_ledger,
)
BACKGROUND_TASKS: set[asyncio.Task[None]] = set()


def transport_failure_category(error: BaseException) -> str:
    """Fixed diagnostic labels only; exception messages can contain URLs or secrets."""
    for kind, label in (
        (asyncio.CancelledError, "gateway_cancelled"),
        (ResponseLimitExceeded, "upstream_response_too_large"),
        (httpx.ReadTimeout, "upstream_read_timeout"),
        (httpx.ConnectTimeout, "upstream_connect_timeout"),
        (httpx.TimeoutException, "upstream_transport_timeout"),
        (httpx.RemoteProtocolError, "upstream_protocol_error"),
        (httpx.NetworkError, "upstream_connection_error"),
    ):
        if isinstance(error, kind):
            return label
    return "transport_failure_unknown"


def rejected_before_generation(
    body: bytes, content_type: str, http_status: int | None,
) -> bool:
    """Recognize an explicit input-validation rejection, never a missing receipt."""
    mime = content_type.partition(";")[0].strip().lower()
    if http_status != 400 or mime != "application/json":
        return False
    try:
        document = json.loads(body)
    except (ValueError, UnicodeError):
        return False
    return (isinstance(document, dict) and set(document) == {"error"}
            and isinstance(document["error"], dict)
            and document["error"].get("type") == "invalid_request_error")


def trusted_model_proxy():
    """Only the operator's explicit model proxy; ignore ambient HTTP_PROXY."""
    from urllib.parse import urlsplit
    value = os.environ.get("DUNGENESS_MODEL_HTTPS_PROXY")
    if not value:
        return None
    target = urlsplit(value)
    if (target.scheme != "http" or not target.hostname or target.port is None
            or target.username or target.password or target.path not in ("", "/")
            or target.query or target.fragment):
        raise ValueError("Invalid trusted model proxy")
    return value


class Gateway:
    """One trusted gateway instance and budget ledger for one benchmark run."""

    def __init__(self) -> None:
        self.run_id = os.environ["TESTBED_RUN_ID"]
        self.ledger = UsageLedger(
            self.run_id,
            Path(os.environ.get("TESTBED_USAGE_DIR", "/var/lib/testbed/usage")),
        )
        set_active_ledger(self.ledger)
        allowed = os.environ.get("DUNGENESS_ALLOWED_MODELS")
        pairs = json.loads(allowed) if allowed else None
        if pairs is not None and (not isinstance(pairs, list) or not pairs or any(
                not isinstance(pair, list) or len(pair) != 2
                or not all(isinstance(item, str) and item for item in pair) for pair in pairs)):
            raise ValueError("Invalid model allowlist")
        if os.environ.get("DUNGENESS_REQUIRE_MODEL_ALLOWLIST") == "1" and not pairs:
            raise ValueError("Hosted command gateway requires an explicit model allowlist")
        self.allowed_models = {tuple(pair) for pair in pairs} if pairs else None
        # OpenRouter can force account-default plugins even when a request
        # disables them. This assertion belongs to the trusted operator, never
        # a run spec or agent request. Leave the route closed until configured.
        self.openrouter_inference_only = os.environ.get("DUNGENESS_OPENROUTER_INFERENCE_ONLY") == "1"
        # Model reasoning can legitimately take longer than an ordinary web
        # request. Responses are streamed to the agent as they arrive, while a
        # bounded overall timeout still prevents abandoned provider calls.
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(600.0, connect=30.0), trust_env=False, follow_redirects=False,
            proxy=trusted_model_proxy()
        )


    async def search(self, query, options=None, request_id="internal"):
        raise ValueError("External web search and fetch are disabled.")

    async def fetch(self, url, options=None, request_id="internal"):
        raise ValueError("External web search and fetch are disabled.")

    async def admit_model(self, provider: str, request: Request, operation: str) -> dict:
        validate_model_transport(operation, request.method, list(request.query_params.multi_items()),
                                 await request.body())
        validate_model_headers(request.headers)
        try:
            payload = await request.json()
        except (ValueError, UnicodeError, RecursionError) as error:
            raise ValueError("model request body must be valid JSON") from error
        # Access policy is independent of command/legacy harness identity,
        # pricing mode, web budgets, and whether a model allowlist was supplied.
        validate_model_request(provider, operation, payload)
        if provider in PROFILES:
            upstream_model(provider, payload['model'])
        # All credential types are checked before admitting a model request.
        provider_auth_headers(provider)
        if provider == "openrouter" and not self.openrouter_inference_only:
            raise ValueError(
                "OpenRouter inference requires the operator to disable account-default "
                "server tools/plugins and set TESTBED_OPENROUTER_INFERENCE_ONLY=1"
            )
        if self.allowed_models is not None and (provider, payload["model"]) not in self.allowed_models:
            raise ValueError("model is not authorized for this run")
        from gateway_models import validate_declared_request
        validate_declared_request(payload, pricing_for_request(provider, payload["model"]))
        if self.allowed_models is None:
            self.ledger.reserve("model_requests")
        else:
            self.ledger.admit_model(request.state.request_id)
        log_event("model_request_admitted", request_id=request.state.request_id)
        return payload

    async def proxy_model(
        self, provider: str, path: str, request: Request
    ) -> Response:
        normalized = path.strip("/")
        cfg = MODEL_PROVIDERS[provider]
        extract = usage_extractor(cfg, normalized)

        # Never concatenate an arbitrary agent-supplied path onto the provider
        # origin. Only the small API surface needed by installed agents passes.
        if normalized not in cfg["routes"]:
            return JSONResponse(
                {"error": "unsupported model operation"}, status_code=404
            )
        if normalized == "models":
            validate_model_transport(normalized, request.method, list(request.query_params.multi_items()),
                                     await request.body())
            validate_model_headers(request.headers)
            # Discovery is local. Do not expose arbitrary provider operations,
            # account state or unapproved model aliases through this GET route.
            names = sorted({name for entry in gateway_pricing.MODEL_PRICING if entry["provider"] == provider
                            for name in entry["request_models"]
                            if self.allowed_models is None or (provider, name) in self.allowed_models})
            return JSONResponse({"object": "list", "data": [
                {"id": name, "object": "model", "owned_by": provider} for name in names]})
        payload = await self.admit_model(provider, request, normalized)
        started = time.monotonic()
        status = "error"
        usage: dict[str, int] = {}
        model = "unknown"
        request_pricing: dict[str, Any] | None = None
        request_id = request.state.request_id
        finalized = False
        upstream_status = None
        failure_category = None
        failure_stage = None

        def finalize(response_body: bytes, content_type: str) -> None:
            """Account for one model request exactly once, including streams."""

            nonlocal finalized, usage
            if finalized:
                return
            finalized = True
            usage = extract(response_body, content_type)
            accounting_basis = "provider_usage" if usage else "unavailable"
            if (not usage and status == "provider_error"
                    and rejected_before_generation(response_body, content_type, upstream_status)):
                # A rejected input did not generate tokens. Successful,
                # interrupted, and ambiguous error responses still fail closed.
                usage = {"input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0,
                         "cache_write_input_tokens": 0, "total_tokens": 0}
                accounting_basis = "input_rejected_before_generation"
            # Charge the token budget using the active tier's relative cache
            # rates. USD accounting below remains the exact stopping criterion.
            billed_tokens = request_budget_tokens(usage, request_pricing)
            usd = round(
                request_usd(usage, request_pricing)
                if request_pricing is not None
                else 0,
                6,
            )
            pricing_tier = (
                request_pricing_rates(usage, request_pricing)[1]
                if request_pricing is not None
                else "unavailable"
            )
            billed_usd = usd if cfg.get("billed", True) and not (request_pricing or {}).get("text_only") else None
            self.ledger.add_model_usage(
                billed_tokens=billed_tokens,
                normalized_usd=usd,
                billed_usd=billed_usd,
            )
            response_documents = decode_response_documents(
                response_body, content_type
            )
            reasoning_summaries = extract_reasoning_summaries(
                response_body, content_type
            )
            for index, summary in enumerate(reasoning_summaries):
                self.ledger.timeline(
                    {
                        "kind": "model.reasoning",
                        "request_id": request_id,
                        "provider": provider,
                        "model": model,
                        "source": "reasoning_summary",
                        "index": index,
                        "text": summary,
                    }
                )
            for index, reasoning in enumerate(
                extract_visible_reasoning_events(response_documents)
            ):
                self.ledger.timeline(
                    {
                        "kind": "model.reasoning",
                        "request_id": request_id,
                        "provider": provider,
                        "model": model,
                        "source": reasoning["source"],
                        "index": index,
                        "text": reasoning["text"],
                    }
                )
            self.ledger.timeline(
                {
                    "kind": "model.response",
                    "request_id": request_id,
                    "provider": provider,
                    "operation": normalized,
                    "model": model,
                    "status": status,
                    "content_type": content_type,
                    "response": response_documents,
                }
            )
            if usage:
                METRICS.increment(
                    "testbed_gateway_model_billed_tokens_total",
                    labels={"provider": provider},
                    value=billed_tokens,
                )
                METRICS.increment(
                    "testbed_gateway_model_usd_total",
                    labels={"provider": provider},
                    value=usd,
                )
            for token_type in (
                "input_tokens",
                "cached_input_tokens",
                "cache_write_input_tokens",
                "output_tokens",
                "reasoning_tokens",
                "total_tokens",
            ):
                if usage.get(token_type):
                    METRICS.increment(
                        "testbed_gateway_model_tokens_total",
                        labels={"provider": provider, "type": token_type},
                        value=usage[token_type],
                    )
            duration_ms = round((time.monotonic() - started) * 1000)
            self.ledger.record(
                "model",
                {
                    "request_id": request_id,
                    "provider": provider,
                    "model": model,
                    **usage,
                    "billed_tokens": billed_tokens,
                    # model_usd/usd remain the normalized budget values for
                    # compatibility with existing run summaries. billed_usd is
                    # null for subscription traffic with no per-request invoice.
                    "usd": usd,
                    "normalized_usd": usd,
                    "billed_usd": billed_usd,
                    "pricing_tier": pricing_tier,
                    "accounting_method": "gateway" if usage else "unavailable",
                    "accounting_basis": accounting_basis,
                    "http_status": upstream_status,
                    "duration_ms": duration_ms,
                    "status": status,
                    **({"failure_category": failure_category, "failure_stage": failure_stage}
                       if failure_category else {}),
                },
            )
            METRICS.increment(
                "testbed_gateway_provider_requests_total",
                labels={
                    "provider": provider,
                    "operation": normalized,
                    "status": status,
                },
            )
            METRICS.increment(
                "testbed_gateway_provider_duration_seconds_sum",
                labels={"provider": provider, "operation": normalized},
                value=duration_ms / 1000,
            )
            log_event(
                "model_request_completed",
                run_id=self.run_id,
                request_id=request_id,
                provider=provider,
                operation=normalized,
                model=model,
                duration_ms=duration_ms,
                status=status,
                usage=usage,
            )
            if self.allowed_models is not None:
                self.ledger.finish_model(request_id, accounted=bool(usage))

        private_values = set()
        auth_headers = provider_auth_headers(provider, private_values=private_values)
        response_filter = SecretFilter(private_values)
        response_body = bytearray()
        received_bytes = 0

        def accept_chunk(chunk, *, final=False):
            nonlocal received_bytes
            received_bytes += len(chunk)
            if received_bytes > MAX_RESPONSE_BYTES:
                raise ResponseLimitExceeded()
            safe = response_filter.feed(chunk, final=final)
            if len(response_body) + len(safe) > MAX_RESPONSE_BYTES:
                raise ResponseLimitExceeded()
            response_body.extend(safe)
            return safe

        content_type = "application/json"
        try:
            model = bounded_model_name(payload.get("model"))
            request_pricing = pricing_for_request(provider, model)
            if normalized == "chat/completions" and payload.get("stream"):
                payload["stream_options"] = {**(payload.get("stream_options") or {}), "include_usage": True}
            if provider == "openrouter":
                # A missing plugins field can inherit an account's default web
                # plugin. This override is gateway-owned; agents cannot set it.
                payload["plugins"] = [{"id": "web", "enabled": False}]
            body = json.dumps(payload, separators=(",", ":")).encode()
            # Record how this agent composed the prompt (profile always; full
            # body only under TESTBED_CAPTURE_PROMPTS) -- lets us measure
            # cross-agent presentation bias from what actually hit the model.
            safe_body = SecretFilter(private_values).feed(body, final=True)
            safe_payload = json.loads(safe_body)
            capture_prompt(request_id, provider, normalized, model, safe_body, safe_payload)
            self.ledger.timeline(
                {
                    "kind": "model.request",
                    "request_id": request_id,
                    "provider": provider,
                    "operation": normalized,
                    "model": model,
                    "prompt_profile": prompt_profile(payload, body),
                    "request": safe_payload,
                }
            )
            upstream_base = os.environ.get(
                cfg["upstream_env"], cfg["upstream_default"]
            ).rstrip("/")
            profile_headers = {}
            if provider in PROFILES:
                profile = PROFILES[provider]
                routed_model = upstream_model(provider, model)
                if profile['model_header']:
                    profile_headers[profile['model_header']] = routed_model
                body = json.dumps({**payload, 'model': routed_model}, separators=(',', ':')).encode()
            upstream_request = self.client.build_request(
                request.method,
                f"{upstream_base}/{normalized}",
                headers={
                    **profile_headers,
                    "content-type": "application/json",
                    "accept": request.headers.get("accept", "application/json"),
                    # Force uncompressed responses: we forward raw upstream bytes
                    # to the agent (only content-type, not content-encoding) and
                    # parse them for accounting, so a compressed body would be
                    # unreadable to BOTH the agent and the usage parser.
                    "accept-encoding": "identity",
                    "user-agent": "dungeness-gateway/1",
                    **{
                        name: request.headers[name]
                        for name in cfg["passthrough"]
                        if name in request.headers
                    },
                    # Trusted credentials win over any allowed client metadata.
                    **auth_headers,
                },
                params=request.query_params,
                content=body,
            )
            upstream = await self.client.send(upstream_request, stream=True)
            upstream_status = upstream.status_code
            # Do not reflect arbitrary upstream headers, even Content-Type.
            raw_type = upstream.headers.get("content-type", "application/json").partition(";")[0].strip().lower()
            content_type = raw_type if raw_type in {"application/json", "text/event-stream"} else "text/plain"
            status = "success" if upstream.is_success else "provider_error"
            # ChatGPT's Codex backend currently returns Responses SSE framing
            # with application/json. The request's stream flag is the reliable
            # signal at this boundary; normalize the downstream header so both
            # Codex and the accounting parser treat it as a stream.
            if (
                provider == "openai-chatgpt"
                and normalized in CHATGPT_ROUTES
                and payload.get("stream") is True
            ):
                content_type = "text/event-stream"
            response_headers = {"content-type": content_type}

            if "text/event-stream" in content_type and upstream.is_success:
                # Bounded relay with backpressure. On disconnect, drain upstream
                # for accounting but discard client output rather than buffering it.
                relay: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=16)
                disconnected = asyncio.Event()

                async def relay_chunk(chunk):
                    if disconnected.is_set():
                        return
                    put = asyncio.create_task(relay.put(chunk))
                    gone = asyncio.create_task(disconnected.wait())
                    try:
                        done, _ = await asyncio.wait((put, gone), timeout=30,
                                                     return_when=asyncio.FIRST_COMPLETED)
                        if not done:
                            # A stalled consumer must not pin a provider pump.
                            # End its stream and continue draining for accounting.
                            disconnected.set()
                            while not relay.empty():
                                relay.get_nowait()
                            relay.put_nowait(None)
                    finally:
                        for pending in (put, gone):
                            if not pending.done(): pending.cancel()
                        await asyncio.gather(put, gone, return_exceptions=True)

                async def pump() -> None:
                    nonlocal status, failure_category, failure_stage
                    try:
                        async for chunk in upstream.aiter_bytes():
                            # Bound individual queue entries as well as total
                            # retained response bytes.
                            for offset in range(0, len(chunk), 64 * 1024):
                                safe = accept_chunk(chunk[offset:offset + 64 * 1024])
                                if safe:
                                    await relay_chunk(safe)
                        tail = accept_chunk(b"", final=True)
                        if tail:
                            await relay_chunk(tail)
                    except BaseException as error:
                        status = "stream_interrupted"
                        failure_category = transport_failure_category(error)
                        failure_stage = "upstream_stream"
                    finally:
                        # Preserve a complete final usage event even if the
                        # transport fails after delivering it. Never treat a
                        # missing event as zero usage.
                        try:
                            if failure_category != "upstream_response_too_large":
                                accept_chunk(b"", final=True)
                        except ResponseLimitExceeded:
                            status = "stream_interrupted"
                            failure_category = "upstream_response_too_large"
                            failure_stage = "upstream_stream"
                        try:
                            await upstream.aclose()
                        finally:
                            try:
                                finalize(bytes(response_body), content_type)
                            finally:
                                await relay_chunk(None)

                pump_task = asyncio.ensure_future(pump())
                BACKGROUND_TASKS.add(pump_task)
                pump_task.add_done_callback(BACKGROUND_TASKS.discard)

                async def stream_chunks() -> AsyncIterator[bytes]:
                    try:
                        while True:
                            chunk = await relay.get()
                            if chunk is None:
                                break
                            yield chunk
                    finally:
                        disconnected.set()

                return StreamingResponse(stream_chunks(), status_code=upstream.status_code,
                                         headers=response_headers,
                                         background=BackgroundTask(disconnected.set))

            try:
                async for chunk in upstream.aiter_bytes():
                    accept_chunk(chunk)
                accept_chunk(b"", final=True)
            except BaseException as error:
                status = "stream_interrupted"
                failure_category = transport_failure_category(error)
                failure_stage = "upstream_response_body"
                raise
            finally:
                await upstream.aclose()
            finalize(bytes(response_body), content_type)
            if not upstream.is_success:
                return safe_provider_error(upstream.status_code, request_id)
            return Response(bytes(response_body), status_code=upstream.status_code,
                            headers=response_headers)
        except BaseException as error:
            if failure_category is None:
                failure_category = transport_failure_category(error)
                failure_stage = "upstream_request"
            finalize(bytes(response_body), content_type)
            if isinstance(error, ResponseLimitExceeded):
                return JSONResponse({"error": {"code": "upstream_response_too_large",
                    "request_id": request_id, "retryable": False}}, status_code=502)
            raise
