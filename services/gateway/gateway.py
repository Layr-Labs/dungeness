#!/usr/bin/env python3
"""Starlette entrypoint for the per-run research gateway.

The request runtime and supporting policy, protocol, pricing, and accounting
code live in the ``gateway_*`` modules beside this file.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
import hmac
import hashlib
import re
import json
import os
import time
from typing import Any

import httpx

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route
import uvicorn

# Re-export the historical gateway.py surface while implementation lives in
# focused modules. Existing tests and downstream imports therefore keep working.
from gateway_models import (
    ANTHROPIC_ROUTES,
    CHATGPT_ROUTES,
    KIMI_CODE_ROUTES,
    MODEL_PROVIDERS,
    MOONSHOT_ROUTES,
    OPENAI_ROUTES,
    OPENROUTER_ROUTES,
    RESEARCH_STATE_CONTEXT_MARKER,
    capture_prompt,
    decode_body,
    decode_response_documents,
    extract_anthropic_usage,
    extract_reasoning_summaries,
    extract_usage,
    extract_visible_reasoning,
    extract_visible_reasoning_events,
    inject_research_state,
    is_sse_body,
    prompt_profile,
    provider_auth_headers,
    research_state_context,
    usage_extractor,
)
from gateway_pricing import (
    MODEL_PRICING,
    PRICING_PATH,
    PRICING_RATE_FIELDS,
    input_token_buckets,
    load_model_pricing,
    pricing_for_request,
    request_budget_tokens,
    request_pricing_rates,
    request_usd,
    validate_pricing_rates,
)
from gateway_runtime import (
    BACKGROUND_TASKS,
    CACHED_TOKEN_WEIGHT,
    EXA_CONTENTS_URL,
    EXA_SEARCH_URL,
    Gateway,
)
from gateway_usage import (
    EVENT_SCHEMA_VERSION,
    EVENT_TOKEN_FILENAME,
    INTERNAL_EVENT_KINDS,
    MAX_INTERNAL_EVENT_BYTES,
    METRICS,
    REQUEST_ID_RE,
    BudgetExceeded,
    Metrics,
    UsageLedger,
    append_jsonl_locked,
    bounded_model_name,
    bounded_text,
    log_event,
    metric_labels,
    safe_request_id,
    set_active_ledger,
    utc_now,
)
from gateway_web import (
    ARXIV_ID_RE,
    CONTENT_BEARING_RESULT_FIELDS,
    DATELESS_CATEGORIES,
    FULL_GIT_SHA_RE,
    SEARCH_TYPES,
    WAYBACK_SNAPSHOT_RE,
    approve_historical_result,
    historical_date_evidence,
    immutable_historical_url,
    make_search_payload,
    mutable_url_reason,
    parse_utc,
    positive_int,
)
from kimi_adapter import model_dump as dump_adapter_event
from kimi_adapter import NativeReasoningStream
from kimi_adapter import request_kimi


_BACKGROUND_TASKS = BACKGROUND_TASKS


# A Compose deployment creates exactly one process for exactly one run, so the
# run-scoped gateway and ledger can be initialized once at process startup.
gateway = Gateway(
    # Resolve the entrypoint symbol at call time so existing integrations can
    # replace ``gateway.request_kimi`` without reaching into implementation
    # modules.
    kimi_request=lambda *args, **kwargs: request_kimi(*args, **kwargs),
)


def instrumentation_route(path: str) -> str:
    """Return a bounded route label; never use an arbitrary URL path as a label."""

    if path.startswith("/model/openai/v1/"):
        return "/model/openai/v1/{operation}"
    if path.startswith("/model/anthropic/v1/"):
        return "/model/anthropic/v1/{operation}"
    if path.startswith("/model/openrouter/v1/"):
        return "/model/openrouter/v1/{operation}"
    if path.startswith("/model/chatgpt/v1/"):
        return "/model/chatgpt/v1/{operation}"
    if path.startswith("/model/moonshot/v1/"):
        return "/model/moonshot/v1/{operation}"
    if path.startswith("/model/kimi-code/v1/"):
        return "/model/kimi-code/v1/{operation}"
    if path in {
        "/healthz",
        "/status",
        "/task",
        "/metrics",
        "/internal/events",
        "/web/search",
        "/web/fetch",
    }:
        return path
    return "unmatched"


class RequestInstrumentationMiddleware(BaseHTTPMiddleware):
    """Attach request IDs and emit bounded-cardinality metrics and JSON logs."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = safe_request_id(request.headers.get("x-request-id"))
        request.state.request_id = request_id
        started = time.monotonic()
        status = 500
        error_type: str | None = None
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["x-request-id"] = request_id
            return response
        except Exception as error:
            error_type = type(error).__name__
            raise
        finally:
            duration_seconds = time.monotonic() - started
            route = instrumentation_route(request.url.path)
            METRICS.observe_http(
                request.method, route, status, duration_seconds
            )
            # Successful probes are represented in metrics but omitted from the
            # event log to avoid health-check and scraper noise.
            if status != 200 or route not in {
                "/healthz",
                "/metrics",
                "/internal/events",
            }:
                log_event(
                    "http_request_completed",
                    run_id=gateway.run_id,
                    request_id=request_id,
                    method=request.method,
                    route=route,
                    status_code=status,
                    duration_ms=round(duration_seconds * 1000),
                    error_type=error_type,
                    level="error" if status >= 500 else "info",
                )


def budget_rejected(request: Request, operation: str, error: BudgetExceeded) -> Response:
    """Instrument a fail-closed budget response without exposing request content."""

    METRICS.increment(
        "testbed_gateway_budget_rejections_total", labels={"operation": operation}
    )
    log_event(
        "budget_rejected",
        run_id=gateway.run_id,
        request_id=request.state.request_id,
        operation=operation,
        reason=str(error),
        level="warning",
    )
    return JSONResponse({"error": str(error)}, status_code=429)


async def health(_request: Request) -> Response:
    return JSONResponse({"status": "ok", "run_id": gateway.run_id})


async def assigned_task(request: Request) -> Response:
    """Read only the task assigned by the trusted Compose configuration."""
    expected = os.environ.get("DUNGENESS_TASK_SHA256")
    if not expected:
        return JSONResponse({"error": "No problem service assigned."}, status_code=404)
    if request.url.query or not re.fullmatch(r"[0-9a-f]{64}", expected):
        return JSONResponse({"error": "Invalid task request or assignment."}, status_code=400)
    try:
        # Never use client-supplied URLs, forward auth headers or follow redirects.
        async with httpx.AsyncClient(trust_env=False, follow_redirects=False, timeout=5) as client:
            async with client.stream("GET", "http://problem:8091/task") as upstream:
                if upstream.status_code != 200:
                    raise ValueError("Task service unavailable")
                raw = bytearray()
                async for chunk in upstream.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > 256 * 1024:
                        raise ValueError("Task document too large")
        document = json.loads(raw)
        if not isinstance(document, dict) or document.get("schema_version") != 1:
            raise ValueError("Invalid task document")
        encoded = json.dumps(document, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()
        if hashlib.sha256(encoded).hexdigest() != expected:
            raise ValueError("Task document changed")
        return Response(encoded, media_type="application/json",
                        headers={"X-Task-SHA256": expected, "Cache-Control": "no-store"})
    except (httpx.HTTPError, ValueError, TypeError, OverflowError, RecursionError):
        return JSONResponse({"error": "Assigned problem unavailable or mismatched."}, status_code=502)


async def status(_request: Request) -> Response:
    return JSONResponse(gateway.ledger.status())


async def metrics(_request: Request) -> Response:
    return PlainTextResponse(
        METRICS.render(gateway.ledger), media_type="text/plain; version=0.0.4"
    )


def validate_internal_event(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ValueError("event must be a JSON object")
    source = document.get("source")
    kind = document.get("kind")
    if source == "research-state":
        if not isinstance(kind, str) or not kind.startswith("research_state."):
            raise ValueError("unsupported research-state event kind")
    elif source in INTERNAL_EVENT_KINDS:
        if kind not in INTERNAL_EVENT_KINDS[source]:
            raise ValueError("unsupported internal event kind")
    else:
        raise ValueError("unsupported internal event source")
    if document.get("run_id") not in {None, gateway.ledger.run_id}:
        raise ValueError("event run_id does not match this gateway")
    for field in ("event_id", "request_id"):
        value = document.get(field)
        if value is not None and (
            not isinstance(value, str) or not 1 <= len(value) <= 256
        ):
            raise ValueError(f"{field} must be bounded non-empty text")
    observed_at = document.get("observed_at")
    if observed_at is not None:
        if not isinstance(observed_at, str) or len(observed_at) > 64:
            raise ValueError("observed_at must be a bounded timestamp")
        parse_utc(observed_at)
    data = document.get("data", {})
    if not isinstance(data, dict):
        raise ValueError("event data must be a JSON object")
    return {
        "source": source,
        "kind": kind,
        "observed_at": observed_at,
        "event_id": document.get("event_id"),
        "request_id": document.get("request_id"),
        "data": data,
    }


async def internal_event(request: Request) -> Response:
    supplied = request.headers.get("x-dungeness-event-token", "")
    if not hmac.compare_digest(supplied, gateway.ledger.event_token):
        return JSONResponse({"error": "forbidden"}, status_code=403)
    body = await request.body()
    if len(body) > MAX_INTERNAL_EVENT_BYTES:
        return JSONResponse({"error": "event body is too large"}, status_code=413)
    try:
        document = json.loads(body or b"{}")
        event = validate_internal_event(document)
    except (json.JSONDecodeError, ValueError) as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    return JSONResponse(gateway.ledger.ingest(event))


async def web_search(request: Request) -> Response:
    payload: dict[str, Any] = {}
    try:
        payload = await request.json()
        return JSONResponse(
            await gateway.search(
                payload.get("query"),
                payload.get("options"),
                request.state.request_id,
            )
        )
    except BudgetExceeded as error:
        await gateway.notify_research_state(
            "/events/web-search",
            {
                "event_id": f"web-search:{request.state.request_id}",
                "query": bounded_text(payload.get("query")),
                "status": "budget_rejected",
            },
        )
        return budget_rejected(request, "web.search", error)
    except (ValueError, TypeError, KeyError) as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except httpx.HTTPError as error:
        return JSONResponse(
            {"error": f"Exa request failed: {type(error).__name__}"}, status_code=502
        )


async def web_fetch(request: Request) -> Response:
    try:
        payload = await request.json()
        return JSONResponse(
            await gateway.fetch(
                payload.get("url"),
                payload.get("options"),
                request.state.request_id,
            )
        )
    except BudgetExceeded as error:
        return budget_rejected(request, "web.fetch", error)
    except (ValueError, TypeError, KeyError) as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except httpx.HTTPError as error:
        return JSONResponse(
            {"error": f"Exa request failed: {type(error).__name__}"}, status_code=502
        )


async def model_openai(request: Request) -> Response:
    try:
        return await gateway.proxy_model("openai", request.path_params["path"], request)
    except BudgetExceeded as error:
        return budget_rejected(request, "model.openai", error)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except httpx.HTTPError as error:
        return JSONResponse(
            {"error": f"provider request failed: {type(error).__name__}"},
            status_code=502,
        )


async def model_anthropic(request: Request) -> Response:
    try:
        return await gateway.proxy_model(
            "anthropic", request.path_params["path"], request
        )
    except BudgetExceeded as error:
        return budget_rejected(request, "model.anthropic", error)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except httpx.HTTPError as error:
        return JSONResponse(
            {"error": f"provider request failed: {type(error).__name__}"},
            status_code=502,
        )


async def model_openrouter(request: Request) -> Response:
    try:
        return await gateway.proxy_model(
            "openrouter", request.path_params["path"], request
        )
    except BudgetExceeded as error:
        return budget_rejected(request, "model.openrouter", error)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except httpx.HTTPError as error:
        return JSONResponse(
            {"error": f"provider request failed: {type(error).__name__}"},
            status_code=502,
        )


async def model_chatgpt(request: Request) -> Response:
    try:
        return await gateway.proxy_model(
            "openai-chatgpt", request.path_params["path"], request
        )
    except BudgetExceeded as error:
        return budget_rejected(request, "model.openai-chatgpt", error)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except httpx.HTTPError as error:
        return JSONResponse(
            {"error": f"provider request failed: {type(error).__name__}"},
            status_code=502,
        )


async def model_moonshot(request: Request) -> Response:
    try:
        if request.path_params["path"].strip("/") == "chat/completions":
            return await gateway.proxy_model("moonshot", request.path_params["path"], request)
        return await gateway.proxy_kimi(
            "moonshot",
            request.path_params["path"],
            request,
        )
    except BudgetExceeded as error:
        return budget_rejected(request, "model.moonshot", error)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except Exception as error:
        log_event(
            "moonshot_adapter_failed",
            run_id=gateway.run_id,
            request_id=request.state.request_id,
            error_type=type(error).__name__,
            level="error",
        )
        return JSONResponse(
            {"error": f"provider request failed: {type(error).__name__}"},
            status_code=502,
        )


async def model_kimi_code(request: Request) -> Response:
    try:
        if request.path_params["path"].strip("/") == "chat/completions":
            return await gateway.proxy_model("kimi-code", request.path_params["path"], request)
        return await gateway.proxy_kimi(
            "kimi-code",
            request.path_params["path"],
            request,
        )
    except BudgetExceeded as error:
        return budget_rejected(request, "model.kimi-code", error)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except Exception as error:
        log_event(
            "kimi_code_adapter_failed",
            run_id=gateway.run_id,
            request_id=request.state.request_id,
            error_type=type(error).__name__,
            level="error",
        )
        return JSONResponse(
            {"error": f"provider request failed: {type(error).__name__}"},
            status_code=502,
        )


async def drain_background_tasks(timeout_seconds: float | None = None) -> None:
    """Finish detached response drains before the gateway process exits."""

    tasks = [task for task in list(_BACKGROUND_TASKS) if not task.done()]
    if not tasks:
        return
    if timeout_seconds is None:
        timeout_seconds = float(
            os.environ.get("GATEWAY_SHUTDOWN_DRAIN_SECONDS", "30")
        )

    done, pending = await asyncio.wait(tasks, timeout=max(0.0, timeout_seconds))
    if pending:
        log_event(
            "background_accounting_drain_timeout",
            run_id=gateway.run_id,
            pending_tasks=len(pending),
            timeout_seconds=timeout_seconds,
        )
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

    failures = 0
    for task in done:
        if task.cancelled():
            continue
        try:
            error = task.exception()
        except asyncio.CancelledError:
            continue
        if error is not None:
            failures += 1
    if failures:
        log_event(
            "background_accounting_task_failed",
            run_id=gateway.run_id,
            failed_tasks=failures,
        )


@asynccontextmanager
async def lifespan(_app: Starlette):
    set_active_ledger(gateway.ledger)
    log_event(
        "gateway_started",
        run_id=gateway.run_id,
        end_published_date=gateway.end_published_date,
        limits=gateway.ledger.limits,
    )
    try:
        yield
    finally:
        try:
            await drain_background_tasks()
        finally:
            gateway.ledger.flush_summary()
            await gateway.client.aclose()
            log_event("gateway_stopped", run_id=gateway.run_id)
            gateway.ledger.close()
            set_active_ledger(None)


app = Starlette(
    routes=[
        Route("/healthz", health, methods=["GET"]),
        Route("/status", status, methods=["GET"]),
        Route("/task", assigned_task, methods=["GET"]),
        Route("/metrics", metrics, methods=["GET"]),
        Route("/internal/events", internal_event, methods=["POST"]),
        Route("/web/search", web_search, methods=["POST"]),
        Route("/web/fetch", web_fetch, methods=["POST"]),
        Route(
            "/model/openai/v1/{path:path}", model_openai, methods=["GET", "POST"]
        ),
        Route(
            "/model/anthropic/v1/{path:path}",
            model_anthropic,
            methods=["GET", "POST"],
        ),
        Route(
            "/model/openrouter/v1/{path:path}",
            model_openrouter,
            methods=["GET", "POST"],
        ),
        Route(
            "/model/chatgpt/v1/{path:path}",
            model_chatgpt,
            methods=["GET", "POST"],
        ),
        Route(
            "/model/moonshot/v1/{path:path}",
            model_moonshot,
            methods=["POST"],
        ),
        Route(
            "/model/kimi-code/v1/{path:path}",
            model_kimi_code,
            methods=["POST"],
        ),
    ],
    lifespan=lifespan,
)
app.add_middleware(RequestInstrumentationMiddleware)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        access_log=False,
        log_level="warning",
    )
