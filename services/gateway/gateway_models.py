"""Model-provider configuration and protocol parsing helpers."""

from __future__ import annotations

from collections import defaultdict
import gzip
import json
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from provider_profiles import PROFILES
from gateway_auth import authentication_headers, profile_authentication
from typing import Any
import zlib


OPENAI_ROUTES = {"responses", "chat/completions", "embeddings", "models"}
ANTHROPIC_ROUTES = {"messages", "messages/count_tokens"}
OPENROUTER_ROUTES = {
    "responses",
    "chat/completions",
    "completions",
    "messages",
    "models",
}
CHATGPT_ROUTES = {"responses", "responses/compact"}
MOONSHOT_ROUTES = {"chat/completions"}
KIMI_CODE_ROUTES = {"chat/completions"}

def validate_declared_request(payload, pricing):
    """Keep measured inference on the exact declared model and priced units."""
    if any(key in payload for key in ("models", "route", "plugins", "web_search_options")):
        raise ValueError("model fallbacks and provider-hosted paid tools need separate accounting")
    if payload.get("background"):
        raise ValueError("background inference cannot settle within this request")
    if payload.get("service_tier") not in (None, "auto", "default"):
        raise ValueError("service tiers require a separate reference pricing policy")

    def tools(items):
        if not isinstance(items, list):
            raise ValueError("tools must be a list")
        for tool in items:
            if not isinstance(tool, dict) or tool.get("type", "function") not in (
                "function", "custom", "namespace", "local_shell", "shell", "apply_patch",
                "bash_20250124", "text_editor_20250124", "text_editor_20250429",
                "text_editor_20250728", "memory_20250818", "tool_search",
            ):
                raise ValueError("only harness-executed tools are metered by this contract")
            if tool.get("type") == "namespace":
                tools(tool.get("tools", []))
    tools(payload.get("tools", []))
    if not pricing.get("text_only"):
        return
    media_types = {"image", "image_url", "input_image", "audio", "input_audio",
                   "file", "input_file", "video", "video_url"}

    def content(value):
        if isinstance(value, list):
            for item in value:
                content(item)
        elif isinstance(value, dict):
            if (isinstance(value.get("type"), str) and value["type"] in media_types
                    or set(value) & {"image_url", "input_audio", "video_url"}):
                raise ValueError("this reference pricing snapshot supports text input only")
            # Tool arguments are opaque data, not protocol-level media. A
            # harness may manipulate JSON containing keys such as image_url.
            for key, item in value.items():
                if key not in {"input", "arguments"}:
                    content(item)
    if payload.get("modalities", ["text"]) != ["text"] or "audio" in payload:
        raise ValueError("this reference pricing snapshot supports text output only")
    content(payload.get("input", []))
    content(payload.get("messages", []))


def decode_body(body: bytes) -> bytes:
    """Decompress a response body if the provider compressed it.

    The gateway forwards `accept-encoding: identity` upstream so responses are
    normally uncompressed, but decompress defensively (gzip/deflate) so usage
    accounting never silently fails on a compressed body -- the exact bug where
    a gzipped SSE stream parsed to zero tokens.
    """
    if body[:2] == b"\x1f\x8b":  # gzip magic
        try:
            return gzip.decompress(body)
        except (OSError, zlib.error):
            return body
    return body


def is_sse_body(body: bytes, content_type: str) -> bool:
    """Recognize SSE even when an upstream labels the stream as JSON."""

    if "text/event-stream" in content_type.lower():
        return True
    stripped = decode_body(body).lstrip()
    return stripped.startswith((b"event:", b"data:"))


def _prompt_text_len(value: Any) -> int:
    """Approximate character length of a prompt fragment across provider shapes
    (strings, content-block lists, message dicts). Structural keys are skipped."""
    if isinstance(value, str):
        return len(value)
    if isinstance(value, list):
        return sum(_prompt_text_len(item) for item in value)
    if isinstance(value, dict):
        return sum(
            _prompt_text_len(v)
            for k, v in value.items()
            if k not in ("type", "role", "name", "id", "tool_call_id", "cache_control")
        )
    return 0


def prompt_profile(payload: Any, body: bytes) -> dict[str, Any]:
    """At-a-glance breakdown of one model request -- how the agent composed the
    prompt (system / per-role / tools sizes, counts, approx tokens) -- so agents
    can be compared without diffing raw megabytes. Sizes only, never content."""
    if not isinstance(payload, dict):
        return {"total_bytes": len(body), "approx_tokens": len(body) // 4}
    system_chars = _prompt_text_len(payload.get("system")) + _prompt_text_len(
        payload.get("instructions")
    )
    messages = payload.get("messages")
    if not isinstance(messages, list):
        messages = payload.get("input") if isinstance(payload.get("input"), list) else []
    by_role: dict[str, int] = {}
    if system_chars:
        by_role["system"] = system_chars
    for m in messages:
        role = m.get("role", "user") if isinstance(m, dict) else "user"
        by_role[role] = by_role.get(role, 0) + _prompt_text_len(
            m.get("content", m) if isinstance(m, dict) else m
        )
    tools = payload.get("tools") if isinstance(payload.get("tools"), list) else []
    return {
        "total_bytes": len(body),
        "approx_tokens": len(body) // 4,
        "messages": len(messages),
        "by_role_chars": by_role,
        "tools": {"count": len(tools), "chars": _prompt_text_len(tools)},
    }


def capture_prompt(
    request_id: str, provider: str, operation: str, model: str, body: bytes, payload: Any
) -> None:
    """Optionally retain the full effective request body for debugging.

    The always-on prompt profile is embedded in the canonical model.request
    event, so writing a second prompt-profiles stream would be redundant.
    """
    try:
        usage_dir = Path(os.environ.get("TESTBED_USAGE_DIR", "/var/lib/testbed/usage"))
        usage_dir.mkdir(parents=True, exist_ok=True)
        if os.environ.get("TESTBED_CAPTURE_PROMPTS", "").lower() in ("1", "true", "yes"):
            prompts = usage_dir / "prompts"
            prompts.mkdir(parents=True, exist_ok=True)
            (prompts / f"{request_id}.json").write_bytes(body)
    except OSError:
        pass


def decode_response_documents(body: bytes, content_type: str) -> list[Any]:
    """Decode a JSON response or ordered SSE data documents for trace storage."""

    body = decode_body(body)
    if is_sse_body(body, content_type):
        documents: list[Any] = []
        for line in body.splitlines():
            if not line.startswith(b"data:"):
                continue
            data = line[5:].strip()
            if not data or data == b"[DONE]":
                continue
            try:
                documents.append(json.loads(data))
            except (json.JSONDecodeError, UnicodeDecodeError):
                documents.append(
                    {
                        "type": "unparsed_sse_data",
                        "text": data.decode("utf-8", errors="replace"),
                    }
                )
        return documents
    if not body:
        return []
    try:
        return [json.loads(body)]
    except (json.JSONDecodeError, UnicodeDecodeError):
        return [{"type": "unparsed_response", "text": body.decode("utf-8", errors="replace")}]


def extract_usage(body: bytes, content_type: str) -> dict[str, int]:
    """Normalize usage from JSON responses or buffered OpenAI SSE events."""

    body = decode_body(body)
    candidates: list[dict[str, Any]] = []
    if is_sse_body(body, content_type):
        for line in body.splitlines():
            if line.startswith(b"data: ") and line[6:] != b"[DONE]":
                try:
                    value = json.loads(line[6:])
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue  # skip a malformed line, don't drop the whole stream
                if isinstance(value, dict):
                    candidates.append(value)
    else:
        try:
            value = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        if isinstance(value, dict):
            candidates.append(value)

    for value in reversed(candidates):
        raw = value.get("usage")
        if not isinstance(raw, dict):
            response = value.get("response")
            raw = response.get("usage") if isinstance(response, dict) else None
        if not isinstance(raw, dict):
            continue
        input_tokens = int(raw.get("input_tokens", raw.get("prompt_tokens", 0)) or 0)
        output_tokens = int(
            raw.get("output_tokens", raw.get("completion_tokens", 0)) or 0
        )
        input_details = raw.get(
            "input_tokens_details", raw.get("prompt_tokens_details", {})
        ) or {}
        output_details = raw.get(
            "output_tokens_details", raw.get("completion_tokens_details", {})
        ) or {}
        cached = int(
            input_details.get("cached_tokens", 0)
            if isinstance(input_details, dict)
            else 0
        )
        cache_write = int(
            input_details.get("cache_write_tokens", 0)
            if isinstance(input_details, dict)
            else 0
        )
        reasoning = int(
            output_details.get("reasoning_tokens", 0)
            if isinstance(output_details, dict)
            else 0
        )
        total = int(raw.get("total_tokens", input_tokens + output_tokens) or 0)
        return {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached,
            "cache_write_input_tokens": cache_write,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning,
            "total_tokens": total,
        }
    return {}


def extract_reasoning_summaries(body: bytes, content_type: str) -> list[str]:
    """Extract readable OpenAI reasoning summaries, never hidden reasoning tokens."""

    body = decode_body(body)
    events: list[dict[str, Any]] = []
    if is_sse_body(body, content_type):
        for line in body.splitlines():
            if not line.startswith(b"data:"):
                continue
            data = line[5:].strip()
            if not data or data == b"[DONE]":
                continue
            try:
                value = json.loads(data)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(value, dict):
                events.append(value)
    else:
        try:
            value = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []
        if isinstance(value, dict):
            events.append(value)

    summaries: list[str] = []
    deltas: dict[int, list[str]] = defaultdict(list)

    def add(text: Any) -> None:
        if isinstance(text, str) and text and text not in summaries:
            summaries.append(text)

    for event in events:
        kind = event.get("type")
        if kind == "response.reasoning_summary_text.delta":
            index = int(event.get("summary_index", 0) or 0)
            delta = event.get("delta")
            if isinstance(delta, str):
                deltas[index].append(delta)
        elif kind == "response.reasoning_summary_text.done":
            add(event.get("text"))
        elif kind == "response.reasoning_summary_part.done":
            part = event.get("part")
            if isinstance(part, dict) and part.get("type") == "summary_text":
                add(part.get("text"))

        response = event.get("response")
        document = response if isinstance(response, dict) else event
        output = document.get("output")
        if not isinstance(output, list):
            continue
        for item in output:
            if not isinstance(item, dict) or item.get("type") != "reasoning":
                continue
            summary = item.get("summary")
            if not isinstance(summary, list):
                continue
            for part in summary:
                if isinstance(part, dict) and part.get("type") == "summary_text":
                    add(part.get("text"))

    if not summaries:
        for index in sorted(deltas):
            add("".join(deltas[index]))
    return summaries


def extract_visible_reasoning_events(value: Any) -> list[dict[str, str]]:
    """Collect every provider-visible reasoning representation in response order."""

    found: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    reasoning_deltas: list[str] = []

    def add(source: str, text: Any) -> None:
        if not isinstance(text, str) or not text:
            return
        key = (source, text)
        if key in seen:
            return
        seen.add(key)
        found.append({"source": source, "text": text})

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            kind = item.get("type")
            if kind == "response.reasoning.delta":
                delta = item.get("delta")
                if isinstance(delta, str):
                    reasoning_deltas.append(delta)
            elif isinstance(kind, str) and kind in {
                "response.reasoning.done",
                "reasoning.text",
            }:
                add(str(kind), item.get("text"))

            add("reasoning_content", item.get("reasoning_content"))
            add("reasoning", item.get("reasoning"))

            details = item.get("reasoning_details")
            if isinstance(details, list):
                for detail in details:
                    if not isinstance(detail, dict):
                        continue
                    detail_type = detail.get("type")
                    source = (
                        str(detail_type)
                        if isinstance(detail_type, str)
                        else "reasoning_details"
                    )
                    add(source, detail.get("text"))

            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    if reasoning_deltas:
        add("response.reasoning.delta", "".join(reasoning_deltas))
    return found


def extract_visible_reasoning(value: Any) -> list[str]:
    """Compatibility wrapper returning only provider-visible reasoning text."""

    return [
        event["text"]
        for event in extract_visible_reasoning_events(value)
    ]


def extract_anthropic_usage(body: bytes, content_type: str) -> dict[str, int]:
    """Normalize usage from an Anthropic Messages response (SSE or JSON).

    Input usage arrives once in `message_start.message.usage`; the running
    output count arrives in successive `message_delta.usage`. Merge them, and
    fold Anthropic's cache buckets into the same schema the OpenAI path uses
    (our `input_tokens` counts ALL input incl. cache; `cached_input_tokens` is
    the discounted cache-read portion).
    """

    body = decode_body(body)
    events: list[dict[str, Any]] = []
    if "text/event-stream" in content_type:
        for line in body.splitlines():
            if line.startswith(b"data:"):
                data = line[5:].strip()
                if data and data != b"[DONE]":
                    try:
                        value = json.loads(data)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue  # skip a malformed line, keep the rest
                    if isinstance(value, dict):
                        events.append(value)
    else:
        try:
            value = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        if isinstance(value, dict):
            events.append(value)

    inp = cache_read = cache_create = out = 0
    found = False
    for value in events:
        kind = value.get("type")
        if kind == "message_start":
            message = value.get("message")
            raw = message.get("usage") if isinstance(message, dict) else None
        else:  # message_delta, a non-stream "message", or a bare usage object
            raw = value.get("usage")
        if not isinstance(raw, dict):
            continue
        found = True
        if raw.get("input_tokens") is not None:
            inp = int(raw.get("input_tokens") or 0)
        if raw.get("cache_read_input_tokens") is not None:
            cache_read = int(raw.get("cache_read_input_tokens") or 0)
        if raw.get("cache_creation_input_tokens") is not None:
            cache_create = int(raw.get("cache_creation_input_tokens") or 0)
        if raw.get("output_tokens") is not None:
            out = int(raw.get("output_tokens") or 0)
    if not found:
        return {}
    total_input = inp + cache_read + cache_create
    return {
        "input_tokens": total_input,
        "cached_input_tokens": cache_read,
        "cache_write_input_tokens": cache_create,
        "output_tokens": out,
        "reasoning_tokens": 0,
        "total_tokens": total_input + out,
    }


# Per-provider proxy configuration. Model calls for every provider share the
# same streaming, accounting, and budget machinery (proxy_model); only the
# route allowlist, upstream origin, auth header, pass-through headers, and usage
# parser differ.
MODEL_PROVIDERS: dict[str, dict[str, Any]] = {
    "openai": {
        "authentication": {"sources": [{"headers": {
            "authorization": {"env": "OPENAI_API_KEY", "prefix": "Bearer "},
        }}]},
        "routes": OPENAI_ROUTES,
        "upstream_env": "OPENAI_UPSTREAM_BASE_URL",
        "upstream_default": "https://api.openai.com/v1",
        "auth": "gateway_secret",
        "billed": True,
        "passthrough": (
            "openai-beta",
            "idempotency-key",
        ),
        "extract_usage": extract_usage,
    },
    "anthropic": {
        "authentication": {"sources": [{"headers": {
            "x-api-key": {"env": "ANTHROPIC_API_KEY"},
            "anthropic-version": {"env": "ANTHROPIC_VERSION", "default": "2023-06-01"},
        }}]},
        "routes": ANTHROPIC_ROUTES,
        "upstream_env": "ANTHROPIC_UPSTREAM_BASE_URL",
        "upstream_default": "https://api.anthropic.com/v1",
        "auth": "gateway_secret",
        "billed": True,
        "passthrough": ("anthropic-beta", "anthropic-version"),
        "extract_usage": extract_anthropic_usage,
    },
    "openrouter": {
        "authentication": {"sources": [{"headers": {
            "authorization": {"env": "OPENROUTER_API_KEY", "prefix": "Bearer "},
        }}]},
        "routes": OPENROUTER_ROUTES,
        "upstream_env": "OPENROUTER_UPSTREAM_BASE_URL",
        "upstream_default": "https://openrouter.ai/api/v1",
        "auth": "gateway_secret",
        "billed": True,
        # OpenRouter accepts (and echoes) optional attribution headers. The
        # Anthropic headers matter only for the `messages` operation, where
        # Claude Code declares beta features (prompt caching, thinking, 1M
        # context) and the API version it speaks.
        "passthrough": (
            "http-referer",
            "x-title",
            "openai-beta",
            "anthropic-beta",
            "anthropic-version",
        ),
        "extract_usage": extract_usage,
    },
    "openai-chatgpt": {
        "authentication": {"sources": [
            {"file_env": "DUNGENESS_CHATGPT_AUTH_FILE", "headers": {
                "authorization": {"path": ["tokens", "access_token"], "prefix": "Bearer "},
                "chatgpt-account-id": {"path": ["tokens", "account_id"]},
            }},
            # Older native-agent runs carry their own bearer credential. A
            # configured file always takes precedence and fails closed on error.
            {"headers": {"authorization": {
                "request_header": "authorization", "require_prefix": "Bearer ",
            }}},
        ]},
        "routes": CHATGPT_ROUTES,
        "upstream_env": "CHATGPT_UPSTREAM_BASE_URL",
        "upstream_default": "https://chatgpt.com/backend-api/codex",
        "auth": "forward_openai_auth",
        "billed": False,
        # ChatGPT's Codex backend uses these client/account headers in addition
        # to the bearer credential. Keep this a fixed allowlist; never forward
        # arbitrary agent-controlled headers.
        "passthrough": (
            "chatgpt-account-id",
            "originator",
            "version",
            "session_id",
            "session-id",
            "thread-id",
            "conversation_id",
            "x-openai-subagent",
            "x-client-request-id",
            "x-codex-turn-metadata",
            "x-codex-installation-id",
            "x-oai-attestation",
            "x-responsesapi-include-timing",
            "traceparent",
            "user-agent",
            "openai-beta",
        ),
        "extract_usage": extract_usage,
    },
    "moonshot": {
        "authentication": {"sources": [{"headers": {
            "authorization": {"env": "MOONSHOT_API_KEY", "prefix": "Bearer "},
        }}]},
        "routes": MOONSHOT_ROUTES,
        "upstream_env": "MOONSHOT_UPSTREAM_BASE_URL",
        "upstream_default": "https://api.moonshot.ai/v1",
        "auth": "gateway_secret",
        "billed": True,
        "api_key_env": "MOONSHOT_API_KEY",
        "passthrough": (),
        "extract_usage": extract_usage,
    },
    "kimi-code": {
        "authentication": {"sources": [{"headers": {
            "authorization": {"env": "KIMI_CODE_API_KEY", "prefix": "Bearer "},
        }}]},
        "routes": KIMI_CODE_ROUTES,
        "upstream_env": "KIMI_CODE_UPSTREAM_BASE_URL",
        "upstream_default": "https://api.kimi.com/coding/v1",
        "auth": "gateway_secret",
        "billed": False,
        "api_key_env": "KIMI_CODE_API_KEY",
        "passthrough": (),
        "extract_usage": extract_usage,
    },
}


def provider_auth_headers(
    provider: str,
    request_headers: Any | None = None,
) -> dict[str, str]:
    """Resolve upstream authentication without ever logging credential values."""

    cfg = MODEL_PROVIDERS.get(provider)
    if cfg is None:
        raise ValueError("Unknown authentication provider.")
    return authentication_headers(cfg["authentication"], request_headers)


for _name, _profile in PROFILES.items():
    MODEL_PROVIDERS[_name] = {
        'authentication': profile_authentication(_profile),
        'routes': set(_profile['routes']),
        'upstream_env': _name.upper().replace('-', '_') + '_UPSTREAM_BASE_URL',
        'upstream_default': _profile['base_url'],
        'auth': 'gateway_secret', 'billed': _profile['billed'],
        'passthrough': (), 'extract_usage': extract_usage,
    }


def usage_extractor(cfg: dict[str, Any], operation: str):
    """Pick the usage parser for one operation.

    Providers default to one response format, but OpenRouter serves both
    OpenAI-compatible operations and the Anthropic Messages API. The Messages
    operation reports Anthropic-shaped usage (split across `message_start` and
    `message_delta` when streaming) regardless of which provider fronts it.
    """

    if operation.startswith("messages"):
        return extract_anthropic_usage
    return cfg["extract_usage"]
