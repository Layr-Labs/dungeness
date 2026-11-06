"""Bounded I/O and credential-safe responses for the run-scoped gateway."""
from gateway_errors import recovery
import asyncio
import json
import re
import uuid
from urllib.parse import quote

from starlette.responses import JSONResponse

MAX_REQUEST_BYTES = 32 * 1024 * 1024
MAX_RESPONSE_BYTES = 64 * 1024 * 1024
MAX_ACTIVE_REQUESTS = 8
REQUEST_BODY_TIMEOUT_SECONDS = 30


class ResponseLimitExceeded(Exception):
    pass


class SecretFilter:
    """Redact literal credentials across transport chunks, including JSON escapes.

    This is defense in depth against accidental credential echo, not a defense
    against a compromised provider deliberately encoding or transforming a key.
    A suffix is retained until it cannot be the beginning of a secret.
    """
    def __init__(self, values):
        variants = set()
        for value in values:
            if value:
                variants.update(v.encode() for v in (value, json.dumps(value)[1:-1], quote(value, safe="")))
        self.pattern = re.compile(b"|".join(re.escape(v) for v in sorted(variants, key=len, reverse=True))) if variants else None
        self.values = tuple(variants)
        self.starts = {value[0] for value in variants}
        self.keep = max(map(len, variants), default=1) - 1
        self.pending = b""

    def feed(self, chunk, *, final=False):
        data = self.pending + chunk
        if self.pattern is None:
            return data
        cutoff = len(data)
        if not final:
            # Hold only a possible credential prefix, not every short SSE event.
            # Long session tokens must not add a token-length latency to normal traffic.
            for start in range(max(0, len(data) - self.keep), len(data)):
                if data[start] in self.starts:
                    suffix = data[start:]
                    if any(len(suffix) < len(value) and value.startswith(suffix) for value in self.values):
                        cutoff = start
                        break
        output, position = [], 0
        for match in self.pattern.finditer(data):
            if match.start() >= cutoff:
                break
            output.extend((data[position:match.start()], b"[REDACTED]"))
            position = match.end()
        end = max(cutoff, position)
        output.append(data[position:end])
        self.pending = data[end:]
        return b"".join(output)


def safe_provider_error(status, request_id, *, accounting_complete=False):
    code = {
        400: "provider_invalid_request", 401: "provider_authentication_failed",
        403: "provider_access_denied", 404: "provider_model_unavailable",
        429: "provider_rate_limited",
    }.get(status, "provider_unavailable" if status >= 500 else "provider_request_failed")
    recovery_code = code if accounting_complete else "provider_accounting_incomplete"
    details = {**recovery(recovery_code, retryable=status in (408, 429, 500, 502, 503, 504),
                         action="check_accounting" if not accounting_complete else None),
               "recovery_code": recovery_code,
               "accounting_complete": accounting_complete, "upstream_request_sent": True}
    return JSONResponse({"error": {
        "code": code, "message": "The model provider rejected or could not complete the request.",
        "request_id": request_id, "upstream_status": status,
        **details,
    }}, status_code=status if 400 <= status <= 599 else 502,
        headers={"x-should-retry": "true" if details["retryable"] else "false"})


def admission_error(code, status, *, retryable=False, **details):
    # Body bounds run before request instrumentation. Generate a safe ID here.
    from gateway_usage import log_event
    identity = uuid.uuid4().hex
    info = {"code": code, "request_id": identity, "upstream_request_sent": False,
            **recovery(code, retryable=retryable), **details}
    log_event("model_request_rejected", **info)
    return JSONResponse({"error": info}, status_code=status,
                        headers={"x-request-id": identity,
                                 "x-should-retry": "true" if info["retryable"] else "false"})


class RequestBoundsMiddleware:
    """Bound request bodies before Starlette buffers them, and active model calls."""
    def __init__(self, app):
        self.app = app
        self.active = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        counted = scope["path"] not in {"/healthz", "/status", "/metrics"}
        limit = MAX_REQUEST_BYTES if counted else 1024
        if counted and self.active >= MAX_ACTIVE_REQUESTS:
            return await admission_error("gateway_capacity", 429, retryable=True)(scope, receive, send)
        # No await between checking and incrementing: atomic within the event loop.
        if counted:
            self.active += 1
        try:
            body = bytearray()
            try:
                async with asyncio.timeout(REQUEST_BODY_TIMEOUT_SECONDS):
                    while True:
                        message = await receive()
                        if message["type"] == "http.disconnect":
                            return
                        body.extend(message.get("body", b""))
                        if len(body) > limit:
                            return await admission_error("request_too_large", 413, limit=limit)(scope, receive, send)
                        if not message.get("more_body", False):
                            break
            except TimeoutError:
                return await admission_error("request_body_timeout", 408, retryable=True)(scope, receive, send)
            delivered = False

            async def bounded_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            await self.app(scope, bounded_receive, send)
        finally:
            if counted:
                self.active -= 1
