"""Bounded I/O and credential-safe responses for the run-scoped gateway."""
import asyncio
import json
import re
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


def safe_provider_error(status, request_id):
    code = {
        400: "provider_invalid_request", 401: "provider_authentication_failed",
        403: "provider_access_denied", 404: "provider_model_unavailable",
        429: "provider_rate_limited",
    }.get(status, "provider_unavailable" if status >= 500 else "provider_request_failed")
    return JSONResponse({"error": {
        "code": code, "message": "The model provider rejected or could not complete the request.",
        "request_id": request_id, "upstream_status": status,
        "retryable": status in (408, 429, 500, 502, 503, 504),
    }}, status_code=status if 400 <= status <= 599 else 502)


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
            return await JSONResponse({"error": {"code": "gateway_capacity", "retryable": True}},
                                      status_code=429)(scope, receive, send)
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
                            return await JSONResponse({"error": {"code": "request_too_large", "limit": limit}},
                                                      status_code=413)(scope, receive, send)
                        if not message.get("more_body", False):
                            break
            except TimeoutError:
                return await JSONResponse({"error": {"code": "request_body_timeout"}},
                                          status_code=408)(scope, receive, send)
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
