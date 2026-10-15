"""Run-scoped gateway implementation for web and model traffic."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator, Callable
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any

import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from gateway_models import (
    CHATGPT_ROUTES,
    MODEL_PROVIDERS,
    capture_prompt,
    decode_response_documents,
    extract_reasoning_summaries,
    extract_usage,
    extract_visible_reasoning_events,
    is_sse_body,
    prompt_profile,
    provider_auth_headers,
    usage_extractor,
)
from gateway_pricing import (
    CACHED_TOKEN_WEIGHT,
    pricing_for_request,
    request_budget_tokens,
    request_pricing_rates,
    request_usd,
)
from gateway_usage import (
    METRICS,
    UsageLedger,
    bounded_model_name,
    bounded_text,
    log_event,
    set_active_ledger,
)
from gateway_web import (
    CONTENT_BEARING_RESULT_FIELDS,
    approve_historical_result,
    make_search_payload,
    parse_utc,
)
from kimi_adapter import model_dump as dump_adapter_event
from kimi_adapter import NativeReasoningStream
from kimi_adapter import request_kimi


EXA_SEARCH_URL = "https://api.exa.ai/search"
EXA_CONTENTS_URL = "https://api.exa.ai/contents"
BACKGROUND_TASKS: set[asyncio.Task[None]] = set()


def rejected_before_generation(body: bytes, content_type: str, http_status: int | None) -> bool:
    """Recognize an explicit input-validation rejection, never a missing receipt."""
    if http_status != 400 or "application/json" not in content_type:
        return False
    try:
        document = json.loads(body)
    except (ValueError, UnicodeError):
        return False
    return (isinstance(document, dict) and set(document) == {"error"}
            and isinstance(document["error"], dict)
            and document["error"].get("type") == "invalid_request_error")


class Gateway:
    """One trusted gateway instance and budget ledger for one benchmark run."""

    def __init__(
        self,
        *,
        kimi_request: Callable[..., Any] | None = None,
    ) -> None:
        self._request_kimi = kimi_request or request_kimi
        self.run_id = os.environ["TESTBED_RUN_ID"]
        self.max_results = int(os.environ.get("EXA_MAX_RESULTS", "25"))
        self.end_published_date = os.environ["EXA_END_PUBLISHED_DATE"]
        self.ledger = UsageLedger(
            self.run_id,
            Path(os.environ.get("TESTBED_USAGE_DIR", "/var/lib/testbed/usage")),
        )
        set_active_ledger(self.ledger)
        # Fetch is intentionally not an arbitrary URL reader. A target becomes
        # eligible only after the gateway independently validates an Exa result.
        # Keep the approval metadata so retrieval can be checked against the
        # exact search-time decision rather than authorizing a raw URL forever.
        self.allowed_fetch_targets: dict[str, dict[str, Any]] = {}
        allowed = os.environ.get("DUNGENESS_ALLOWED_MODELS")
        self.allowed_models = {tuple(pair) for pair in json.loads(allowed)} if allowed else None
        # Model reasoning can legitimately take longer than an ordinary web
        # request. Responses are streamed to the agent as they arrive, while a
        # bounded overall timeout still prevents abandoned provider calls.
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(600.0, connect=30.0)
        )


    async def search(
        self,
        query: str,
        options: dict[str, Any] | None = None,
        request_id: str = "internal",
    ) -> dict[str, Any]:
        self.ledger.reserve("searches")
        started = time.monotonic()
        status = "error"
        provider_called = False
        self.ledger.timeline(
            {
                "kind": "web.search.request",
                "request_id": request_id,
                "query": bounded_text(query),
                "options": options or {},
            }
        )
        try:
            payload = make_search_payload(
                query,
                options or {},
                max_results=self.max_results,
                end_published_date=self.end_published_date,
            )
            provider_called = True
            response = await self.client.post(
                EXA_SEARCH_URL,
                headers={
                    "x-api-key": os.environ["EXA_API_KEY"],
                    "content-type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            cutoff = parse_utc(self.end_published_date)
            kept = []
            rejected: dict[str, int] = defaultdict(int)
            results = result.get("results", [])
            if not isinstance(results, list):
                raise ValueError("Exa search response results must be a list")
            for item in results:
                approval, reason = approve_historical_result(item, cutoff)
                if approval is None:
                    rejected[reason or "rejected"] += 1
                    self.ledger.append(
                        "web-rejections",
                        {
                            "request_id": request_id,
                            "operation": "search",
                            "reason": reason or "rejected",
                            "url": bounded_text(
                                item.get("url") if isinstance(item, dict) else ""
                            ),
                        },
                    )
                    continue

                approved_item = dict(item)
                if approval["content_access"] != "immutable":
                    for key in CONTENT_BEARING_RESULT_FIELDS:
                        approved_item.pop(key, None)
                approved_item["testbedHistorical"] = {
                    "effectivePublishedAt": approval["effective_published_at"],
                    "dateEvidence": approval["date_evidence"],
                    "contentAccess": approval["content_access"],
                    "fetchEligible": approval["content_access"] == "immutable",
                }
                kept.append(approved_item)
                if approval["content_access"] == "immutable":
                    for key in ("id", "url"):
                        if isinstance(item.get(key), str):
                            self.allowed_fetch_targets[item[key]] = approval
            result["results"] = kept
            result["testbedPolicy"] = {
                "endPublishedDate": self.end_published_date,
                "maxAgeHours": -1,
                "mode": "strict-historical",
                "missingDate": "reject",
                "mutableUrl": "reject",
                "mutableContent": "metadata-only",
                "rejectedResults": dict(sorted(rejected.items())),
            }
            status = "success"
            METRICS.increment(
                "testbed_gateway_web_results_total",
                labels={"operation": "search"},
                value=len(kept),
            )
            self.ledger.timeline(
                {
                    "kind": "web.search.response",
                    "request_id": request_id,
                    "status": status,
                    "response": result,
                }
            )
            return result
        except BaseException as error:
            self.ledger.timeline(
                {
                    "kind": "web.search.response",
                    "request_id": request_id,
                    "status": status,
                    "error_type": type(error).__name__,
                }
            )
            raise
        finally:
            duration_ms = round((time.monotonic() - started) * 1000)
            # The canonical web.accounting event records the actual query so a
            # reviewer can see what the agent researched. Metrics labels and
            # the operational stderr log stay query-free.
            self.ledger.record(
                "web",
                {
                    "request_id": request_id,
                    "operation": "search",
                    "query": bounded_text(query),
                    "duration_ms": duration_ms,
                    "status": status,
                },
            )
            if provider_called:
                METRICS.increment(
                    "testbed_gateway_provider_requests_total",
                    labels={"provider": "exa", "operation": "search", "status": status},
                )
                METRICS.increment(
                    "testbed_gateway_provider_duration_seconds_sum",
                    labels={"provider": "exa", "operation": "search"},
                    value=duration_ms / 1000,
                )
            log_event(
                "web_request_completed",
                run_id=self.run_id,
                request_id=request_id,
                operation="search",
                provider="exa",
                provider_called=provider_called,
                duration_ms=duration_ms,
                status=status,
            )

    async def fetch(
        self,
        url: str,
        options: dict[str, Any] | None = None,
        request_id: str = "internal",
    ) -> dict[str, Any]:
        self.ledger.reserve("fetches")
        started = time.monotonic()
        status = "error"
        provider_called = False
        self.ledger.timeline(
            {
                "kind": "web.fetch.request",
                "request_id": request_id,
                "url": bounded_text(url),
                "options": options or {},
            }
        )
        try:
            approval = self.allowed_fetch_targets.get(url)
            if approval is None:
                raise ValueError(
                    "fetch target was not approved by an earlier historical search"
                )
            options = options or {"highlights": True}
            if not isinstance(options, dict):
                raise ValueError("options must be an object")
            unknown = sorted(set(options) - {"highlights", "text"})
            if unknown:
                raise ValueError(f"unsupported fetch options: {', '.join(unknown)}")
            provider_called = True
            response = await self.client.post(
                EXA_CONTENTS_URL,
                headers={
                    "x-api-key": os.environ["EXA_API_KEY"],
                    "content-type": "application/json",
                },
                json={"urls": [url], **options, "maxAgeHours": -1},
            )
            response.raise_for_status()
            result = response.json()
            results = result.get("results")
            if not isinstance(results, list) or len(results) != 1:
                raise ValueError("Exa fetch response must contain exactly one result")
            fetched = results[0]
            fetched_approval, reason = approve_historical_result(
                fetched, parse_utc(self.end_published_date)
            )
            if fetched_approval is None:
                raise ValueError(
                    f"fetched content failed historical validation: {reason}"
                )
            if fetched_approval["url"] != approval["url"]:
                raise ValueError("fetched content URL differs from approved result")
            if (
                fetched_approval["effective_published_at"]
                != approval["effective_published_at"]
            ):
                raise ValueError(
                    "fetched content publication metadata differs from approved result"
                )

            content_digest = hashlib.sha256(
                json.dumps(
                    fetched, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                ).encode("utf-8")
            ).hexdigest()
            result["testbedPolicy"] = {
                "maxAgeHours": -1,
                "mode": "strict-historical",
                "effectivePublishedAt": approval["effective_published_at"],
                "contentSha256": content_digest,
            }
            status = "success"
            self.ledger.timeline(
                {
                    "kind": "web.fetch.response",
                    "request_id": request_id,
                    "status": status,
                    "response": result,
                }
            )
            return result
        except BaseException as error:
            self.ledger.timeline(
                {
                    "kind": "web.fetch.response",
                    "request_id": request_id,
                    "status": status,
                    "error_type": type(error).__name__,
                }
            )
            raise
        finally:
            duration_ms = round((time.monotonic() - started) * 1000)
            self.ledger.record(
                "web",
                {
                    "request_id": request_id,
                    "operation": "fetch",
                    "url": bounded_text(url),
                    "duration_ms": duration_ms,
                    "status": status,
                },
            )
            if provider_called:
                METRICS.increment(
                    "testbed_gateway_provider_requests_total",
                    labels={"provider": "exa", "operation": "fetch", "status": status},
                )
                METRICS.increment(
                    "testbed_gateway_provider_duration_seconds_sum",
                    labels={"provider": "exa", "operation": "fetch"},
                    value=duration_ms / 1000,
                )
            log_event(
                "web_request_completed",
                run_id=self.run_id,
                request_id=request_id,
                operation="fetch",
                provider="exa",
                provider_called=provider_called,
                duration_ms=duration_ms,
                status=status,
            )

    async def admit_model(self, provider: str, request: Request) -> None:
        if self.allowed_models is None:
            self.ledger.reserve("model_requests")
            return
        payload = await request.json()
        if (not isinstance(payload, dict) or not isinstance(payload.get("model"), str)
                or (provider, payload["model"]) not in self.allowed_models):
            raise ValueError("model is not authorized for this run")
        from gateway_models import validate_declared_request
        validate_declared_request(payload, pricing_for_request(provider, payload["model"]))
        self.ledger.admit_model(request.state.request_id)

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
        await self.admit_model(provider, request)
        started = time.monotonic()
        status = "error"
        usage: dict[str, int] = {}
        model = "unknown"
        request_pricing: dict[str, Any] | None = None
        request_id = request.state.request_id
        finalized = False
        upstream_status = None

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

        response_body = bytearray()
        content_type = "application/json"
        try:
            body = await request.body()
            try:
                payload = json.loads(body)
            except json.JSONDecodeError as error:
                raise ValueError("model request body must be valid JSON") from error
            if not isinstance(payload, dict):
                raise ValueError("model request body must be a JSON object")
            model = bounded_model_name(payload.get("model"))
            request_pricing = pricing_for_request(provider, model)
            if normalized == "chat/completions" and payload.get("stream"):
                payload["stream_options"] = {**(payload.get("stream_options") or {}), "include_usage": True}
            if provider == "openrouter" and model == "moonshotai/kimi-k3":
                reasoning = payload.get("reasoning")
                if reasoning is None:
                    reasoning = {}
                    payload["reasoning"] = reasoning
                if isinstance(reasoning, dict):
                    # OpenRouter returns provider-visible reasoning by default,
                    # but make that invariant explicit for research traces.
                    reasoning["exclude"] = False
            body = json.dumps(payload, separators=(",", ":")).encode()
            # Record how this agent composed the prompt (profile always; full
            # body only under TESTBED_CAPTURE_PROMPTS) -- lets us measure
            # cross-agent presentation bias from what actually hit the model.
            capture_prompt(request_id, provider, normalized, model, body, payload)
            self.ledger.timeline(
                {
                    "kind": "model.request",
                    "request_id": request_id,
                    "provider": provider,
                    "operation": normalized,
                    "model": model,
                    "prompt_profile": prompt_profile(payload, body),
                    "request": payload,
                }
            )
            upstream_base = os.environ.get(
                cfg["upstream_env"], cfg["upstream_default"]
            ).rstrip("/")
            upstream_request = self.client.build_request(
                request.method,
                f"{upstream_base}/{normalized}",
                headers={
                    # API profiles receive a gateway-owned secret. Subscription
                    # profiles explicitly forward Codex's ChatGPT bearer token.
                    **provider_auth_headers(provider, request.headers),
                    "content-type": request.headers.get(
                        "content-type", "application/json"
                    ),
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
                        and not (name == "chatgpt-account-id"
                                 and os.environ.get("DUNGENESS_CHATGPT_AUTH_FILE"))
                    },
                },
                params=request.query_params,
                content=body,
            )
            upstream = await self.client.send(upstream_request, stream=True)
            upstream_status = upstream.status_code
            content_type = upstream.headers.get("content-type", "application/json")
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

            if "text/event-stream" in content_type:
                # Decouple upstream draining from the client connection. A pump
                # task reads the WHOLE upstream so the provider's final usage
                # event is captured for accounting even if the agent disconnects
                # early (common with Codex -- `stream_interrupted`). Chunks are
                # relayed to the agent via an unbounded queue; if the agent goes
                # away, the pump keeps draining upstream to completion and then
                # finalizes. Without this, an interrupted request logs zero tokens
                # yet the provider still billed it.
                relay: asyncio.Queue[bytes | None] = asyncio.Queue()

                async def pump() -> None:
                    nonlocal status
                    try:
                        async for chunk in upstream.aiter_raw():
                            response_body.extend(chunk)
                            relay.put_nowait(chunk)
                    except BaseException:
                        status = "stream_interrupted"
                    finally:
                        relay.put_nowait(None)
                        await upstream.aclose()
                        finalize(bytes(response_body), content_type)

                pump_task = asyncio.ensure_future(pump())
                BACKGROUND_TASKS.add(pump_task)
                pump_task.add_done_callback(BACKGROUND_TASKS.discard)

                async def stream_chunks() -> AsyncIterator[bytes]:
                    # The agent may stop reading (disconnect); that cancels this
                    # generator but NOT the pump, which finishes accounting.
                    while True:
                        chunk = await relay.get()
                        if chunk is None:
                            break
                        yield chunk

                return StreamingResponse(
                    stream_chunks(),
                    status_code=upstream.status_code,
                    headers=response_headers,
                )

            try:
                response_body.extend(await upstream.aread())
            except BaseException:
                status = "stream_interrupted"
                raise
            finally:
                await upstream.aclose()
            finalize(bytes(response_body), content_type)
            return Response(
                bytes(response_body),
                status_code=upstream.status_code,
                headers=response_headers,
            )
        except BaseException:
            finalize(bytes(response_body), content_type)
            raise

    async def proxy_kimi(
        self,
        provider: str,
        path: str,
        request: Request,
    ) -> Response:
        """Translate Codex Responses traffic to Kimi Chat Completions."""

        config = MODEL_PROVIDERS.get(provider)
        if config is None or config.get("adapter") != "responses-to-chat":
            raise ValueError(f"unsupported Kimi adapter provider: {provider}")
        normalized = path.strip("/")
        if normalized not in config["routes"]:
            return JSONResponse(
                {"error": "unsupported model operation"}, status_code=404
            )
        await self.admit_model(provider, request)
        started = time.monotonic()
        status = "error"
        response_body = bytearray()
        request_id = request.state.request_id
        model = "unknown"
        request_pricing: dict[str, Any] | None = None
        finalized = False
        payload: dict[str, Any] = {}

        def trace(event: dict[str, Any]) -> None:
            record = {
                "request_id": request_id,
                "provider": provider,
                "model": model,
                **event,
            }
            self.ledger.timeline(
                {
                    "kind": "model.provider_event",
                    **record,
                }
            )
            for index, reasoning in enumerate(
                extract_visible_reasoning_events(event.get("event"))
            ):
                self.ledger.timeline(
                    {
                        "kind": "model.reasoning",
                        "request_id": request_id,
                        "provider": provider,
                        "model": model,
                        "source": reasoning["source"],
                        "stage": event.get("stage"),
                        "index": index,
                        "text": reasoning["text"],
                    }
                )

        def finalize(content_type: str) -> None:
            nonlocal finalized
            if finalized:
                return
            finalized = True
            usage = extract_usage(bytes(response_body), content_type)
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
            billed_usd = usd if config.get("billed", True) and not (request_pricing or {}).get("text_only") else None
            self.ledger.add_model_usage(
                billed_tokens=billed_tokens,
                normalized_usd=usd,
                billed_usd=billed_usd,
            )
            duration_ms = round((time.monotonic() - started) * 1000)
            response_documents = decode_response_documents(
                bytes(response_body), content_type
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
            self.ledger.record(
                "model",
                {
                    "request_id": request_id,
                    "provider": provider,
                    "model": model,
                    **usage,
                    "billed_tokens": billed_tokens,
                    "usd": usd,
                    "normalized_usd": usd,
                    "billed_usd": billed_usd,
                    "pricing_tier": pricing_tier,
                    "accounting_method": "gateway" if usage else "unavailable",
                    "duration_ms": duration_ms,
                    "status": status,
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

        try:
            body = await request.body()
            try:
                parsed_payload = json.loads(body)
            except json.JSONDecodeError as error:
                raise ValueError("model request body must be valid JSON") from error
            if not isinstance(parsed_payload, dict):
                raise ValueError("model request body must be a JSON object")
            payload = parsed_payload
            model = bounded_model_name(payload.get("model"))
            request_pricing = pricing_for_request(provider, model)
            capture_prompt(request_id, provider, normalized, model, body, payload)
            self.ledger.timeline(
                {
                    "kind": "model.request",
                    "request_id": request_id,
                    "provider": provider,
                    "operation": normalized,
                    "model": model,
                    "prompt_profile": prompt_profile(payload, body),
                    "request": payload,
                }
            )
            result = await self._request_kimi(
                payload,
                api_base=os.environ.get(
                    str(config["upstream_env"]),
                    str(config["upstream_default"]),
                ).rstrip("/"),
                api_key=os.environ[str(config["api_key_env"])],
                trace=trace,
            )

            if hasattr(result, "__aiter__"):
                if not isinstance(result, NativeReasoningStream):
                    result = NativeReasoningStream(result)
                relay: asyncio.Queue[bytes | None] = asyncio.Queue()

                async def pump() -> None:
                    nonlocal status
                    try:
                        async for event in result:  # type: ignore[union-attr]
                            document = dump_adapter_event(event)
                            trace(
                                {
                                    "stage": "normalized",
                                    "protocol": "openai-responses",
                                    "event": document,
                                }
                            )
                            event_type = str(document.get("type") or "message")
                            encoded = (
                                f"event: {event_type}\n"
                                f"data: {json.dumps(document, separators=(',', ':'))}\n\n"
                            ).encode()
                            response_body.extend(encoded)
                            relay.put_nowait(encoded)
                        done = b"data: [DONE]\n\n"
                        response_body.extend(done)
                        relay.put_nowait(done)
                        status = "success"
                    except BaseException:
                        status = "stream_interrupted"
                    finally:
                        relay.put_nowait(None)
                        finalize("text/event-stream")

                pump_task = asyncio.ensure_future(pump())
                BACKGROUND_TASKS.add(pump_task)
                pump_task.add_done_callback(BACKGROUND_TASKS.discard)

                async def stream_chunks() -> AsyncIterator[bytes]:
                    while True:
                        chunk = await relay.get()
                        if chunk is None:
                            break
                        yield chunk

                return StreamingResponse(
                    stream_chunks(),
                    status_code=200,
                    headers={
                        "content-type": "text/event-stream",
                        "cache-control": "no-cache",
                    },
                )

            document = dump_adapter_event(result)
            trace(
                {
                    "stage": "normalized",
                    "protocol": "openai-responses",
                    "event": document,
                }
            )
            response_body.extend(
                json.dumps(document, separators=(",", ":")).encode()
            )
            status = "success"
            finalize("application/json")
            return JSONResponse(document)
        except BaseException:
            finalize("text/event-stream" if payload.get("stream") else "application/json")
            raise
