#!/usr/bin/env python3
"""Render a Dungeness gateway transcript as a self-contained HTML chat viewer.

The viewer shows, per model request, exactly what the gateway sent to the model
provider and what came back, so harness effects (injected research state, tool
trimming, persona rewrites, prompt-cache breaks) are visible at a glance.

Usage:
    python3 scripts/render_gateway_transcript.py runs/users/bx/<run-id> [-o out.html]

Standard library only. The output is a single HTML file with inline CSS and a
small amount of inline vanilla JavaScript; it opens offline.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections.abc import Iterable, Iterator
import glob
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RESEARCH_STATE_MARKER = "## Current Dungeness research-effort state (per-request)"
TRUNCATE_CHARS = 1500
REASONING_TRUNCATE_CHARS = 800
CYBERSECURITY_STATUS = "cybersecurity blocked"
CYBERSECURITY_DEFAULT_REASON = "Codex stopped the run under its cybersecurity policy"
CYBERSECURITY_MESSAGE_MARKERS = (
    "flagged for possible cybersecurity risk",
    "trusted access for cyber",
)

# Legacy GPT-5.6-sol normalized pricing for trajectory reconstruction.
# Canonical runs use the cumulative
# normalized_usd snapshot embedded directly in each evaluation event.
INPUT_PER_MTOK = 5.0
CACHED_INPUT_PER_MTOK = 0.5
OUTPUT_PER_MTOK = 30.0

EVALUATION_SCORE_RE = re.compile(r"(?m)^score:\s*([0-9.eE+-]+)\s*$")
EVALUATION_SUBMISSIONS_RE = re.compile(
    r"(?m)^submissions remaining:\s*(\d+)\s*$"
)
KNOWLEDGE_BASE_COMMAND_RE = re.compile(
    r"(?:^|(?:&&|\|\||;|\n|\()\s*)"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*"
    r"(?:[^\s;&|()]*/)?knowledge-base\s+"
    r"(?:status|list|search|read|neighbors|inspire)\b"
)


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield JSONL objects leniently; missing files and bad lines yield nothing."""
    if not path.is_file():
        return
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                yield value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return list(iter_jsonl(path))


def read_json(path: Path) -> Any:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fmt_clock(dt: datetime | None) -> str:
    return dt.strftime("%H:%M:%S") if dt else "--:--:--"


def fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%SZ") if dt else "n/a"


def fmt_int(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return "-"
    if isinstance(value, (int, float)):
        return f"{int(value):,}"
    return str(value)


def fmt_usd(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"${value:,.4f}"
    return "-"


def fmt_ms(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value >= 1000:
            return f"{value / 1000:.1f}s"
        return f"{int(value)}ms"
    return "-"


def fmt_score(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return "-"
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{value:,.3f}"
    return str(value)


def fmt_ratio(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


def ratio_class(value: float | None) -> str:
    if value is None:
        return "ratio-none"
    if value < 0.5:
        return "ratio-red"
    if value <= 0.8:
        return "ratio-amber"
    return "ratio-green"


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:14]


def short_json(value: Any, limit: int = 4000) -> str:
    try:
        text = json.dumps(value, indent=2, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = str(value)
    if len(text) > limit:
        text = text[:limit] + f"\n… [{len(text) - limit} more chars]"
    return text


def cybersecurity_stop_reason(value: Any, failure_context: bool = False) -> str | None:
    """Return a policy-stop reason from structured error data only.

    This deliberately ignores ordinary prompt and response text. ECDSA task
    descriptions can mention cybersecurity, so scanning arbitrary transcript
    content would incorrectly label otherwise successful runs.
    """
    if isinstance(value, list):
        for item in value:
            reason = cybersecurity_stop_reason(item, failure_context)
            if reason:
                return reason
        return None
    if not isinstance(value, dict):
        if failure_context and isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in CYBERSECURITY_MESSAGE_MARKERS):
                return value
        return None

    code = value.get("codex_error_info")
    if code is None:
        code = value.get("code")
    if isinstance(code, str) and code.lower() == "cyber_policy":
        message = value.get("message")
        return (
            message.strip()
            if isinstance(message, str) and message.strip()
            else CYBERSECURITY_DEFAULT_REASON
        )

    node_type = str(value.get("type") or "").lower()
    node_status = str(value.get("status") or "").lower()
    is_failure = failure_context or node_type in {
        "error",
        "response.failed",
        "turn.failed",
    } or node_status in {"error", "failed"}

    message = value.get("message")
    if is_failure and isinstance(message, str):
        lowered = message.lower()
        if any(marker in lowered for marker in CYBERSECURITY_MESSAGE_MARKERS):
            return message

    for key, child in value.items():
        if not isinstance(child, (dict, list, str)):
            continue
        child_is_failure = is_failure or key == "error"
        reason = cybersecurity_stop_reason(child, child_is_failure)
        if reason:
            return reason
    return None


def load_agent_cybersecurity_stop_reason(run_dir: Path) -> str | None:
    """Fallback for runs whose gateway timeline omitted the terminal failure."""
    agent_pattern = str(run_dir / "harbor" / "*" / "task__*" / "agent")
    for agent_dir_text in sorted(glob.glob(agent_pattern)):
        agent_dir = Path(agent_dir_text)
        codex_log = agent_dir / "codex.txt"
        if codex_log.is_file():
            with codex_log.open("r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(entry, dict):
                        continue
                    if str(entry.get("type") or "").lower() not in {
                        "error",
                        "turn.failed",
                    }:
                        continue
                    reason = cybersecurity_stop_reason(entry, True)
                    if reason:
                        return reason

        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.is_dir():
            continue
        for session_path in sorted(sessions_dir.glob("**/*.jsonl")):
            with session_path.open("r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(entry, dict):
                        continue
                    payload = entry.get("payload")
                    if not isinstance(payload, dict):
                        continue
                    if payload.get("type") != "task_complete":
                        continue
                    reason = cybersecurity_stop_reason(payload.get("error"), True)
                    if reason:
                        return reason
    return None


# ---------------------------------------------------------------------------
# Message normalisation (Chat Completions and Responses API shapes)
# ---------------------------------------------------------------------------


@dataclass
class ToolCall:
    call_id: str
    name: str
    arguments: str
    command: str | None = None
    extras: str | None = None


@dataclass
class Message:
    role: str
    text: str
    item_type: str = "message"
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    reasoning: str | None = None
    name: str | None = None
    tool_names: list[str] = field(default_factory=list)
    key: str = ""

    @property
    def is_research_state(self) -> bool:
        return RESEARCH_STATE_MARKER in (self.text or "")

    def research_state_stale(self) -> bool | None:
        if not self.is_research_state:
            return None
        return research_state_stale_flag(self.text)


def research_state_stale_flag(text: str) -> bool | None:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if match:
        try:
            payload = json.loads(match.group(1))
            stale = (
                payload.get("evaluation", {}).get("staleness", {}).get("stale")
                if isinstance(payload, dict)
                else None
            )
            if isinstance(stale, bool):
                return stale
        except (json.JSONDecodeError, AttributeError):
            pass
    if re.search(r'"stale"\s*:\s*true', text):
        return True
    if re.search(r'"stale"\s*:\s*false', text):
        return False
    return None


def content_to_text(content: Any) -> str:
    """Flatten string / part-list content into plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        pieces: list[str] = []
        for part in content:
            if isinstance(part, str):
                pieces.append(part)
            elif isinstance(part, dict):
                if isinstance(part.get("text"), str):
                    pieces.append(part["text"])
                elif part.get("type") in ("input_image", "image_url", "image"):
                    pieces.append("[image]")
                elif isinstance(part.get("refusal"), str):
                    pieces.append(part["refusal"])
                else:
                    pieces.append(short_json(part, 500))
        return "\n".join(pieces)
    if isinstance(content, dict):
        if isinstance(content.get("text"), str):
            return content["text"]
        return short_json(content, 2000)
    return str(content)


def extract_command(name: str, arguments: Any) -> tuple[str | None, str | None]:
    """Return (command, extras) for a tool call, if a shell-like command exists."""
    parsed: Any = arguments
    if isinstance(arguments, str):
        stripped = arguments.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = None
        else:
            parsed = None
        if parsed is None:
            # Codex "exec" custom tool: JavaScript orchestrating tools.exec_command({...})
            match = re.search(r"tools\.(\w+)\((\{.*?\})\)\s*;?", arguments, re.S)
            if match:
                try:
                    inner = json.loads(match.group(2))
                except json.JSONDecodeError:
                    inner = None
                if isinstance(inner, dict):
                    cmd, extras = _command_from_dict(inner)
                    if cmd is not None:
                        return f"{match.group(1)}: {cmd}", extras
            first_line = arguments.strip().splitlines()[0] if arguments.strip() else ""
            return (first_line[:300] or None), None
    if isinstance(parsed, dict):
        return _command_from_dict(parsed)
    return None, None


def _command_from_dict(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    cmd = payload.get("cmd") or payload.get("command")
    if isinstance(cmd, list):
        cmd = " ".join(str(part) for part in cmd)
    if not isinstance(cmd, str):
        return None, None
    extras = {k: v for k, v in payload.items() if k not in ("cmd", "command")}
    extra_text = None
    if extras:
        extra_text = ", ".join(f"{k}={json.dumps(v, default=str)}" for k, v in extras.items())
        if len(extra_text) > 160:
            extra_text = extra_text[:160] + "…"
    return cmd, extra_text


def make_tool_call(call_id: Any, name: Any, arguments: Any) -> ToolCall:
    if not isinstance(arguments, str):
        arguments = json.dumps(arguments, ensure_ascii=False, default=str)
    name_text = str(name or "tool")
    command, extras = extract_command(name_text, arguments)
    return ToolCall(str(call_id or ""), name_text, arguments, command, extras)


def collect_tool_names(tools: Any, prefix: str = "") -> list[str]:
    names: list[str] = []
    if not isinstance(tools, list):
        return names
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        nested = tool.get("tools")
        if isinstance(nested, list):
            namespace = tool.get("name") or tool.get("type") or ""
            sub_prefix = f"{prefix}{namespace}." if namespace and namespace != "functions" else prefix
            names.extend(collect_tool_names(nested, sub_prefix))
            continue
        function = tool.get("function") if isinstance(tool.get("function"), dict) else {}
        name = tool.get("name") or function.get("name") or tool.get("type") or "?"
        names.append(f"{prefix}{name}")
    return names


def finalize(message: Message, raw: Any) -> Message:
    message.key = stable_hash(raw)
    return message


def normalize_chat_messages(request: dict[str, Any]) -> list[Message]:
    messages: list[Message] = []
    for raw in request.get("messages") or []:
        if not isinstance(raw, dict):
            messages.append(finalize(Message("other", short_json(raw), "unknown"), raw))
            continue
        role = str(raw.get("role") or "other")
        text = content_to_text(raw.get("content"))
        tool_calls = []
        for call in raw.get("tool_calls") or []:
            if not isinstance(call, dict):
                continue
            function = call.get("function") if isinstance(call.get("function"), dict) else {}
            tool_calls.append(
                make_tool_call(call.get("id"), function.get("name") or call.get("name"), function.get("arguments", ""))
            )
        if role == "function":
            role = "tool"
        reasoning = raw.get("reasoning_content") if isinstance(raw.get("reasoning_content"), str) else None
        messages.append(
            finalize(
                Message(
                    role,
                    text,
                    "message",
                    tool_calls,
                    raw.get("tool_call_id"),
                    reasoning,
                    raw.get("name"),
                ),
                raw,
            )
        )
    return messages


def normalize_responses_input(request: dict[str, Any]) -> list[Message]:
    messages: list[Message] = []
    instructions = request.get("instructions")
    if isinstance(instructions, str) and instructions:
        messages.append(finalize(Message("system", instructions, "instructions"), {"instructions": instructions}))
    items = request.get("input")
    if isinstance(items, str):
        items = [{"role": "user", "content": items, "type": "message"}]
    for raw in items or []:
        if not isinstance(raw, dict):
            messages.append(finalize(Message("other", short_json(raw), "unknown"), raw))
            continue
        item_type = str(raw.get("type") or ("message" if "role" in raw else "unknown"))
        role = str(raw.get("role") or "")
        if item_type == "message":
            messages.append(finalize(Message(role or "user", content_to_text(raw.get("content")), "message"), raw))
        elif item_type == "reasoning":
            summary = raw.get("summary") or []
            text = "\n".join(
                part.get("text", "") for part in summary if isinstance(part, dict)
            ) or ("[encrypted reasoning]" if raw.get("encrypted_content") else "")
            messages.append(finalize(Message("assistant", "", "reasoning", reasoning=text), raw))
        elif item_type in ("function_call", "custom_tool_call", "local_shell_call", "shell_call"):
            arguments = raw.get("arguments")
            if arguments is None:
                arguments = raw.get("input")
            if arguments is None and isinstance(raw.get("action"), dict):
                arguments = raw["action"]
            call = make_tool_call(raw.get("call_id") or raw.get("id"), raw.get("name") or item_type, arguments or "")
            messages.append(finalize(Message("assistant", "", "tool_call", [call]), raw))
        elif item_type in (
            "function_call_output",
            "custom_tool_call_output",
            "local_shell_call_output",
            "shell_call_output",
        ):
            output = raw.get("output")
            messages.append(
                finalize(Message("tool", content_to_text(output), "tool_result", tool_call_id=raw.get("call_id")), raw)
            )
        elif item_type == "additional_tools" or isinstance(raw.get("tools"), list):
            names = collect_tool_names(raw.get("tools"))
            text = f"{len(names)} tool definition(s): " + ", ".join(names)
            messages.append(finalize(Message(role or "developer", text, "tools", tool_names=names), raw))
        else:
            messages.append(finalize(Message(role or "other", short_json(raw), item_type), raw))
    return messages


def normalize_request(request: dict[str, Any], operation: str) -> tuple[list[Message], list[str]]:
    if not isinstance(request, dict):
        return [], []
    if "messages" in request and "input" not in request:
        messages = normalize_chat_messages(request)
    elif "input" in request or "instructions" in request:
        messages = normalize_responses_input(request)
    elif operation == "responses":
        messages = normalize_responses_input(request)
    else:
        messages = normalize_chat_messages(request)
    tool_names = collect_tool_names(request.get("tools"))
    for message in messages:
        if message.item_type == "tools":
            tool_names.extend(message.tool_names)
    return messages, tool_names


# ---------------------------------------------------------------------------
# Response reconstruction
# ---------------------------------------------------------------------------


@dataclass
class ResponseBlock:
    kind: str
    text: str = ""
    tool_call: ToolCall | None = None
    raw_type: str | None = None


@dataclass
class Response:
    available: bool = False
    text: str = ""
    reasoning: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    blocks: list[ResponseBlock] = field(default_factory=list)
    finish_reason: str | None = None
    status: str | None = None
    source: str = ""


ANTHROPIC_STREAM_EVENT_TYPES = {
    "message_start",
    "content_block_start",
    "content_block_delta",
    "content_block_stop",
    "message_delta",
    "message_stop",
    "ping",
}


def parse_response(payload: Any) -> Response:
    if payload is None:
        return Response(available=False)
    if isinstance(payload, dict):
        if "choices" in payload:
            return _parse_chat_dict(payload)
        if payload.get("type") == "message" and isinstance(payload.get("content"), list):
            return _parse_anthropic_message(payload)
        if "output" in payload or payload.get("object") == "response":
            return _parse_responses_dict(payload)
        if isinstance(payload.get("response"), dict):
            return _parse_responses_dict(payload["response"])
        return Response(available=True, text=short_json(payload), source="unknown-dict")
    if isinstance(payload, list):
        dicts = [item for item in payload if isinstance(item, dict)]
        if any("choices" in item for item in dicts):
            return _parse_chat_chunks(dicts)
        if any(item.get("type") in ANTHROPIC_STREAM_EVENT_TYPES for item in dicts):
            return _parse_anthropic_events(dicts)
        if any(str(item.get("type", "")).startswith("response.") for item in dicts):
            return _parse_responses_events(dicts)
        if dicts and all("output" in item for item in dicts):
            return _parse_responses_dict(dicts[-1])
        return Response(available=bool(dicts), text=short_json(payload), source="unknown-list")
    return Response(available=True, text=str(payload), source="unknown")


def _append_response_block(response: Response, block: ResponseBlock) -> None:
    response.blocks.append(block)
    if block.kind == "thinking" and block.text:
        response.reasoning = (
            response.reasoning + "\n" + block.text
        ).strip() if response.reasoning else block.text
    elif block.kind == "text" and block.text:
        response.text = (
            response.text + "\n" + block.text
        ).strip() if response.text else block.text
    elif block.kind == "tool_use" and block.tool_call is not None:
        response.tool_calls.append(block.tool_call)


def _anthropic_content_block(raw: dict[str, Any]) -> ResponseBlock:
    block_type = str(raw.get("type") or "unknown")
    if block_type == "thinking":
        return ResponseBlock(
            "thinking",
            str(raw.get("thinking") or ""),
            raw_type=block_type,
        )
    if block_type == "redacted_thinking":
        return ResponseBlock(
            "thinking",
            "[redacted thinking]",
            raw_type=block_type,
        )
    if block_type == "text":
        return ResponseBlock(
            "text",
            str(raw.get("text") or ""),
            raw_type=block_type,
        )
    if block_type in {"tool_use", "server_tool_use", "mcp_tool_use"}:
        call = make_tool_call(
            raw.get("id"),
            raw.get("name") or block_type,
            raw.get("input") if raw.get("input") is not None else {},
        )
        return ResponseBlock(
            "tool_use",
            tool_call=call,
            raw_type=block_type,
        )
    if block_type.endswith("_tool_result") or block_type == "tool_result":
        return ResponseBlock(
            "tool_result",
            content_to_text(raw.get("content")),
            raw_type=block_type,
        )
    return ResponseBlock(
        "unknown",
        short_json(raw),
        raw_type=block_type,
    )


def _parse_anthropic_message(payload: dict[str, Any]) -> Response:
    response = Response(available=True, source="anthropic-message")
    for raw in payload.get("content") or []:
        if isinstance(raw, dict):
            _append_response_block(response, _anthropic_content_block(raw))
        else:
            _append_response_block(
                response,
                ResponseBlock("unknown", short_json(raw), raw_type="unknown"),
            )
    stop_reason = payload.get("stop_reason")
    if stop_reason:
        response.finish_reason = str(stop_reason)
    return response


def _parse_anthropic_events(events: list[dict[str, Any]]) -> Response:
    response = Response(available=True, source="anthropic-messages-stream")
    builders: dict[int, dict[str, Any]] = {}
    order: list[int] = []
    start_message: dict[str, Any] | None = None

    def ensure_builder(index: int, block_type: str = "unknown") -> dict[str, Any]:
        builder = builders.get(index)
        if builder is None:
            builder = {
                "type": block_type,
                "raw": {"type": block_type},
                "thinking": [],
                "text": [],
                "input_parts": [],
                "unknown_deltas": [],
            }
            builders[index] = builder
            order.append(index)
        elif builder["type"] == "unknown" and block_type != "unknown":
            builder["type"] = block_type
        return builder

    for event in events:
        event_type = str(event.get("type") or "")
        if event_type == "message_start":
            message = event.get("message")
            if isinstance(message, dict):
                start_message = message
                if message.get("stop_reason"):
                    response.finish_reason = str(message["stop_reason"])
        elif event_type == "content_block_start":
            index = event.get("index")
            if not isinstance(index, int):
                index = len(order)
            raw = (
                event.get("content_block")
                if isinstance(event.get("content_block"), dict)
                else {}
            )
            block_type = str(raw.get("type") or "unknown")
            builder = ensure_builder(index, block_type)
            builder["raw"] = dict(raw)
            if isinstance(raw.get("thinking"), str) and raw["thinking"]:
                builder["thinking"].append(raw["thinking"])
            if isinstance(raw.get("text"), str) and raw["text"]:
                builder["text"].append(raw["text"])
        elif event_type == "content_block_delta":
            index = event.get("index")
            if not isinstance(index, int):
                index = len(order)
            delta = event.get("delta") if isinstance(event.get("delta"), dict) else {}
            delta_type = str(delta.get("type") or "")
            inferred_type = {
                "thinking_delta": "thinking",
                "text_delta": "text",
                "input_json_delta": "tool_use",
            }.get(delta_type, "unknown")
            builder = ensure_builder(index, inferred_type)
            if delta_type == "thinking_delta" and isinstance(delta.get("thinking"), str):
                builder["thinking"].append(delta["thinking"])
            elif delta_type == "text_delta" and isinstance(delta.get("text"), str):
                builder["text"].append(delta["text"])
            elif delta_type == "input_json_delta" and isinstance(delta.get("partial_json"), str):
                builder["input_parts"].append(delta["partial_json"])
            elif delta_type != "signature_delta":
                builder["unknown_deltas"].append(delta)
        elif event_type == "message_delta":
            delta = event.get("delta") if isinstance(event.get("delta"), dict) else {}
            if delta.get("stop_reason"):
                response.finish_reason = str(delta["stop_reason"])

    if not order and start_message is not None:
        return _parse_anthropic_message(start_message)

    for index in order:
        builder = builders[index]
        block_type = str(builder["type"])
        raw = dict(builder["raw"])
        if block_type in {"thinking", "redacted_thinking"}:
            raw["type"] = block_type
            if block_type == "thinking":
                raw["thinking"] = "".join(builder["thinking"])
        elif block_type == "text":
            raw["type"] = block_type
            raw["text"] = "".join(builder["text"])
        elif block_type in {"tool_use", "server_tool_use", "mcp_tool_use"}:
            raw["type"] = block_type
            partial_json = "".join(builder["input_parts"])
            if partial_json:
                try:
                    raw["input"] = json.loads(partial_json)
                except json.JSONDecodeError:
                    raw["input"] = partial_json
            elif raw.get("input") is None:
                raw["input"] = {}
        elif builder["unknown_deltas"]:
            raw["deltas"] = builder["unknown_deltas"]
        _append_response_block(response, _anthropic_content_block(raw))

    if not response.blocks:
        response.text = short_json(events)
    return response


def _parse_chat_dict(payload: dict[str, Any]) -> Response:
    response = Response(available=True, source="chat")
    choices = payload.get("choices") or []
    if choices and isinstance(choices[0], dict):
        choice = choices[0]
        message = choice.get("message") or choice.get("delta") or {}
        response.text = content_to_text(message.get("content"))
        if isinstance(message.get("reasoning_content"), str):
            response.reasoning = message["reasoning_content"]
        for call in message.get("tool_calls") or []:
            if isinstance(call, dict):
                function = call.get("function") or {}
                response.tool_calls.append(
                    make_tool_call(call.get("id"), function.get("name"), function.get("arguments", ""))
                )
        response.finish_reason = choice.get("finish_reason")
    return response


def _parse_chat_chunks(chunks: list[dict[str, Any]]) -> Response:
    response = Response(available=True, source="chat-stream")
    text_parts: list[str] = []
    reasoning_parts: list[str] = []
    calls: dict[int, dict[str, Any]] = {}
    for chunk in chunks:
        for choice in chunk.get("choices") or []:
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta") or choice.get("message") or {}
            content = delta.get("content")
            if isinstance(content, str):
                text_parts.append(content)
            elif content:
                text_parts.append(content_to_text(content))
            reasoning = delta.get("reasoning_content") or delta.get("reasoning")
            if isinstance(reasoning, str):
                reasoning_parts.append(reasoning)
            for call in delta.get("tool_calls") or []:
                if not isinstance(call, dict):
                    continue
                index = call.get("index")
                if not isinstance(index, int):
                    index = len(calls)
                entry = calls.setdefault(index, {"id": "", "name": "", "arguments": ""})
                if call.get("id"):
                    entry["id"] = call["id"]
                function = call.get("function") or {}
                if function.get("name") and not entry["name"]:
                    entry["name"] = function["name"]
                if isinstance(function.get("arguments"), str):
                    entry["arguments"] += function["arguments"]
            if choice.get("finish_reason"):
                response.finish_reason = choice["finish_reason"]
    response.text = "".join(text_parts)
    response.reasoning = "".join(reasoning_parts)
    for index in sorted(calls):
        entry = calls[index]
        response.tool_calls.append(make_tool_call(entry["id"], entry["name"], entry["arguments"]))
    return response


def _parse_output_items(items: list[Any], response: Response) -> None:
    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "message":
            text = content_to_text(item.get("content"))
            if text:
                response.text = (response.text + "\n" + text).strip() if response.text else text
        elif item_type == "reasoning":
            summary = "\n".join(
                part.get("text", "") for part in item.get("summary") or [] if isinstance(part, dict)
            )
            if summary:
                response.reasoning = (response.reasoning + "\n" + summary).strip() if response.reasoning else summary
        elif item_type in ("function_call", "custom_tool_call", "local_shell_call", "shell_call"):
            arguments = item.get("arguments")
            if arguments is None:
                arguments = item.get("input")
            if arguments is None and isinstance(item.get("action"), dict):
                arguments = item["action"]
            response.tool_calls.append(
                make_tool_call(item.get("call_id") or item.get("id"), item.get("name") or item_type, arguments or "")
            )
        elif item_type in ("web_search_call", "file_search_call", "computer_call", "code_interpreter_call"):
            response.tool_calls.append(make_tool_call(item.get("id"), item_type, item.get("action") or {}))


def _parse_responses_dict(payload: dict[str, Any]) -> Response:
    response = Response(available=True, source="responses")
    _parse_output_items(payload.get("output") or [], response)
    response.status = payload.get("status")
    incomplete = payload.get("incomplete_details")
    if isinstance(incomplete, dict) and incomplete.get("reason"):
        response.finish_reason = f"incomplete: {incomplete['reason']}"
    elif response.status:
        response.finish_reason = response.status
    return response


def _parse_responses_events(events: list[dict[str, Any]]) -> Response:
    response = Response(available=True, source="responses-stream")
    completed: dict[str, Any] | None = None
    done_items: list[Any] = []
    text_deltas: list[str] = []
    reasoning_deltas: list[str] = []
    for event in events:
        event_type = str(event.get("type", ""))
        if event_type in ("response.completed", "response.incomplete", "response.failed"):
            if isinstance(event.get("response"), dict):
                completed = event["response"]
        elif event_type == "response.output_item.done":
            done_items.append(event.get("item"))
        elif event_type == "response.output_text.delta" and isinstance(event.get("delta"), str):
            text_deltas.append(event["delta"])
        elif event_type == "response.reasoning_summary_text.delta" and isinstance(event.get("delta"), str):
            reasoning_deltas.append(event["delta"])
    if completed and completed.get("output"):
        _parse_output_items(completed["output"], response)
    elif done_items:
        _parse_output_items(done_items, response)
    if not response.text and text_deltas:
        response.text = "".join(text_deltas)
    if not response.reasoning and reasoning_deltas:
        response.reasoning = "".join(reasoning_deltas)
    if completed:
        response.status = completed.get("status")
        incomplete = completed.get("incomplete_details")
        if isinstance(incomplete, dict) and incomplete.get("reason"):
            response.finish_reason = f"incomplete: {incomplete['reason']}"
        elif response.status:
            response.finish_reason = response.status
        error = completed.get("error")
        if isinstance(error, dict) and error.get("message"):
            response.finish_reason = f"error: {error['message']}"
    return response


def response_from_trajectory(step: dict[str, Any]) -> Response:
    response = Response(available=True, source="trajectory")
    response.text = str(step.get("message") or "")
    response.reasoning = str(step.get("reasoning_content") or "")
    for call in step.get("tool_calls") or []:
        if isinstance(call, dict):
            response.tool_calls.append(
                make_tool_call(
                    call.get("tool_call_id") or call.get("id"),
                    call.get("function_name") or call.get("name"),
                    call.get("arguments") or {},
                )
            )
    return response


# ---------------------------------------------------------------------------
# Run loading
# ---------------------------------------------------------------------------


@dataclass
class RequestView:
    index: int
    request_id: str
    timestamp: datetime | None
    provider: str
    model: str
    operation: str
    messages: list[Message]
    tool_names: list[str]
    prompt_profile: dict[str, Any] | None
    accounting: dict[str, Any] = field(default_factory=dict)
    harness: dict[str, Any] | None = None
    response: Response = field(default_factory=Response)
    response_timestamp: datetime | None = None
    response_status: str | None = None
    reasoning_stream: str = ""

    def cache_ratio(self) -> float | None:
        cached = self.accounting.get("cached_input_tokens")
        total = self.accounting.get("input_tokens")
        if isinstance(cached, (int, float)) and isinstance(total, (int, float)) and total > 0:
            return max(0.0, min(1.0, float(cached) / float(total)))
        return None


@dataclass
class Marker:
    kind: str
    label: str
    detail: str = ""
    timestamp: datetime | None = None
    request_id: str | None = None
    after_request: bool = False
    css: str = ""
    anchor: str = ""
    slot: int | None = None


@dataclass
class RunData:
    run_dir: Path
    run_id: str
    requests: list[RequestView]
    record: dict[str, Any]
    evals: list[dict[str, Any]]
    research_state: list[dict[str, Any]]
    gateway_events: list[dict[str, Any]]
    delivery_events: list[dict[str, Any]]
    kb_events: list[dict[str, Any]]
    legacy_eval_timestamps: list[datetime] = field(default_factory=list)
    legacy_kb_timestamps: list[datetime] = field(default_factory=list)
    metric_direction: str = "minimize"
    warnings: list[str] = field(default_factory=list)
    cybersecurity_stop_reason: str | None = None
    verifier_score: float | None = None
    verifier_metric: str | None = None
    verifier_finished_at: datetime | None = None


def load_trajectory(run_dir: Path) -> list[dict[str, Any]]:
    pattern = str(run_dir / "harbor" / "*" / "task__*" / "agent" / "trajectory.json")
    for path in sorted(glob.glob(pattern)):
        payload = read_json(Path(path))
        if isinstance(payload, dict) and isinstance(payload.get("steps"), list):
            return [step for step in payload["steps"] if isinstance(step, dict)]
        if isinstance(payload, list):
            return [step for step in payload if isinstance(step, dict)]
    return []


def load_legacy_action_timestamps(
    run_dir: Path,
) -> tuple[list[datetime], list[datetime]]:
    """Recover evaluator and KB command times from pre-canonical Codex logs."""
    evaluation_timestamps: list[datetime] = []
    knowledge_base_timestamps: list[datetime] = []
    rollout_paths = sorted(
        run_dir.glob("harbor/**/agent/sessions/**/rollout-*.jsonl")
    )
    for rollout_path in rollout_paths:
        for record in iter_jsonl(rollout_path):
            if record.get("type") != "event_msg":
                continue
            payload = record.get("payload")
            item = payload.get("item") if isinstance(payload, dict) else None
            if not isinstance(item, dict) or item.get("type") != "CommandExecution":
                continue
            timestamp = parse_ts(record.get("timestamp"))
            if timestamp is None:
                continue

            output = item.get("stdout")
            if not isinstance(output, str):
                output = item.get("formatted_output")
            if not isinstance(output, str):
                output = item.get("aggregated_output")
            if (
                isinstance(output, str)
                and EVALUATION_SUBMISSIONS_RE.search(output)
                and EVALUATION_SCORE_RE.search(output)
            ):
                evaluation_timestamps.append(timestamp)

            command = item.get("command")
            if isinstance(command, list):
                command_parts = [
                    str(part) for part in command if part is not None
                ]
                command_text = command_parts[-1] if command_parts else ""
            else:
                command_text = str(command or "")
            if KNOWLEDGE_BASE_COMMAND_RE.search(command_text):
                knowledge_base_timestamps.append(timestamp)

    evaluation_timestamps.sort()
    knowledge_base_timestamps.sort()
    return evaluation_timestamps, knowledge_base_timestamps


def score_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def verifier_score_from_stats(
    stats: Any,
    metric_name: str | None,
) -> tuple[float | None, str | None]:
    """Extract Harbor's aggregate final-verifier score from job statistics."""
    if not isinstance(stats, dict) or not isinstance(stats.get("evals"), dict):
        return None, None
    for evaluation in stats["evals"].values():
        if not isinstance(evaluation, dict):
            continue
        reward_stats = evaluation.get("reward_stats")
        if not isinstance(reward_stats, dict) or not reward_stats:
            continue
        selected_metric = (
            metric_name
            if metric_name in reward_stats
            else next(iter(reward_stats))
            if metric_name is None and len(reward_stats) == 1
            else None
        )
        if selected_metric is None:
            continue

        # Harbor's aggregate metric is authoritative when present. A Dungeness
        # run currently has one trial, but using the aggregate also behaves
        # correctly if a job ever contains multiple trials.
        metrics = evaluation.get("metrics")
        if isinstance(metrics, list):
            for metric in metrics:
                if not isinstance(metric, dict):
                    continue
                score = score_number(metric.get("mean"))
                if score is not None:
                    return score, selected_metric

        values = reward_stats.get(selected_metric)
        if isinstance(values, dict) and len(values) == 1:
            score = score_number(next(iter(values)))
            if score is not None:
                return score, selected_metric
    return None, None


def verifier_score_from_trial(
    payload: Any,
    metric_name: str | None,
) -> tuple[float | None, str | None]:
    if not isinstance(payload, dict):
        return None, None
    verifier = payload.get("verifier_result")
    rewards = verifier.get("rewards") if isinstance(verifier, dict) else None
    if not isinstance(rewards, dict) or not rewards:
        return None, None
    selected_metric = (
        metric_name
        if metric_name in rewards
        else next(iter(rewards))
        if metric_name is None and len(rewards) == 1
        else None
    )
    if selected_metric is None:
        return None, None
    return score_number(rewards.get(selected_metric)), selected_metric


def load_verifier_result(
    run_dir: Path,
    record: dict[str, Any],
    metric_name: str | None,
) -> tuple[float | None, str | None, datetime | None]:
    """Load the authoritative final verifier result, including older runs."""
    data = record.get("data") if isinstance(record.get("data"), dict) else {}
    record_finished_at = (
        parse_ts(data.get("finished_at"))
        if isinstance(data, dict)
        else None
    )
    trial_results = sorted(
        (run_dir / "harbor").glob("*/task__*/result.json")
    )

    # Prefer the live Harbor job result. It can appear before record.json is
    # finalized, allowing the watcher to update as soon as verification ends.
    for path in sorted((run_dir / "harbor").glob("*/result.json")):
        payload = read_json(path)
        if not isinstance(payload, dict):
            continue
        score, selected_metric = verifier_score_from_stats(
            payload.get("stats"),
            metric_name,
        )
        if score is not None:
            trial_finished_at = None
            for trial_path in trial_results:
                trial_payload = read_json(trial_path)
                trial_score, trial_metric = verifier_score_from_trial(
                    trial_payload,
                    selected_metric,
                )
                if trial_score == score and trial_metric == selected_metric:
                    if isinstance(trial_payload, dict):
                        trial_finished_at = parse_ts(
                            trial_payload.get("finished_at")
                        )
                    break
            return (
                score,
                selected_metric,
                record_finished_at
                or trial_finished_at
                or parse_ts(payload.get("finished_at")),
            )

    # Completed run records retain the same Harbor statistics, so archived runs
    # remain renderable even when their Harbor directory was pruned.
    execution = data.get("execution") if isinstance(data, dict) else None
    if isinstance(execution, dict):
        score, selected_metric = verifier_score_from_stats(
            execution.get("stats"),
            metric_name,
        )
        if score is not None:
            return (
                score,
                selected_metric,
                record_finished_at or parse_ts(execution.get("finished_at")),
            )

    # Fall back to the per-trial result for partially retained Harbor output.
    for path in trial_results:
        payload = read_json(path)
        score, selected_metric = verifier_score_from_trial(payload, metric_name)
        if score is not None:
            finished_at = (
                parse_ts(payload.get("finished_at"))
                if isinstance(payload, dict)
                else None
            )
            return score, selected_metric, record_finished_at or finished_at
    return None, None, None


def canonical_event_views(
    events: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Project schema-v1 canonical events into the viewer's legacy-shaped views."""

    views = {
        "timeline": [],
        "model": [],
        "evals": [],
        "research_state": [],
        "gateway": [],
        "delivery": [],
        "kb": [],
    }

    def flattened(event: dict[str, Any]) -> dict[str, Any]:
        data = event.get("data")
        result = dict(data) if isinstance(data, dict) else {}
        result.update(
            {
                key: event[key]
                for key in (
                    "run_id",
                    "sequence",
                    "event_id",
                    "request_id",
                )
                if event.get(key) is not None
            }
        )
        result["observed_at"] = event.get("observed_at")
        result["timestamp"] = event.get("observed_at")
        if isinstance(event.get("usage"), dict):
            result["cumulative_usage"] = dict(event["usage"])
        return result

    for event in events:
        source = event.get("source")
        kind = event.get("kind")
        if not isinstance(kind, str):
            continue
        view = flattened(event)
        if source == "gateway" and (
            kind.startswith("model.") or kind == "harness.applied"
        ):
            if kind == "model.accounting":
                views["model"].append(view)
            else:
                view["kind"] = kind
                views["timeline"].append(view)
        if source == "evaluator" and kind == "evaluation.completed":
            views["evals"].append(view)
        if source == "research-state" and kind.startswith("research_state."):
            view["kind"] = kind.removeprefix("research_state.")
            views["research_state"].append(view)
        if source == "gateway" and kind.startswith("gateway."):
            view["event"] = kind.removeprefix("gateway.")
            views["gateway"].append(view)
        if source == "gateway" and kind == "research_state.delivery":
            views["delivery"].append(view)
        if source == "knowledge-base" and kind == "knowledge_base.request":
            view["event"] = "knowledge_base_request"
            views["kb"].append(view)
        if source == "knowledge-base" and kind == "knowledge_base.inspiration":
            view.setdefault("action", "inspire")
            view.setdefault("event", "kb_lookup_completed")
            views["kb"].append(view)
    return views


def load_run(run_dir: Path) -> RunData:
    usage = run_dir / "usage"
    record_raw = read_json(run_dir / "record.json")
    record = record_raw if isinstance(record_raw, dict) else {}
    run_id = str(record.get("id") or record.get("data", {}).get("run_id") or run_dir.name)
    warnings: list[str] = []

    canonical_path = usage / "events.jsonl"
    timeline_path = usage / "gateway-timeline.jsonl"
    if canonical_path.is_file():
        canonical = canonical_event_views(iter_jsonl(canonical_path))
        timeline = canonical["timeline"] or read_jsonl(timeline_path)
        model_event_rows = canonical["model"] or read_jsonl(
            usage / "model-events.jsonl"
        )
    else:
        if not timeline_path.is_file():
            warnings.append(
                f"missing {canonical_path} and legacy {timeline_path}"
            )
        canonical = None
        timeline = read_jsonl(timeline_path)
        model_event_rows = read_jsonl(usage / "model-events.jsonl")

    model_events = {
        e.get("request_id"): e
        for e in model_event_rows
        if e.get("request_id")
    }

    requests: list[RequestView] = []
    by_id: dict[str, RequestView] = {}
    reasoning_parts: dict[str, list[tuple[int, str]]] = {}
    pending_harness: dict[str, dict[str, Any]] = {}
    pending_responses: dict[str, dict[str, Any]] = {}
    security_reason: str | None = None

    for entry in timeline:
        kind = entry.get("kind")
        request_id = str(entry.get("request_id") or "")
        if kind == "model.request":
            request = entry.get("request") if isinstance(entry.get("request"), dict) else {}
            operation = str(entry.get("operation") or ("responses" if "input" in request else "chat/completions"))
            messages, tool_names = normalize_request(request, operation)
            view = RequestView(
                index=len(requests) + 1,
                request_id=request_id,
                timestamp=parse_ts(entry.get("timestamp")),
                provider=str(entry.get("provider") or "?"),
                model=str(entry.get("model") or request.get("model") or "?"),
                operation=operation,
                messages=messages,
                tool_names=tool_names,
                prompt_profile=entry.get("prompt_profile") if isinstance(entry.get("prompt_profile"), dict) else None,
            )
            requests.append(view)
            if request_id:
                by_id[request_id] = view
                if request_id in pending_harness:
                    view.harness = pending_harness.pop(request_id)
                if request_id in pending_responses:
                    _attach_response(view, pending_responses.pop(request_id))
        elif kind == "model.response":
            if security_reason is None:
                security_reason = cybersecurity_stop_reason(
                    {
                        "status": entry.get("status"),
                        "response": entry.get("response"),
                        "error": entry.get("error"),
                    }
                )
            view = by_id.get(request_id)
            if view is not None:
                _attach_response(view, entry)
            elif request_id:
                pending_responses[request_id] = entry
        elif kind == "model.reasoning":
            text = entry.get("text")
            if isinstance(text, str) and request_id:
                order = entry.get("sequence") if isinstance(entry.get("sequence"), int) else len(reasoning_parts.get(request_id, []))
                reasoning_parts.setdefault(request_id, []).append((order, text))
        elif kind == "harness.applied":
            view = by_id.get(request_id)
            if view is not None:
                view.harness = entry
            elif request_id:
                pending_harness[request_id] = entry
        # unknown kinds are ignored

    for request_id, parts in reasoning_parts.items():
        view = by_id.get(request_id)
        if view is not None:
            parts.sort(key=lambda item: item[0])
            view.reasoning_stream = "".join(text for _, text in parts)

    for view in requests:
        accounting = dict(model_events.get(view.request_id) or {})
        if not accounting and view.accounting:
            accounting = dict(view.accounting)
        elif view.accounting:
            for key, value in view.accounting.items():
                accounting.setdefault(key, value)
        view.accounting = accounting

    trajectory: list[dict[str, Any]] | None = None
    for position, view in enumerate(requests):
        if view.response.available:
            continue
        if trajectory is None:
            trajectory = load_trajectory(run_dir)
        if not trajectory or view.timestamp is None:
            continue
        next_ts = requests[position + 1].timestamp if position + 1 < len(requests) else None
        for step in trajectory:
            if step.get("source") in ("user", "system"):
                continue
            step_ts = parse_ts(step.get("timestamp"))
            if step_ts is None or step_ts < view.timestamp:
                continue
            if next_ts is not None and step_ts >= next_ts:
                break
            view.response = response_from_trajectory(step)
            break

    data = record.get("data") if isinstance(record.get("data"), dict) else {}
    metric = data.get("metric") if isinstance(data.get("metric"), dict) else {}
    direction = str(metric.get("direction") or "minimize")
    metric_name = (
        str(metric["name"])
        if isinstance(metric.get("name"), str)
        else None
    )
    verifier_score, verifier_metric, verifier_finished_at = load_verifier_result(
        run_dir,
        record,
        metric_name,
    )
    if security_reason is None:
        security_reason = cybersecurity_stop_reason(data.get("error"), True)
    raw_status = str(data.get("status") or "").lower()
    if security_reason is None and (
        (not canonical_path.is_file() and not timeline_path.is_file())
        or raw_status in {"failed", "error", "errored", "stopped", "cancelled", "canceled"}
    ):
        security_reason = load_agent_cybersecurity_stop_reason(run_dir)
    legacy_eval_timestamps: list[datetime] = []
    legacy_kb_timestamps: list[datetime] = []
    if canonical is None:
        (
            legacy_eval_timestamps,
            legacy_kb_timestamps,
        ) = load_legacy_action_timestamps(run_dir)

    return RunData(
        run_dir=run_dir,
        run_id=run_id,
        requests=requests,
        record=record,
        evals=(
            canonical["evals"] or read_jsonl(usage / "eval-events.jsonl")
            if canonical is not None
            else read_jsonl(usage / "eval-events.jsonl")
        ),
        research_state=(
            canonical["research_state"]
            or read_jsonl(usage / "research-state-events.jsonl")
            if canonical is not None
            else read_jsonl(usage / "research-state-events.jsonl")
        ),
        gateway_events=(
            canonical["gateway"] or read_jsonl(usage / "gateway-events.jsonl")
            if canonical is not None
            else read_jsonl(usage / "gateway-events.jsonl")
        ),
        delivery_events=(
            canonical["delivery"]
            or read_jsonl(usage / "research-state-delivery-events.jsonl")
            if canonical is not None
            else read_jsonl(usage / "research-state-delivery-events.jsonl")
        ),
        kb_events=(
            canonical["kb"] or read_jsonl(usage / "knowledge-base-events.jsonl")
            if canonical is not None
            else read_jsonl(usage / "knowledge-base-events.jsonl")
        ),
        legacy_eval_timestamps=legacy_eval_timestamps,
        legacy_kb_timestamps=legacy_kb_timestamps,
        metric_direction=direction,
        warnings=warnings,
        cybersecurity_stop_reason=security_reason,
        verifier_score=verifier_score,
        verifier_metric=verifier_metric,
        verifier_finished_at=verifier_finished_at,
    )


def _attach_response(view: RequestView, entry: dict[str, Any]) -> None:
    view.response = parse_response(entry.get("response"))
    view.response_timestamp = parse_ts(entry.get("timestamp"))
    view.response_status = entry.get("status")
    usage = entry.get("usage")
    if isinstance(usage, dict):
        view.accounting = {
            "input_tokens": usage.get("input_tokens"),
            "cached_input_tokens": usage.get("cached_input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "reasoning_tokens": usage.get("reasoning_tokens"),
            "status": entry.get("status"),
        }
    if view.response.available and not view.response.finish_reason and entry.get("status") not in (None, "success"):
        view.response.finish_reason = str(entry.get("status"))


# ---------------------------------------------------------------------------
# Delta computation
# ---------------------------------------------------------------------------


@dataclass
class DeltaEntry:
    message: Message
    position: int
    status: str  # new | changed | tail-replaced


@dataclass
class Delta:
    unchanged_prefix: int
    entries: list[DeltaEntry]
    prefix_break_at: int | None
    dropped_tail: int


def comparable(previous: RequestView, current: RequestView) -> bool:
    """Requests to different providers/models/operations do not share a prompt cache."""
    return (previous.provider, previous.model, previous.operation) == (current.provider, current.model, current.operation)


def compute_delta(previous: list[Message] | None, current: list[Message]) -> Delta:
    if previous is None:
        return Delta(0, [DeltaEntry(m, i, "new") for i, m in enumerate(current)], None, 0)
    common = 0
    while common < len(previous) and common < len(current) and previous[common].key == current[common].key:
        common += 1
    prefix_break = common if common < len(previous) - 1 else None
    previous_keys = {m.key for m in previous}
    entries: list[DeltaEntry] = []
    for position in range(common, len(current)):
        if current[position].key in previous_keys:
            # Same content already sent in the previous request; only its cache
            # position changed. Rendered as a collapsed stub in the delta view.
            status = "same"
        elif position < len(previous) - 1:
            status = "changed"
        elif position == len(previous) - 1:
            status = "tail-replaced"
        else:
            status = "new"
        entries.append(DeltaEntry(current[position], position, status))
    dropped = max(0, len(previous) - len(current))
    return Delta(common, entries, prefix_break, dropped)


# ---------------------------------------------------------------------------
# Markers (rail)
# ---------------------------------------------------------------------------


def _request_id_from_event_id(event_id: Any) -> str | None:
    if not isinstance(event_id, str):
        return None
    parts = event_id.split(":")
    if len(parts) >= 3 and parts[0] == "model-usage":
        return parts[-1]
    return None


def is_ok_status(status: Any) -> bool:
    return status in ("ok", "valid", "success")


EVALUATE_COMMAND_RE = re.compile(
    r"(?:^|(?:&&|\|\||;|\n|\()\s*)"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*"
    r"(?:(?:command|time)\s+)?"
    r"(?:timeout(?:\s+--?\S+)*\s+\S+\s+)?"
    r"(?:[^\s;&|()]*/)?evaluate(?=$|[\s;&|)])"
)


def command_invokes_evaluate(command: str | None) -> bool:
    return isinstance(command, str) and bool(EVALUATE_COMMAND_RE.search(command))


def evaluation_call_views(run: RunData) -> list[RequestView]:
    calls: list[RequestView] = []
    for view in run.requests:
        for call in view.response.tool_calls:
            if command_invokes_evaluate(call.command):
                calls.append(view)
    return calls


def request_normalized_cost(accounting: dict[str, Any]) -> float | None:
    for key in ("normalized_usd", "usd"):
        value = accounting.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)

    input_tokens = accounting.get("input_tokens")
    cached_tokens = accounting.get("cached_input_tokens")
    output_tokens = accounting.get("output_tokens")
    if not any(
        isinstance(value, (int, float)) and not isinstance(value, bool)
        for value in (input_tokens, cached_tokens, output_tokens)
    ):
        return None
    input_count = int(input_tokens or 0)
    cached_count = int(cached_tokens or 0)
    output_count = int(output_tokens or 0)
    noncached_count = max(0, input_count - cached_count)
    return (
        noncached_count * INPUT_PER_MTOK / 1_000_000
        + cached_count * CACHED_INPUT_PER_MTOK / 1_000_000
        + output_count * OUTPUT_PER_MTOK / 1_000_000
    )


def model_cost_timeline(run: RunData) -> list[tuple[datetime, float]]:
    """Return successful model responses with cumulative normalized cost."""
    request_costs: list[tuple[datetime, float]] = []
    for view in run.requests:
        timestamp = view.response_timestamp or view.timestamp
        cost = request_normalized_cost(view.accounting)
        if timestamp is not None and cost is not None:
            request_costs.append((timestamp, cost))
    request_costs.sort(key=lambda item: item[0])

    timeline: list[tuple[datetime, float]] = []
    running_cost = 0.0
    for timestamp, cost in request_costs:
        running_cost += cost
        timeline.append((timestamp, running_cost))
    return timeline


def cumulative_cost_at(
    timeline: list[tuple[datetime, float]],
    timestamp: datetime | None,
) -> float | None:
    if timestamp is None or not timeline:
        return None
    position = bisect_right(
        [event_timestamp for event_timestamp, _ in timeline],
        timestamp,
    ) - 1
    return timeline[position][1] if position >= 0 else 0.0


def evaluation_trajectory_points(
    run: RunData,
    cost_timeline: list[tuple[datetime, float]] | None = None,
) -> list[dict[str, Any]]:
    """Return report-compatible score/cumulative-cost points for one run."""
    calls = evaluation_call_views(run)
    if cost_timeline is None:
        cost_timeline = model_cost_timeline(run)

    points: list[dict[str, Any]] = []
    for index, event in enumerate(run.evals, start=1):
        score = score_number(event.get("score"))
        if score is None:
            continue
        timestamp = parse_ts(event.get("observed_at") or event.get("timestamp"))
        if timestamp is None and index <= len(calls):
            call = calls[index - 1]
            timestamp = call.response_timestamp or call.timestamp
        if timestamp is None and index <= len(run.legacy_eval_timestamps):
            timestamp = run.legacy_eval_timestamps[index - 1]

        cumulative_usd = None
        cumulative_usage = event.get("cumulative_usage")
        if isinstance(cumulative_usage, dict):
            cumulative_usd = score_number(
                cumulative_usage.get("normalized_usd")
            )
        cost_source = "evaluation usage snapshot"
        if cumulative_usd is None:
            cumulative_usd = cumulative_cost_at(cost_timeline, timestamp)
            cost_source = (
                "gateway accounting timeline"
                if cumulative_usd is not None
                else "unavailable"
            )

        avg_toffoli = score_number(event.get("avg_toffoli"))
        peak_qubits = event.get("peak_qubits")
        points.append(
            {
                "index": index,
                "timestamp": (
                    timestamp.isoformat()
                    if timestamp is not None
                    else None
                ),
                "cumulative_usd": (
                    float(cumulative_usd)
                    if cumulative_usd is not None
                    else None
                ),
                "cost_source": cost_source,
                "status": str(event.get("status") or "unknown"),
                "score": score,
                "avg_toffoli": avg_toffoli,
                "peak_qubits": (
                    int(peak_qubits)
                    if isinstance(peak_qubits, (int, float))
                    and not isinstance(peak_qubits, bool)
                    else None
                ),
            }
        )
    return points


def knowledge_base_trajectory_points(
    run: RunData,
    cost_timeline: list[tuple[datetime, float]],
) -> list[dict[str, Any]]:
    """Place KB activity on the same cumulative-cost chronology as evals."""
    points: list[dict[str, Any]] = []
    for event in run.kb_events:
        if event.get("event") != "knowledge_base_request" and not event.get(
            "action"
        ):
            continue
        index = len(points) + 1
        timestamp = parse_ts(event.get("observed_at") or event.get("timestamp"))
        if index <= len(run.legacy_kb_timestamps):
            timestamp = run.legacy_kb_timestamps[index - 1]

        cumulative_usd = None
        cumulative_usage = event.get("cumulative_usage")
        if isinstance(cumulative_usage, dict):
            cumulative_usd = score_number(
                cumulative_usage.get("normalized_usd")
            )
        cost_source = "event usage snapshot"
        if cumulative_usd is None:
            cumulative_usd = cumulative_cost_at(cost_timeline, timestamp)
            cost_source = (
                "gateway accounting timeline"
                if cumulative_usd is not None
                else "unavailable"
            )

        action = str(event.get("action") or "request")
        if event.get("page"):
            detail = str(event["page"])
        elif action == "search" and event.get("matches") is not None:
            detail = f"{fmt_int(event.get('matches'))} matches"
        elif action == "inspire":
            detail = (
                "qualifying"
                if event.get("qualifying")
                else "not qualifying"
            )
        else:
            detail = ""
        points.append(
            {
                "index": index,
                "timestamp": (
                    timestamp.isoformat()
                    if timestamp is not None
                    else None
                ),
                "cumulative_usd": (
                    float(cumulative_usd)
                    if cumulative_usd is not None
                    else None
                ),
                "cost_source": cost_source,
                "action": action,
                "detail": detail,
            }
        )
    return points


def evaluation_trajectory_data(
    run: RunData,
    markers: list[Marker],
    summary: dict[str, Any],
) -> dict[str, Any]:
    cost_timeline = model_cost_timeline(run)
    points = evaluation_trajectory_points(run, cost_timeline)
    knowledge_base = knowledge_base_trajectory_points(run, cost_timeline)
    evaluation_markers = [
        marker for marker in markers if marker.kind == "evaluation"
    ]
    for point in points:
        marker_index = int(point["index"]) - 1
        if 0 <= marker_index < len(evaluation_markers):
            point["anchor"] = evaluation_markers[marker_index].anchor
    knowledge_base_markers = [
        marker for marker in markers if marker.kind == "kb"
    ]
    for point in knowledge_base:
        marker_index = int(point["index"]) - 1
        if 0 <= marker_index < len(knowledge_base_markers):
            point["anchor"] = knowledge_base_markers[marker_index].anchor

    verifier_marker = next(
        (marker for marker in markers if marker.kind == "verifier"),
        None,
    )
    verifier = None
    if run.verifier_score is not None:
        current_usd = summary.get("total_usd")
        verifier = {
            "score": run.verifier_score,
            "cumulative_usd": (
                float(current_usd)
                if isinstance(current_usd, (int, float))
                and not isinstance(current_usd, bool)
                else max(
                    (
                        float(point["cumulative_usd"])
                        for point in points
                        if isinstance(
                            point.get("cumulative_usd"),
                            (int, float),
                        )
                        and not isinstance(
                            point.get("cumulative_usd"),
                            bool,
                        )
                    ),
                    default=0.0,
                )
            ),
            "metric": run.verifier_metric,
            "anchor": verifier_marker.anchor if verifier_marker else None,
        }
    return {
        "direction": run.metric_direction,
        "points": points,
        "knowledge_base": knowledge_base,
        "verifier": verifier,
        "current_usd": summary.get("total_usd"),
    }


def build_markers(run: RunData) -> list[Marker]:
    markers: list[Marker] = []

    # Place an evaluation immediately after the model response that invoked
    # `evaluate` when possible. Canonical evaluator timestamps and older
    # research-state timestamps are fallbacks for incomplete transcripts.
    eval_calls = evaluation_call_views(run)
    rs_evals = [e for e in run.research_state if e.get("kind") == "evaluation"]
    used_rs: set[int] = set()
    best: float | None = None
    for position, ev in enumerate(run.evals):
        status = str(ev.get("status") or "?")
        score = ev.get("score")
        timestamp: datetime | None = None
        request_id = None
        after_request = False
        if position < len(eval_calls):
            call_view = eval_calls[position]
            request_id = call_view.request_id
            timestamp = call_view.response_timestamp or call_view.timestamp
            after_request = True
        else:
            timestamp = parse_ts(ev.get("observed_at") or ev.get("timestamp"))
            if (
                timestamp is None
                and position < len(run.legacy_eval_timestamps)
            ):
                timestamp = run.legacy_eval_timestamps[position]
            for rs_index, rs in enumerate(rs_evals):
                if rs_index in used_rs:
                    continue
                same_candidate = (
                    rs.get("candidate_sha256")
                    and rs.get("candidate_sha256") == ev.get("candidate_sha256")
                )
                if same_candidate or (
                    len(rs_evals) == len(run.evals) and rs_index == position
                ):
                    timestamp = timestamp or parse_ts(rs.get("observed_at"))
                    used_rs.add(rs_index)
                    break
        if request_id is None and timestamp is None:
            needles = []
            if isinstance(score, (int, float)) and is_ok_status(status):
                needles.append(f"score: {fmt_score(score).replace(',', '')}")
            sha = ev.get("candidate_sha256")
            if isinstance(sha, str) and len(sha) >= 12:
                needles.append(sha[:12])
            for view in run.requests:
                if any(any(n in m.text for n in needles) for m in view.messages):
                    request_id = view.request_id
                    break
        is_ok = is_ok_status(status)
        if is_ok and isinstance(score, (int, float)):
            if best is None or (score < best if run.metric_direction == "minimize" else score > best):
                best = float(score)
                improved = True
            else:
                improved = False
        else:
            improved = False
        label = f"evaluation #{position + 1}: {status}"
        if isinstance(score, (int, float)):
            label += f" score {fmt_score(score)}"
        if improved:
            label += " (new best)"
        detail_parts = []
        if ev.get("avg_toffoli") is not None:
            detail_parts.append(f"avg_toffoli {fmt_score(ev.get('avg_toffoli'))}")
        if ev.get("peak_qubits") is not None:
            detail_parts.append(f"peak_qubits {fmt_int(ev.get('peak_qubits'))}")
        cumulative_usage = ev.get("cumulative_usage")
        if isinstance(cumulative_usage, dict):
            detail_parts.append(
                f"cost {fmt_usd(cumulative_usage.get('normalized_usd'))}"
            )
        if best is not None:
            detail_parts.append(f"best so far {fmt_score(best)}")
        if ev.get("candidate_sha256"):
            detail_parts.append(f"candidate {str(ev['candidate_sha256'])[:12]}")
        if ev.get("error") or ev.get("message"):
            detail_parts.append(str(ev.get("error") or ev.get("message"))[:200])
        css = "eval-ok" if is_ok else "eval-bad"
        marker = Marker("evaluation", label, " · ".join(detail_parts), timestamp, request_id, css=css)
        marker.after_request = after_request
        markers.append(marker)

    if run.verifier_score is not None:
        detail_parts = ["authoritative final score"]
        if best is not None:
            detail_parts.append(f"best evaluation {fmt_score(best)}")
        if run.verifier_metric:
            detail_parts.append(f"metric {run.verifier_metric}")
        markers.append(
            Marker(
                "verifier",
                f"final verifier: score {fmt_score(run.verifier_score)}",
                " · ".join(detail_parts),
                run.verifier_finished_at,
                None,
                css="verifier",
            )
        )

    # Research-state transitions and controller lifecycle events.
    last_stale: bool | None = None
    for event in run.research_state:
        kind = event.get("kind")
        timestamp = parse_ts(event.get("observed_at") or event.get("timestamp"))
        if kind == "model_usage":
            staleness = event.get("evaluation_staleness") if isinstance(event.get("evaluation_staleness"), dict) else {}
            stale = staleness.get("stale")
            if isinstance(stale, bool) and stale != last_stale and (stale or last_stale is not None):
                request_id = _request_id_from_event_id(event.get("event_id"))
                if stale:
                    detail = (
                        f"{staleness.get('model_requests_since_evaluation', '?')} requests / "
                        f"{staleness.get('seconds_since_evaluation', '?')}s since last evaluation"
                    )
                    markers.append(Marker("stale", "research-state: evaluation STALE", detail, timestamp, request_id, css="stale-on"))
                else:
                    markers.append(Marker("stale", "research-state: evaluation fresh again", "", timestamp, request_id, css="stale-off"))
            if isinstance(stale, bool):
                last_stale = stale
        elif kind in ("evaluation",):
            continue  # represented by authoritative evaluator events above
        elif kind:
            detail = ", ".join(
                f"{k}={v}" for k, v in event.items()
                if k not in ("kind", "observed_at", "run_id", "schema_version", "event_id") and not isinstance(v, (dict, list))
            )
            css = "lifecycle"
            if kind == "completion_attempt":
                css = "completion"
            markers.append(Marker(str(kind), f"research-state: {kind}", detail[:300], timestamp, None, css=css))

    # Gateway budget rejections.
    for event in run.gateway_events:
        if event.get("event") == "budget_rejected":
            markers.append(
                Marker(
                    "budget_rejected",
                    "gateway: budget_rejected",
                    f"{event.get('operation', '')} — {event.get('reason', '')}",
                    parse_ts(event.get("timestamp")),
                    None,
                    css="budget",
                )
            )

    # Hook deliveries (research-state delivery events) — show failures only.
    for event in run.delivery_events:
        status = str(event.get("status") or "")
        if status and status != "success":
            markers.append(
                Marker(
                    "hook",
                    f"hook delivery {status}: {event.get('path', '')}",
                    str(event.get("error_type") or event.get("error") or ""),
                    parse_ts(event.get("observed_at") or event.get("timestamp")),
                    _request_id_from_event_id(event.get("event_id")),
                    css="hook",
                )
            )

    # Knowledge-base requests (muted context).
    kb_position = 0
    for event in run.kb_events:
        if event.get("event") == "knowledge_base_request" or event.get("action"):
            timestamp = parse_ts(
                event.get("observed_at") or event.get("timestamp")
            )
            if kb_position < len(run.legacy_kb_timestamps):
                timestamp = run.legacy_kb_timestamps[kb_position]
            kb_position += 1
            action = str(event.get("action") or "request")
            target = ""
            if event.get("page"):
                target = f": {event['page']}"
            elif action == "search" and event.get("matches") is not None:
                target = f": {fmt_int(event.get('matches'))} matches"
            elif action == "inspire":
                target = ": qualifying" if event.get("qualifying") else ": not qualifying"
            details = []
            if event.get("bytes") is not None:
                details.append(f"{fmt_int(event.get('bytes'))} bytes")
            if event.get("search_id"):
                details.append(str(event["search_id"]))
            if event.get("reason"):
                details.append(str(event["reason"]))
            markers.append(
                Marker(
                    "kb",
                    f"knowledge-base {action}{target}",
                    " · ".join(details),
                    timestamp,
                    None,
                    css="kb",
                )
            )
    return markers


def place_markers(run: RunData, markers: list[Marker]) -> tuple[dict[int, list[Marker]], list[Marker]]:
    """Return ({slot: markers}, unplaced). Slot i means "before request index i (1-based)";
    slot len(requests)+1 means after the last request."""
    slots: dict[int, list[Marker]] = {}
    unplaced: list[Marker] = []
    by_id = {view.request_id: view for view in run.requests}
    for marker in markers:
        slot: int | None = None
        if marker.request_id and marker.request_id in by_id:
            view = by_id[marker.request_id]
            slot = view.index + 1 if marker.after_request else view.index
        elif marker.timestamp is not None:
            slot = len(run.requests) + 1
            for view in run.requests:
                if view.timestamp is not None and view.timestamp > marker.timestamp:
                    slot = view.index
                    break
        if slot is None:
            unplaced.append(marker)
        else:
            marker.slot = slot
            slots.setdefault(slot, []).append(marker)
    for slot_markers in slots.values():
        slot_markers.sort(key=lambda m: (m.timestamp or datetime.min.replace(tzinfo=timezone.utc)))
    return slots, unplaced


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

CSS = """
:root{--bg:#f4f5f7;--card:#fff;--ink:#1d2129;--muted:#6b7280;--line:#e2e5ea;
--sys:#eef2ff;--sysb:#4f46e5;--usr:#ecfdf5;--usrb:#059669;--asst:#fff7ed;--asstb:#ea580c;
--tool:#f1f5f9;--toolb:#475569;--harness:#fef3c7;--harnessb:#b45309;--danger:#dc2626;--amber:#d97706;--green:#15803d;}
*{box-sizing:border-box}
body{margin:0;overflow-x:hidden;font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
header.run{width:100vw;background:#111827;color:#f9fafb;padding:16px 24px}
header.run h1{margin:0 0 6px;font-size:18px;font-weight:600;overflow-wrap:anywhere}
header.run .stats{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px}
header.run .stats b{color:#fff}
header.run .stats span{min-width:0;color:#cbd5e1;overflow-wrap:anywhere}
header.run .err{color:#fca5a5}
header.run .term{color:#fde68a}
header.run .security{color:#f0abfc}
.controls{width:100vw;position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);padding:8px 24px;display:flex;gap:10px;align-items:center;font-size:13px}
.controls button{font:inherit;padding:4px 10px;border:1px solid #cbd5e1;border-radius:6px;background:#f8fafc;cursor:pointer}
.controls button:hover{background:#eef2f7}
.eval-trajectory-shell{width:100vw;max-width:1540px;margin:0 auto;padding:16px 24px 0}
.eval-trajectory{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.eval-trajectory-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:3px}
.eval-trajectory-head>*{min-width:0;max-width:100%}
.eval-trajectory h2{margin:0;font-size:15px;font-weight:600;overflow-wrap:anywhere}
.eval-trajectory-summary{color:var(--muted);font-size:12px;overflow-wrap:anywhere}
.eval-trajectory-legend{display:flex;gap:14px;align-items:center;flex-wrap:wrap;color:var(--muted);font-size:11px;margin-bottom:3px}
.eval-trajectory-legend span{display:inline-flex;gap:5px;align-items:center}
.eval-trajectory-legend i{display:inline-block;width:9px;height:9px}
.eval-trajectory-legend .valid{border-radius:50%;background:var(--green)}
.eval-trajectory-legend .invalid{position:relative;width:10px;height:10px}
.eval-trajectory-legend .invalid::before,.eval-trajectory-legend .invalid::after{content:"";position:absolute;left:4px;top:0;width:2px;height:11px;background:var(--danger)}
.eval-trajectory-legend .invalid::before{transform:rotate(45deg)}
.eval-trajectory-legend .invalid::after{transform:rotate(-45deg)}
.eval-trajectory-legend .final{border-radius:2px;background:#7c3aed;transform:rotate(45deg)}
.eval-trajectory-legend .kb{border-radius:2px;background:#4f46e5;transform:rotate(45deg)}
.eval-trajectory-chart{width:100%;min-height:290px}
.eval-trajectory-chart svg{display:block;width:100%;height:auto;overflow:visible}
.eval-chart-frame{fill:#fff;stroke:var(--line);stroke-width:1}
.eval-chart-grid{stroke:#e5e7eb;stroke-width:1}
.eval-chart-axis{stroke:#94a3b8;stroke-width:1}
.eval-chart-tick,.eval-chart-axis-title,.eval-chart-label{fill:var(--ink);font-size:12px;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.eval-chart-tick{fill:var(--muted)}
.eval-chart-axis-title{font-weight:600}
.eval-chart-line{fill:none;stroke:var(--green);stroke-width:2}
.eval-chart-valid{fill:var(--green);stroke:#fff;stroke-width:1.5;cursor:pointer}
.eval-chart-invalid{stroke:var(--danger);stroke-width:2;cursor:pointer}
.eval-chart-final{fill:#7c3aed;stroke:#fff;stroke-width:1.5;cursor:pointer}
.eval-chart-best-label{fill:var(--green);font-weight:600}
.eval-chart-final-label{fill:#7c3aed;font-weight:600}
.eval-chart-kb-guide{stroke:#4f46e5;stroke-width:1;stroke-dasharray:2 3;opacity:.24}
.eval-chart-kb{fill:#4f46e5;stroke:#fff;stroke-width:1;cursor:pointer}
.eval-chart-kb-label{fill:#4338ca;font-size:10px;font-weight:600;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.eval-chart-kb-lane{fill:#4338ca;font-size:11px;font-weight:600;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.eval-chart-empty{fill:var(--muted);font-size:13px}
.page-shell{width:100vw;max-width:1540px;margin:0 auto;padding:16px 24px 60px;display:grid;grid-template-columns:minmax(0,1200px) 276px;gap:20px;align-items:start}
main{min-width:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:12px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.card>summary{list-style:none;cursor:pointer;padding:10px 14px;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-size:13px}
.card>summary::-webkit-details-marker{display:none}
.card>summary .idx{font-weight:700;font-size:14px;min-width:38px}
.card>summary .kv{color:var(--muted)}
.card>summary .kv b{color:var(--ink);font-weight:600}
.card.break>summary{border-left:6px solid var(--danger)}
.card.noTool>summary{border-left:6px solid var(--amber)}
.body{border-top:1px solid var(--line);padding:12px 14px}
.badge{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:.2px;vertical-align:middle}
.badge.break{background:var(--danger);color:#fff}
.badge.notool{background:var(--amber);color:#fff}
.badge.stale{background:#7f1d1d;color:#fff}
.badge.harness{background:var(--harnessb);color:#fff}
.badge.changed{background:#fde68a;color:#78350f}
.badge.new{background:#dcfce7;color:#14532d}
.badge.tail{background:#e0e7ff;color:#3730a3}
.badge.rs{background:#fbbf24;color:#451a03}
.badge.info{background:#e5e7eb;color:#374151}
.badge.err{background:#fecaca;color:#7f1d1d}
.ratio-red{color:var(--danger);font-weight:700}
.ratio-amber{color:var(--amber);font-weight:700}
.ratio-green{color:var(--green);font-weight:700}
.ratio-none{color:var(--muted)}
.note{color:var(--muted);font-size:13px;margin:6px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.note button,.msg button,.resp button{font:inherit;font-size:12px;padding:2px 8px;border:1px solid #cbd5e1;border-radius:6px;background:#f8fafc;cursor:pointer}
.alert{background:#fef2f2;border:1px solid #fecaca;color:#7f1d1d;border-radius:8px;padding:8px 12px;margin:8px 0;font-weight:600}
.alert.soft{background:#fffbeb;border-color:#fde68a;color:#78350f;font-weight:500}
.msg{border-radius:8px;padding:8px 12px;margin:8px 0;border-left:4px solid var(--toolb);background:var(--tool);max-width:100%}
.msg.system,.msg.developer{background:var(--sys);border-color:var(--sysb)}
.msg.user{background:var(--usr);border-color:var(--usrb)}
.msg.assistant{background:var(--asst);border-color:var(--asstb)}
.msg.tool{background:var(--tool);border-color:var(--toolb)}
.msg.harness{background:var(--harness);border-color:var(--harnessb);outline:2px dashed var(--harnessb);outline-offset:-2px}
.msg.flag-changed{box-shadow:inset 0 0 0 2px #f59e0b}
.msg .head{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px;color:var(--muted);margin-bottom:4px}
.msg .head .role{font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--ink)}
.msg pre,.resp pre{margin:4px 0;white-space:pre-wrap;word-break:break-word;font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.msg .text{white-space:pre-wrap;word-break:break-word}
.msg.tool .text{font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#fff;border:1px solid var(--line);border-radius:6px;padding:6px 8px}
.more[hidden]{display:none}
.tc{font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#fff;border:1px solid var(--line);border-radius:6px;padding:4px 8px;margin:3px 0;word-break:break-word;white-space:pre-wrap}
.tc .name{color:#7c3aed;font-weight:700}
.tc .extras{color:var(--muted)}
.reasoning{background:#faf5ff;border-left:4px solid #a855f7;border-radius:8px;padding:6px 12px;margin:6px 0;color:#3b0764;white-space:pre-wrap;word-break:break-word;font-size:13px}
.resp{margin-top:14px;border-top:2px dashed var(--line);padding-top:10px}
.resp h4,.body h4{margin:4px 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted)}
.resp .text{background:var(--asst);border-left:4px solid var(--asstb);border-radius:8px;padding:8px 12px;white-space:pre-wrap;word-break:break-word}
.resp-sequence{display:flex;flex-direction:column;gap:8px;margin:6px 0}
.resp-block{border:1px solid var(--line);border-radius:8px;padding:7px 10px;background:#fff}
.resp-block .seqhead{display:flex;gap:8px;align-items:center;color:var(--muted);font-size:12px;margin-bottom:4px}
.resp-block .seqnum{display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;border-radius:999px;background:#e5e7eb;color:#374151;font-weight:700}
.resp-block .seqkind{font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--ink)}
.resp-block.rb-thinking{background:#faf5ff;border-color:#e9d5ff}
.resp-block.rb-text{background:#fff7ed;border-color:#fed7aa}
.resp-block.rb-tool-use,.resp-block.rb-tool-result{background:#f8fafc;border-color:#cbd5e1}
.resp-block .reasoning,.resp-block .text{margin:0}
.marker{display:flex;gap:10px;align-items:baseline;margin:6px 0 6px 12px;padding:6px 12px;border-radius:8px;font-size:13px;border-left:4px solid #94a3b8;background:#fff;scroll-margin-top:58px}
.marker .t{color:var(--muted);font-variant-numeric:tabular-nums;min-width:66px}
.marker .d{color:var(--muted)}
.marker.eval-ok{border-color:var(--green);background:#f0fdf4}
.marker.eval-bad{border-color:var(--danger);background:#fef2f2}
.marker.verifier{border-color:#7c3aed;background:#faf5ff;font-weight:600}
.marker.stale-on{border-color:#7f1d1d;background:#fef2f2;font-weight:600}
.marker.stale-off{border-color:var(--green);background:#f0fdf4}
.marker.budget{border-color:var(--danger);background:#fef2f2;font-weight:600}
.marker.hook{border-color:var(--amber);background:#fffbeb}
.marker.completion,.marker.lifecycle{border-color:#4f46e5;background:#eef2ff}
.marker.kb{border-color:#cbd5e1;background:#f8fafc;color:var(--muted);font-size:12px;padding:3px 12px}
.rail{background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px 14px;margin:12px 0}
.rail h3{margin:4px 0 8px;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.progress-sidebar{min-width:0;position:sticky;top:58px;align-self:start;max-height:calc(100vh - 74px)}
.progress-panel{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;box-shadow:0 1px 2px rgba(0,0,0,.04);max-height:inherit;display:flex;flex-direction:column;gap:10px}
.progress-panel h2{margin:0;font-size:14px}
.progress-status{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.progress-summary{display:flex;gap:10px;flex-wrap:wrap;color:var(--muted);font-size:11px}
.progress-summary b{color:var(--ink)}
.progress-map{display:grid;grid-template-columns:34px minmax(0,1fr);gap:9px;min-height:220px}
.progress-track{position:relative;margin:7px 0;min-height:206px}
.progress-axis{position:absolute;left:16px;top:0;bottom:0;width:3px;border-radius:3px;background:#e2e8f0}
.progress-current{position:absolute;z-index:4;left:3px;top:0;width:29px;height:3px;border-radius:3px;background:#111827;transform:translateY(-1px);transition:top .12s ease}
.progress-current::after{content:"";position:absolute;right:-2px;top:-4px;width:10px;height:10px;border:2px solid #fff;border-radius:50%;background:#111827;box-shadow:0 0 0 1px #111827}
.progress-point{position:absolute;z-index:3;display:block;padding:0;border:2px solid #fff;box-shadow:0 0 0 1px currentColor;transform:translate(-50%,-50%);cursor:pointer}
.progress-point.eval{left:11px;width:13px;height:13px;border-radius:50%;color:var(--green);background:var(--green)}
.progress-point.eval.bad{color:var(--danger);background:var(--danger)}
.progress-point.verifier{left:11px;width:15px;height:15px;border-radius:3px;color:#7c3aed;background:#7c3aed;transform:translate(-50%,-50%) rotate(45deg)}
.progress-point.kb{left:23px;width:9px;height:9px;border-radius:2px;color:#4f46e5;background:#4f46e5;transform:translate(-50%,-50%) rotate(45deg)}
.progress-scale{position:relative;color:var(--muted);font-size:10px}
.progress-scale span{position:absolute;left:0}
.progress-scale .start{top:0}
.progress-scale .end{bottom:0}
.progress-legend{display:flex;gap:12px;align-items:center;color:var(--muted);font-size:11px}
.progress-legend span{display:inline-flex;gap:5px;align-items:center}
.progress-legend i{display:inline-block;width:8px;height:8px}
.progress-legend .eval-key{border-radius:50%;background:var(--green)}
.progress-legend .verifier-key{border-radius:2px;background:#7c3aed;transform:rotate(45deg)}
.progress-legend .kb-key{border-radius:2px;background:#4f46e5;transform:rotate(45deg)}
.progress-events{flex:1;min-height:0;overflow:auto;border-top:1px solid var(--line);padding-top:7px}
.progress-event{display:grid;grid-template-columns:27px minmax(0,1fr);gap:7px;padding:6px 4px;color:var(--ink);text-decoration:none;border-radius:6px;opacity:.55}
.progress-event:hover{background:#f8fafc;opacity:1}
.progress-event.past{opacity:1}
.progress-event.current{background:#eef2ff;box-shadow:inset 3px 0 #4f46e5}
.progress-event .glyph{display:flex;align-items:center;justify-content:center;width:24px;height:20px;border-radius:5px;font-size:9px;font-weight:700;color:#fff;background:#4f46e5}
.progress-event.eval .glyph{background:var(--green)}
.progress-event.eval.bad .glyph{background:var(--danger)}
.progress-event.verifier .glyph{background:#7c3aed}
.progress-event strong{display:block;font-size:11px;line-height:1.3;font-weight:600}
.progress-event small{display:block;color:var(--muted);font-size:10px;line-height:1.3;margin-top:2px}
.progress-empty{color:var(--muted);font-size:12px;padding:8px 2px}
.card.full .delta{display:none}
.card:not(.full) .fullctx{display:none}
.tools{font-size:12px;color:var(--muted);margin:4px 0 8px}
.note.stub{background:#fff7ed;border:1px dashed #fdba74;border-radius:8px;padding:6px 10px;color:#7c2d12}
.warn{background:#fffbeb;border:1px solid #fde68a;padding:6px 12px;border-radius:8px;margin:8px 0;font-size:13px}
@media(max-width:1050px){
  .page-shell{grid-template-columns:minmax(0,1fr) 230px;gap:14px;padding-left:14px;padding-right:14px}
}
@media(max-width:760px){
  header.run{padding:14px 12px}
  .controls{padding:8px 10px;flex-wrap:wrap}
  .eval-trajectory-shell{padding:10px 10px 0}
  .eval-trajectory{padding:12px 10px}
  .eval-trajectory-chart{min-height:260px}
  .page-shell{display:block;padding:10px 10px 48px}
  .progress-sidebar{position:static;max-height:none;margin-top:14px}
  .progress-panel{max-height:none}
  .progress-map{min-height:150px}
  .progress-track{min-height:136px}
  .progress-events{max-height:240px}
}
"""

JS = """
function toggleMore(btn){var m=btn.previousElementSibling;if(!m)return;m.hidden=!m.hidden;btn.textContent=m.hidden?btn.getAttribute('data-more'):'show less';}
function buildFull(card){var ctx=card.querySelector('.fullctx');if(!ctx||ctx.getAttribute('data-built'))return;var ids=(card.getAttribute('data-full')||'').split(' ');for(var i=0;i<ids.length;i++){if(!ids[i])continue;var src=document.getElementById(ids[i]);if(!src){var p=document.createElement('div');p.className='note';p.textContent='[message '+ids[i]+' not found]';ctx.appendChild(p);continue;}var c=src.cloneNode(true);c.removeAttribute('id');ctx.appendChild(c);}ctx.setAttribute('data-built','1');}
function setFull(card,full){if(full){buildFull(card);card.classList.add('full');}else{card.classList.remove('full');}var b=card.querySelector('.viewbtn');if(b)b.textContent=full?'show delta only':'show full context';}
function toggleFull(btn){var card=btn.closest('.card');setFull(card,!card.classList.contains('full'));}
function allFull(full){var cards=document.querySelectorAll('.card');for(var i=0;i<cards.length;i++){setFull(cards[i],full);}}
function allOpen(open){var cards=document.querySelectorAll('.card');for(var i=0;i<cards.length;i++){cards[i].open=open;}}
var evalTrajectoryResizeTimer=null;
function evalSvg(name,attrs,text){
  var node=document.createElementNS('http://www.w3.org/2000/svg',name);
  if(attrs){for(var key in attrs){if(Object.prototype.hasOwnProperty.call(attrs,key)&&attrs[key]!==null&&attrs[key]!==undefined)node.setAttribute(key,String(attrs[key]));}}
  if(text!==undefined&&text!==null)node.textContent=String(text);
  return node;
}
function evalScore(value){
  var n=Number(value);if(!isFinite(n))return '-';
  if(Math.abs(n)>=1000000000)return (n/1000000000).toFixed(n>=10000000000?2:3).replace(/0+$/,'').replace(/\\.$/,'')+'B';
  if(Math.abs(n)>=1000000)return (n/1000000).toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'M';
  if(Math.abs(n)>=1000)return (n/1000).toFixed(1).replace(/\\.0$/,'')+'K';
  return n.toLocaleString(undefined,{maximumFractionDigits:3});
}
function evalUsd(value){
  var n=Number(value);if(!isFinite(n))return '-';
  return '$'+n.toFixed(n<1?2:n<10?2:1).replace(/\\.0$/,'');
}
function evalIsValid(point){
  var status=String(point.status||'').toLowerCase();
  return (status==='ok'||status==='valid'||status==='success')&&isFinite(Number(point.score))&&Number(point.score)>0;
}
function evalHasCost(point){
  return !!point&&point.cumulative_usd!==null&&point.cumulative_usd!==undefined&&point.cumulative_usd!==''&&isFinite(Number(point.cumulative_usd));
}
function evalTooltip(point){
  var lines=['Evaluation #'+point.index,String(point.status||'unknown'),'cost '+evalUsd(point.cumulative_usd),'score '+Number(point.score).toLocaleString()];
  if(point.avg_toffoli!==null&&point.avg_toffoli!==undefined)lines.push('avg Toffoli '+Number(point.avg_toffoli).toLocaleString());
  if(point.peak_qubits!==null&&point.peak_qubits!==undefined)lines.push('peak qubits '+Number(point.peak_qubits).toLocaleString());
  if(point.cost_source)lines.push('cost source: '+point.cost_source);
  return lines.join(' · ');
}
function evalKbTooltip(point){
  var lines=['KB'+point.index,String(point.action||'request')];
  if(point.detail)lines.push(String(point.detail));
  lines.push('cost '+evalUsd(point.cumulative_usd));
  if(point.timestamp)lines.push(String(point.timestamp));
  if(point.cost_source)lines.push('cost source: '+point.cost_source);
  return lines.join(' · ');
}
function evalLinkedMark(mark,anchor,label){
  mark.appendChild(evalSvg('title',null,label));
  if(!anchor)return mark;
  var link=evalSvg('a',{href:'#'+anchor,'aria-label':label});
  link.appendChild(mark);return link;
}
function drawEvalTrajectory(){
  var host=document.getElementById('eval-trajectory-chart');
  var source=document.getElementById('eval-trajectory-data');
  if(!host||!source)return;
  var data;try{data=JSON.parse(source.textContent||'{}');}catch(error){host.textContent='Could not parse evaluation trajectory data.';return;}
  var width=Math.max(300,Math.floor(host.getBoundingClientRect().width||900));
  var compact=width<560;
  var height=compact?328:378;
  var margin={left:compact?64:78,right:compact?14:26,top:64,bottom:56};
  var plotWidth=Math.max(1,width-margin.left-margin.right);
  var plotHeight=Math.max(1,height-margin.top-margin.bottom);
  var points=Array.isArray(data.points)?data.points:[];
  var costedPoints=points.filter(evalHasCost);
  var valid=costedPoints.filter(evalIsValid);
  var invalid=costedPoints.filter(function(point){return !evalIsValid(point);});
  var validWithoutCost=points.filter(function(point){return evalIsValid(point)&&!evalHasCost(point);});
  var knowledgeBase=(Array.isArray(data.knowledge_base)?data.knowledge_base:[]).filter(evalHasCost);
  var verifier=data.verifier&&evalHasCost(data.verifier)&&isFinite(Number(data.verifier.score))&&Number(data.verifier.score)>0?data.verifier:null;
  var yValues=valid.map(function(point){return Number(point.score);});
  if(verifier)yValues.push(Number(verifier.score));
  var xValues=costedPoints.map(function(point){return Number(point.cumulative_usd);});
  for(var ki=0;ki<knowledgeBase.length;ki++)xValues.push(Number(knowledgeBase[ki].cumulative_usd));
  if(verifier)xValues.push(Number(verifier.cumulative_usd));
  if(data.current_usd!==null&&data.current_usd!==undefined&&data.current_usd!==''&&isFinite(Number(data.current_usd)))xValues.push(Number(data.current_usd));
  var xMax=Math.max.apply(null,[1].concat(xValues))*1.025;
  var hasScores=yValues.length>0;
  var logMin=0,logMax=1;
  if(hasScores){
    logMin=Math.log10(Math.min.apply(null,yValues));
    logMax=Math.log10(Math.max.apply(null,yValues));
    if(Math.abs(logMax-logMin)<0.001){logMin-=0.08;logMax+=0.08;}
    else{var yPad=(logMax-logMin)*0.09;logMin-=yPad;logMax+=yPad;}
  }
  function x(value){return margin.left+(Math.max(0,Number(value))/xMax)*plotWidth;}
  function y(value){var lv=Math.log10(Math.max(Number(value),Number.MIN_VALUE));return margin.top+((logMax-lv)/(logMax-logMin))*plotHeight;}
  var svg=evalSvg('svg',{viewBox:'0 0 '+width+' '+height,role:'img','aria-labelledby':'eval-chart-title eval-chart-desc'});
  svg.appendChild(evalSvg('title',{id:'eval-chart-title'},'Evaluation score and knowledge-base activity versus cumulative model spend'));
  svg.appendChild(evalSvg('desc',{id:'eval-chart-desc'},costedPoints.length+' of '+points.length+' evaluations and '+knowledgeBase.length+' knowledge-base calls plotted by cumulative normalized USD. '+(data.direction==='maximize'?'Higher':'Lower')+' score is better.'));
  svg.appendChild(evalSvg('rect',{class:'eval-chart-frame',x:margin.left,y:margin.top,width:plotWidth,height:plotHeight}));

  if(knowledgeBase.length){
    svg.appendChild(evalSvg('text',{class:'eval-chart-kb-lane',x:margin.left,y:12},'KB activity'));
    var kbLastByLane=[-Infinity,-Infinity,-Infinity];
    var kbLastLabel=-Infinity;
    var kbLabelGap=compact?42:31;
    for(var kbi=0;kbi<knowledgeBase.length;kbi++){
      var kbPoint=knowledgeBase[kbi],kbX=x(kbPoint.cumulative_usd),kbLane=0;
      for(var candidateLane=0;candidateLane<3;candidateLane++){
        if(kbX-kbLastByLane[candidateLane]>=11){kbLane=candidateLane;break;}
        if(kbLastByLane[candidateLane]<kbLastByLane[kbLane])kbLane=candidateLane;
      }
      kbLastByLane[kbLane]=kbX;
      var kbY=20+kbLane*13,kbSize=4;
      svg.appendChild(evalSvg('line',{class:'eval-chart-kb-guide',x1:kbX,y1:kbY+kbSize,x2:kbX,y2:margin.top}));
      var kbDiamond=evalSvg('polygon',{class:'eval-chart-kb',points:kbX+','+(kbY-kbSize)+' '+(kbX+kbSize)+','+kbY+' '+kbX+','+(kbY+kbSize)+' '+(kbX-kbSize)+','+kbY});
      svg.appendChild(evalLinkedMark(kbDiamond,kbPoint.anchor,evalKbTooltip(kbPoint)));
      var labelAllowed=kbX-kbLastLabel>=kbLabelGap||kbi===knowledgeBase.length-1;
      if(labelAllowed){
        var kbLabelLeft=kbX>width-45;
        svg.appendChild(evalSvg('text',{class:'eval-chart-kb-label',x:kbX+(kbLabelLeft?-6:6),y:kbY+3,'text-anchor':kbLabelLeft?'end':'start'},'KB'+kbPoint.index));
        kbLastLabel=kbX;
      }
    }
  }

  var xTicks=compact?4:6;
  for(var xi=0;xi<xTicks;xi++){
    var xValue=xMax*xi/(xTicks-1),xPos=x(xValue);
    svg.appendChild(evalSvg('line',{class:'eval-chart-grid',x1:xPos,y1:margin.top,x2:xPos,y2:margin.top+plotHeight}));
    svg.appendChild(evalSvg('text',{class:'eval-chart-tick',x:xPos,y:margin.top+plotHeight+19,'text-anchor':xi===0?'start':xi===xTicks-1?'end':'middle'},evalUsd(xValue)));
  }
  if(hasScores){
    var yTicks=compact?4:5;
    for(var yi=0;yi<yTicks;yi++){
      var yLog=logMin+(logMax-logMin)*yi/(yTicks-1);
      var yValue=Math.pow(10,yLog),yPos=y(yValue);
      svg.appendChild(evalSvg('line',{class:'eval-chart-grid',x1:margin.left,y1:yPos,x2:margin.left+plotWidth,y2:yPos}));
      svg.appendChild(evalSvg('text',{class:'eval-chart-tick',x:margin.left-9,y:yPos+4,'text-anchor':'end'},evalScore(yValue)));
    }
  }
  svg.appendChild(evalSvg('line',{class:'eval-chart-axis',x1:margin.left,y1:margin.top+plotHeight,x2:margin.left+plotWidth,y2:margin.top+plotHeight}));
  svg.appendChild(evalSvg('line',{class:'eval-chart-axis',x1:margin.left,y1:margin.top,x2:margin.left,y2:margin.top+plotHeight}));
  svg.appendChild(evalSvg('text',{class:'eval-chart-axis-title',x:margin.left+plotWidth/2,y:height-9,'text-anchor':'middle'},'Cumulative normalized model cost (USD)'));
  var yTitle=evalSvg('text',{class:'eval-chart-axis-title',x:16,y:margin.top+plotHeight/2,'text-anchor':'middle',transform:'rotate(-90 16 '+(margin.top+plotHeight/2)+')'},'Authoritative score (log scale)');
  svg.appendChild(yTitle);

  if(valid.length){
    var path='';
    for(var pi=0;pi<valid.length;pi++)path+=(pi?'L':'M')+x(valid[pi].cumulative_usd).toFixed(2)+' '+y(valid[pi].score).toFixed(2)+' ';
    svg.appendChild(evalSvg('path',{class:'eval-chart-line',d:path.trim()}));
    for(var vi=0;vi<valid.length;vi++){
      var point=valid[vi];
      var circle=evalSvg('circle',{class:'eval-chart-valid',cx:x(point.cumulative_usd),cy:y(point.score),r:compact?4.5:5.5});
      svg.appendChild(evalLinkedMark(circle,point.anchor,evalTooltip(point)));
    }
    var direction=String(data.direction||'minimize');
    var best=valid[0];
    for(var bi=1;bi<valid.length;bi++){
      if((direction==='maximize'&&Number(valid[bi].score)>Number(best.score))||(direction!=='maximize'&&Number(valid[bi].score)<Number(best.score)))best=valid[bi];
    }
    var bestX=x(best.cumulative_usd),bestY=y(best.score),bestLeft=bestX>width-125;
    svg.appendChild(evalSvg('text',{class:'eval-chart-label eval-chart-best-label',x:bestX+(bestLeft?-8:8),y:Math.max(margin.top+13,bestY-9),'text-anchor':bestLeft?'end':'start'},'best eval '+evalScore(best.score)));
  }
  var invalidY=margin.top+10;
  for(var ii=0;ii<invalid.length;ii++){
    var invalidPoint=invalid[ii],invalidX=x(invalidPoint.cumulative_usd);
    var group=evalSvg('g',{class:'eval-chart-invalid'});
    group.appendChild(evalSvg('line',{x1:invalidX-5,y1:invalidY-5,x2:invalidX+5,y2:invalidY+5}));
    group.appendChild(evalSvg('line',{x1:invalidX-5,y1:invalidY+5,x2:invalidX+5,y2:invalidY-5}));
    svg.appendChild(evalLinkedMark(group,invalidPoint.anchor,evalTooltip(invalidPoint)));
  }
  if(verifier&&hasScores){
    var finalX=x(verifier.cumulative_usd),finalY=y(verifier.score),size=compact?6:7;
    var diamond=evalSvg('polygon',{class:'eval-chart-final',points:finalX+','+(finalY-size)+' '+(finalX+size)+','+finalY+' '+finalX+','+(finalY+size)+' '+(finalX-size)+','+finalY});
    var finalLabel='Final verifier · cost '+evalUsd(verifier.cumulative_usd)+' · score '+Number(verifier.score).toLocaleString();
    svg.appendChild(evalLinkedMark(diamond,verifier.anchor,finalLabel));
    var finalLeft=finalX>width-130;
    svg.appendChild(evalSvg('text',{class:'eval-chart-label eval-chart-final-label',x:finalX+(finalLeft?-9:9),y:Math.min(margin.top+plotHeight-5,finalY+18),'text-anchor':finalLeft?'end':'start'},'final '+evalScore(verifier.score)));
  }
  if(!hasScores){
    var emptyMessage=points.length?(validWithoutCost.length?'Evaluation scores exist, but their spend positions are unavailable.':'No valid score yet; invalid evaluations are marked at the top.'):'No evaluations recorded yet. The plot will update automatically.';
    svg.appendChild(evalSvg('text',{class:'eval-chart-empty',x:margin.left+plotWidth/2,y:margin.top+plotHeight/2,'text-anchor':'middle'},emptyMessage));
  }
  host.replaceChildren(svg);
}
function scheduleEvalTrajectory(){clearTimeout(evalTrajectoryResizeTimer);evalTrajectoryResizeTimer=setTimeout(drawEvalTrajectory,80);}
function updateProgressRail(){
  var panel=document.querySelector('.progress-panel');if(!panel)return;
  var cards=document.querySelectorAll('details.card');var total=cards.length;
  var current=total?1:0;var probe=Math.max(72,window.innerHeight*.24);
  for(var i=0;i<cards.length;i++){if(cards[i].getBoundingClientRect().top<=probe)current=i+1;else break;}
  var atEnd=(window.scrollY+window.innerHeight)>=document.documentElement.scrollHeight-4;
  var slot=atEnd&&total?total+1:current;
  var pct=total?Math.max(0,Math.min(100,((slot-1)/total)*100)):0;
  var cursor=document.getElementById('progress-current');if(cursor)cursor.style.top=pct+'%';
  var status=document.getElementById('progress-status');
  if(status){
    status.textContent=slot===total+1?'End · '+total+' requests':'Request #'+current+' of '+total+' · '+Math.round(pct)+'%';
  }
  var events=document.querySelectorAll('.progress-event');
  for(var j=0;j<events.length;j++){
    var eventSlot=parseInt(events[j].getAttribute('data-slot')||'0',10);
    events[j].classList.toggle('past',eventSlot>0&&eventSlot<=slot);
    events[j].classList.toggle('current',eventSlot===slot);
  }
}
var progressTick=false;
function scheduleProgressRail(){if(progressTick)return;progressTick=true;requestAnimationFrame(function(){progressTick=false;updateProgressRail();});}
window.addEventListener('scroll',scheduleProgressRail,{passive:true});
window.addEventListener('resize',function(){scheduleProgressRail();scheduleEvalTrajectory();});
document.addEventListener('toggle',scheduleProgressRail,true);
document.addEventListener('DOMContentLoaded',function(){updateProgressRail();drawEvalTrajectory();});
"""


class Renderer:
    def __init__(self, run: RunData) -> None:
        self.run = run
        self.first_id_for_key: dict[str, str] = {}
        self.dup_counter = 0

    # -- text helpers -----------------------------------------------------

    def truncated(self, text: str, limit: int = TRUNCATE_CHARS, css: str = "text") -> str:
        if len(text) <= limit:
            return f'<div class="{css}">{esc(text)}</div>'
        head, rest = text[:limit], text[limit:]
        more_label = f"… show all ({len(text):,} chars)"
        return (
            f'<div class="{css}"><span>{esc(head)}</span><span class="more" hidden>{esc(rest)}</span> '
            f'<button type="button" data-more="{esc(more_label)}" onclick="toggleMore(this)">{esc(more_label)}</button></div>'
        )

    def render_tool_call(self, call: ToolCall) -> str:
        if call.command:
            body = f'<span class="name">{esc(call.name)}</span> $ {esc(call.command)}'
            if call.extras:
                body += f' <span class="extras">[{esc(call.extras)}]</span>'
        else:
            args = call.arguments if len(call.arguments) <= 600 else call.arguments[:600] + "…"
            body = f'<span class="name">{esc(call.name)}</span>({esc(args)})'
        cid = f' <span class="extras">{esc(call.call_id[:18])}</span>' if call.call_id else ""
        return f'<div class="tc">{body}{cid}</div>'

    def render_response_block(self, block: ResponseBlock, position: int) -> str:
        labels = {
            "thinking": "Thinking",
            "text": "Assistant text",
            "tool_use": "Tool use",
            "tool_result": "Tool result",
            "unknown": "Response block",
        }
        label = labels.get(block.kind, block.kind.replace("_", " ").title())
        raw_type = (
            f'<span>{esc(block.raw_type)}</span>'
            if block.raw_type and block.raw_type != block.kind
            else ""
        )
        parts = [
            f'<div class="resp-block rb-{esc(block.kind)}">',
            '<div class="seqhead">',
            f'<span class="seqnum">{position}</span>',
            f'<span class="seqkind">{esc(label)}</span>',
            raw_type,
            "</div>",
        ]
        if block.kind == "thinking":
            parts.append(
                self.truncated(
                    block.text,
                    REASONING_TRUNCATE_CHARS,
                    "reasoning",
                )
            )
        elif block.kind == "text":
            parts.append(self.truncated(block.text))
        elif block.kind == "tool_use" and block.tool_call is not None:
            parts.append(self.render_tool_call(block.tool_call))
        else:
            parts.append(self.truncated(block.text, css="text"))
        parts.append("</div>")
        return "".join(parts)

    # -- messages ---------------------------------------------------------

    def render_message(self, message: Message, status: str | None, prev_same_position: Message | None) -> str:
        role_css = message.role if message.role in ("system", "developer", "user", "assistant", "tool") else "other"
        classes = ["msg", role_css]
        badges: list[str] = []
        is_rs = message.is_research_state
        if is_rs:
            classes.append("harness")
            badges.append('<span class="badge rs">HARNESS: research-state injection</span>')
            stale = message.research_state_stale()
            if stale is True:
                badges.append('<span class="badge stale">STALE</span>')
        if message.item_type == "instructions":
            badges.append('<span class="badge info">instructions</span>')
        elif message.item_type == "tools":
            badges.append('<span class="badge info">tool definitions</span>')
        elif message.item_type == "reasoning":
            badges.append('<span class="badge info">reasoning item</span>')
        if status == "changed":
            classes.append("flag-changed")
            if message.role in ("system", "developer"):
                badges.append('<span class="badge changed">system message CHANGED vs previous request</span>')
            else:
                badges.append('<span class="badge changed">CHANGED vs previous request</span>')
        elif status == "tail-replaced":
            badges.append('<span class="badge tail">new (replaces previous trailing message)</span>')
        elif status == "new":
            badges.append('<span class="badge new">new</span>')
        if prev_same_position is not None and status == "changed" and prev_same_position.role != message.role:
            badges.append(f'<span class="badge info">was: {esc(prev_same_position.role)}</span>')

        # Assign a DOM id for lazy full-context cloning.
        if message.key in self.first_id_for_key:
            self.dup_counter += 1
            dom_id = f"m-{message.key}-d{self.dup_counter}"
        else:
            dom_id = f"m-{message.key}"
            self.first_id_for_key[message.key] = dom_id

        parts = [f'<div class="msg {" ".join(classes[1:])}" id="{dom_id}">']
        parts.append('<div class="head">')
        parts.append(f'<span class="role">{esc(message.role)}</span>')
        if message.name:
            parts.append(f"<span>{esc(message.name)}</span>")
        if message.tool_call_id:
            parts.append(f"<span>↩ {esc(str(message.tool_call_id)[:18])}</span>")
        parts.append(f"<span>{len(message.text):,} chars</span>")
        parts.extend(badges)
        parts.append("</div>")
        if message.reasoning:
            parts.append('<div class="reasoning">')
            parts.append(self.truncated(message.reasoning, REASONING_TRUNCATE_CHARS))
            parts.append("</div>")
        if message.text:
            parts.append(self.truncated(message.text))
        for call in message.tool_calls:
            parts.append(self.render_tool_call(call))
        parts.append("</div>")
        return "".join(parts)

    # -- response ---------------------------------------------------------

    def render_response(self, view: RequestView) -> tuple[str, bool]:
        response = view.response
        parts = ['<div class="resp">']
        header = "<h4>Response"
        if view.response_timestamp:
            header += f" · {fmt_clock(view.response_timestamp)}"
        if response.source:
            header += f" · {esc(response.source)}"
        header += "</h4>"
        parts.append(header)
        no_tool_call = False
        if not response.available:
            parts.append('<div class="note">No response recorded in the gateway timeline.</div>')
            if view.reasoning_stream:
                parts.append("<h4>Reasoning (model.reasoning stream)</h4>")
                parts.append(f'<div class="reasoning">{self.truncated(view.reasoning_stream, REASONING_TRUNCATE_CHARS)}</div>')
            parts.append("</div>")
            return "".join(parts), no_tool_call
        if response.blocks:
            parts.append(f"<h4>Response sequence ({len(response.blocks)} blocks)</h4>")
            parts.append('<div class="resp-sequence">')
            for position, block in enumerate(response.blocks, 1):
                parts.append(self.render_response_block(block, position))
            parts.append("</div>")
        else:
            reasoning = response.reasoning or view.reasoning_stream
            if reasoning:
                parts.append("<h4>Reasoning</h4>")
                parts.append(f'<div class="reasoning">{self.truncated(reasoning, REASONING_TRUNCATE_CHARS)}</div>')
            if response.text:
                parts.append("<h4>Assistant text</h4>")
                parts.append(self.truncated(response.text))
            if response.tool_calls:
                parts.append(f"<h4>Tool calls ({len(response.tool_calls)})</h4>")
                for call in response.tool_calls:
                    parts.append(self.render_tool_call(call))
        if not response.tool_calls:
            no_tool_call = True
            parts.append('<div class="alert">NO TOOL CALL (turn ends)</div>')
        finish_bits = []
        if response.finish_reason:
            finish_bits.append(f"finish: <b>{esc(response.finish_reason)}</b>")
        if view.response_status and view.response_status != "success":
            finish_bits.append(f'<span class="badge err">gateway status {esc(view.response_status)}</span>')
        elif view.response_status:
            finish_bits.append(f"status {esc(view.response_status)}")
        if finish_bits:
            parts.append(f'<div class="note">{" · ".join(finish_bits)}</div>')
        parts.append("</div>")
        return "".join(parts), no_tool_call

    # -- card -------------------------------------------------------------

    def render_card(self, view: RequestView, previous: RequestView | None) -> str:
        baseline_note = None
        if previous is not None and not comparable(previous, view):
            baseline_note = (
                f"previous request used {previous.provider}/{previous.model} · {previous.operation}; "
                "this one is not cache-comparable, so all messages are shown as new."
            )
            previous = None
        delta = compute_delta(previous.messages if previous else None, view.messages)
        prev_messages = previous.messages if previous else []
        harness = view.harness
        dropped = harness.get("dropped_tools") if isinstance(harness, dict) else None
        replacements = harness.get("system_prompt_replacements") if isinstance(harness, dict) else None

        body: list[str] = []
        # Harness label.
        if harness:
            drop_list = ", ".join(str(t) for t in dropped) if isinstance(dropped, list) else "none"
            drop_count = len(dropped) if isinstance(dropped, list) else 0
            profile = harness.get("profile") or ""
            body.append(
                '<div class="alert soft"><span class="badge harness">HARNESS APPLIED</span> '
                f"dropped {drop_count} tool(s): {esc(drop_list)} · system prompt replacements: {esc(replacements if replacements is not None else 0)}"
                + (f" · profile {esc(profile)}" if profile else "")
                + "</div>"
            )
        if view.tool_names:
            names = ", ".join(view.tool_names)
            body.append(f'<div class="tools">tools sent: {len(view.tool_names)} — {esc(names)}</div>')
        else:
            body.append('<div class="tools">tools sent: 0</div>')

        if baseline_note:
            body.append(f'<div class="alert soft">{esc(baseline_note)}</div>')
        # Prefix break alert.
        if delta.prefix_break_at is not None:
            broken = view.messages[delta.prefix_break_at] if delta.prefix_break_at < len(view.messages) else None
            role = broken.role if broken else prev_messages[delta.prefix_break_at].role
            what = "research-state injection" if (broken and broken.is_research_state) else f"{role} message"
            later = len(prev_messages) - 1 - delta.prefix_break_at
            body.append(
                f'<div class="alert"><span class="badge break">PREFIX CHANGED (cache break)</span> '
                f"message #{delta.prefix_break_at + 1} ({esc(what)}) differs from the previous request; "
                f"{later} later message(s) that were already in context can no longer be cache hits.</div>"
            )
        if delta.dropped_tail:
            body.append(f'<div class="alert soft">{delta.dropped_tail} message(s) present in the previous request are gone (history trimmed or compacted).</div>')

        # Delta view.
        body.append('<div class="delta">')
        if previous is not None:
            note = f"{delta.unchanged_prefix} earlier message(s) unchanged" if delta.unchanged_prefix else "no unchanged prefix"
            shown = sum(1 for e in delta.entries if e.status != "same")
            body.append(
                f'<div class="note">{note} · {shown} new/changed shown '
                f'<button type="button" class="viewbtn" onclick="toggleFull(this)">show full context</button></div>'
            )
        else:
            body.append(
                f'<div class="note">first request · all {len(view.messages)} message(s) shown '
                f'<button type="button" class="viewbtn" onclick="toggleFull(this)">show full context</button></div>'
            )
        same_run: list[DeltaEntry] = []

        def flush_same() -> None:
            if not same_run:
                return
            roles = ", ".join(f"{e.message.role}" for e in same_run[:6]) + (" …" if len(same_run) > 6 else "")
            body.append(
                f'<div class="note stub">{len(same_run)} message(s) #{same_run[0].position + 1}–#{same_run[-1].position + 1} '
                f"identical in content to the previous request but re-sent after the change above (no longer cache hits): {esc(roles)}</div>"
            )
            same_run.clear()

        for entry in delta.entries:
            if entry.status == "same":
                same_run.append(entry)
                continue
            flush_same()
            prev_same = prev_messages[entry.position] if entry.position < len(prev_messages) else None
            body.append(self.render_message(entry.message, entry.status, prev_same))
        flush_same()
        body.append("</div>")
        body.append('<div class="fullctx"><div class="note">full context as sent (' + str(len(view.messages)) + " messages)</div></div>")

        response_html, no_tool_call = self.render_response(view)
        body.append(response_html)

        # Header.
        ratio = view.cache_ratio()
        acc = view.accounting
        classes = ["card"]
        if delta.prefix_break_at is not None:
            classes.append("break")
        if no_tool_call and view.response.available:
            classes.append("noTool")
        head_badges = []
        if delta.prefix_break_at is not None:
            head_badges.append('<span class="badge break">PREFIX CHANGED</span>')
        if no_tool_call and view.response.available:
            head_badges.append('<span class="badge notool">NO TOOL CALL</span>')
        if harness:
            drop_count = len(dropped) if isinstance(dropped, list) else 0
            head_badges.append(f'<span class="badge harness">harness −{drop_count} tools</span>')
        if any(m.is_research_state and m.research_state_stale() for m in view.messages):
            head_badges.append('<span class="badge stale">STALE</span>')
        if acc.get("status") and acc.get("status") != "success":
            head_badges.append(f'<span class="badge err">{esc(acc.get("status"))}</span>')

        full_ids = " ".join(self.first_id_for_key.get(m.key, f"m-{m.key}") for m in view.messages)
        summary = (
            f'<summary><span class="idx">#{view.index}</span>'
            f'<span class="kv">{fmt_clock(view.timestamp)}</span>'
            f'<span class="kv"><b>{esc(view.provider)}/{esc(view.model)}</b> · {esc(view.operation)}</span>'
            f'<span class="kv">msgs <b>{len(view.messages)}</b></span>'
            f'<span class="kv">dur <b>{fmt_ms(acc.get("duration_ms"))}</b></span>'
            f'<span class="kv">in <b>{fmt_int(acc.get("input_tokens"))}</b></span>'
            f'<span class="kv">cached <b>{fmt_int(acc.get("cached_input_tokens"))}</b> '
            f'<span class="{ratio_class(ratio)}">{fmt_ratio(ratio)}</span></span>'
            f'<span class="kv">reasoning <b>{fmt_int(acc.get("reasoning_tokens"))}</b></span>'
            f'<span class="kv">out <b>{fmt_int(acc.get("output_tokens"))}</b></span>'
            f'<span class="kv">usd <b>{fmt_usd(acc.get("usd") if acc.get("usd") is not None else acc.get("normalized_usd"))}</b></span>'
            + "".join(head_badges)
            + "</summary>"
        )
        return (
            f'<details class="{" ".join(classes)}" open id="req-{view.index}" data-full="{esc(full_ids)}" data-rid="{esc(view.request_id)}">'
            + summary
            + '<div class="body">'
            + "".join(body)
            + "</div></details>"
        )

    # -- markers ----------------------------------------------------------

    def render_marker(self, marker: Marker) -> str:
        detail = f' <span class="d">{esc(marker.detail)}</span>' if marker.detail else ""
        anchor = f' id="{esc(marker.anchor)}"' if marker.anchor else ""
        return (
            f'<div class="marker {esc(marker.css)}"{anchor}><span class="t">{fmt_clock(marker.timestamp)}</span>'
            f"<span>{esc(marker.label)}</span>{detail}</div>"
        )

    def render_progress_sidebar(self, markers: list[Marker]) -> str:
        total = len(self.run.requests)
        events = [
            marker
            for marker in markers
            if marker.kind in {"evaluation", "verifier", "kb"}
        ]
        events.sort(
            key=lambda marker: (
                marker.slot if marker.slot is not None else total + 2,
                marker.timestamp or datetime.min.replace(tzinfo=timezone.utc),
                marker.label,
            )
        )
        eval_count = sum(marker.kind == "evaluation" for marker in events)
        verifier_count = sum(marker.kind == "verifier" for marker in events)
        kb_count = sum(marker.kind == "kb" for marker in events)
        parts = [
            '<aside class="progress-sidebar" aria-label="Run progress">',
            '<section class="progress-panel">',
            "<h2>Run progress</h2>",
            '<div class="progress-status" id="progress-status" aria-live="polite">',
            f"Request #1 of {total} · 0%" if total else "No model requests",
            "</div>",
            '<div class="progress-summary">',
            f"<span><b>{eval_count}</b> evaluations</span>",
            f"<span><b>{verifier_count}</b> final verifier</span>",
            f"<span><b>{kb_count}</b> KB calls</span>",
            "</div>",
            '<div class="progress-map">',
            '<div class="progress-track">',
            '<div class="progress-axis"></div>',
            '<div class="progress-current" id="progress-current"></div>',
        ]
        if total:
            for marker in events:
                if marker.slot is None:
                    continue
                pct = max(
                    0.0,
                    min(100.0, ((marker.slot - 1) / total) * 100.0),
                )
                marker_class = (
                    "eval"
                    if marker.kind == "evaluation"
                    else "verifier"
                    if marker.kind == "verifier"
                    else "kb"
                )
                if marker.kind == "evaluation" and marker.css == "eval-bad":
                    marker_class += " bad"
                title = marker.label
                if marker.detail:
                    title += f" — {marker.detail}"
                parts.append(
                    f'<a class="progress-point {marker_class}" '
                    f'href="#{esc(marker.anchor)}" style="top:{pct:.3f}%" '
                    f'title="{esc(title)}" aria-label="{esc(title)}"></a>'
                )
        parts.extend(
            [
                "</div>",
                '<div class="progress-scale"><span class="start">start</span><span class="end">end</span></div>',
                "</div>",
                '<div class="progress-legend">',
                '<span><i class="eval-key"></i> evaluation</span>',
                '<span><i class="verifier-key"></i> final verifier</span>',
                '<span><i class="kb-key"></i> knowledge base</span>',
                "</div>",
                '<div class="progress-events" aria-label="Evaluation, verifier, and knowledge-base events">',
            ]
        )
        if not events:
            parts.append(
                '<div class="progress-empty">'
                "No evaluations, verifier result, or knowledge-base calls recorded yet."
                "</div>"
            )
        for marker in events:
            marker_class = (
                "eval"
                if marker.kind == "evaluation"
                else "verifier"
                if marker.kind == "verifier"
                else "kb"
            )
            glyph = (
                "EVAL"
                if marker.kind == "evaluation"
                else "FINAL"
                if marker.kind == "verifier"
                else "KB"
            )
            if marker.kind == "evaluation" and marker.css == "eval-bad":
                marker_class += " bad"
            slot = marker.slot or 0
            if marker.slot is None:
                position = "position unavailable"
            elif marker.slot <= 1:
                position = "before request #1"
            elif marker.slot > total:
                position = f"after request #{total}"
            else:
                position = f"after request #{marker.slot - 1}"
            detail = marker.detail
            if detail:
                detail = f"{position} · {detail}"
            else:
                detail = position
            parts.append(
                f'<a class="progress-event {marker_class}" '
                f'href="#{esc(marker.anchor)}" data-slot="{slot}">'
                f'<span class="glyph">{glyph}</span><span>'
                f"<strong>{esc(marker.label)}</strong>"
                f"<small>{esc(detail)}</small></span></a>"
            )
        parts.extend(["</div>", "</section>", "</aside>"])
        return "".join(parts)

    def render_evaluation_trajectory(
        self,
        markers: list[Marker],
        summary: dict[str, Any],
    ) -> str:
        data = evaluation_trajectory_data(self.run, markers, summary)
        points = data["points"]
        valid = [
            point
            for point in points
            if is_ok_status(point.get("status"))
            and isinstance(point.get("score"), (int, float))
            and point["score"] > 0
        ]
        invalid_count = len(points) - len(valid)
        unresolved_costs = sum(
            1
            for point in points
            if not isinstance(point.get("cumulative_usd"), (int, float))
            or isinstance(point.get("cumulative_usd"), bool)
        )
        knowledge_base = data["knowledge_base"]
        summary_parts = [
            f"{len(points)} evaluation{'s' if len(points) != 1 else ''}",
            f"{len(valid)} valid",
            f"{invalid_count} invalid",
            f"{len(knowledge_base)} KB call"
            f"{'s' if len(knowledge_base) != 1 else ''}",
        ]
        if unresolved_costs:
            summary_parts.append(
                f"{unresolved_costs} eval cost"
                f"{'s' if unresolved_costs != 1 else ''} unavailable"
            )
        if valid:
            best = (
                max(valid, key=lambda point: point["score"])
                if self.run.metric_direction == "maximize"
                else min(valid, key=lambda point: point["score"])
            )
            summary_parts.append(
                f"best {fmt_score(best['score'])} at "
                f"{fmt_usd(best['cumulative_usd'])}"
            )
        if data["verifier"] is not None:
            summary_parts.append(
                "final verifier "
                f"{fmt_score(data['verifier']['score'])}"
            )

        encoded = json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        ).replace("</", "<\\/")
        direction = (
            "higher is better"
            if self.run.metric_direction == "maximize"
            else "lower is better"
        )
        legend = [
            '<span><i class="valid"></i>valid evaluation</span>',
            '<span><i class="invalid"></i>invalid evaluation</span>',
            '<span><i class="kb"></i>knowledge-base activity</span>',
        ]
        if data["verifier"] is not None:
            legend.append(
                '<span><i class="final"></i>final verifier</span>'
            )
        return (
            '<div class="eval-trajectory-shell">'
            '<section class="eval-trajectory" aria-labelledby="eval-trajectory-title">'
            '<div class="eval-trajectory-head">'
            '<h2 id="eval-trajectory-title">Evaluation score and KB activity versus cumulative spend</h2>'
            f'<div class="eval-trajectory-summary">{" · ".join(esc(part) for part in summary_parts)}</div>'
            "</div>"
            '<div class="eval-trajectory-legend">'
            + "".join(legend)
            + f"<span>{esc(direction)} · log score axis</span>"
            "</div>"
            '<div id="eval-trajectory-chart" class="eval-trajectory-chart" '
            'aria-live="polite"></div>'
            f'<script type="application/json" id="eval-trajectory-data">{encoded}</script>'
            "</section></div>"
        )

    # -- whole document ---------------------------------------------------

    def render(self) -> str:
        run = self.run
        data = run.record.get("data") if isinstance(run.record.get("data"), dict) else {}
        summary = summarize_run(run)
        total_usd = summary["total_usd"]
        usd_seen = total_usd is not None
        total_in = summary["input_tokens"]
        overall_ratio = summary["cache_ratio"]
        valid_count = summary["evaluations_valid"]
        invalid_count = summary["evaluations_invalid"]
        best_evaluation = summary["best_evaluation_score"]
        final_verifier = summary["final_verifier_score"]
        started = parse_ts(summary["started_at"])
        finished = parse_ts(summary["finished_at"])
        duration = ""
        if started and finished:
            seconds = int((finished - started).total_seconds())
            duration = f"{seconds // 60}m{seconds % 60:02d}s"
        breaks = summary["prefix_breaks"]
        no_tool = summary["no_tool_call_turns"]
        deliveries_ok = summary["hook_deliveries_ok"]
        deliveries_bad = summary["hook_deliveries_failed"]

        markers = build_markers(run)
        for position, marker in enumerate(markers, 1):
            marker.anchor = f"event-{position}"
        slots, unplaced = place_markers(run, markers)

        out: list[str] = []
        out.append(
            "<!DOCTYPE html><html lang=\"en\"><head>"
            "<meta charset=\"utf-8\">"
            "<meta name=\"viewport\" "
            "content=\"width=device-width,initial-scale=1\">"
        )
        out.append(f"<title>Gateway transcript — {esc(run.run_id)}</title>")
        out.append(f"<style>{CSS}</style></head><body>")
        out.append('<header class="run">')
        out.append(f"<h1>Gateway transcript · {esc(run.run_id)}</h1>")
        status = summary["status"]
        error = data.get("error")
        stats = [
            f"<span>requests</span> <b>{len(run.requests)}</b>",
            f"<span>total usd</span> <b>{fmt_usd(total_usd) if usd_seen else '-'}</b>",
            f"<span>input tokens</span> <b>{fmt_int(total_in)}</b>",
            f'<span>overall cache ratio</span> <b class="{ratio_class(overall_ratio)}">{fmt_ratio(overall_ratio)}</b>',
            f"<span>evaluations</span> <b>{valid_count} valid / {invalid_count} invalid</b>",
            f"<span>best evaluation ({esc(run.metric_direction)})</span> <b>{fmt_score(best_evaluation)}</b>",
            f"<span>prefix breaks</span> <b>{breaks}</b>",
            f"<span>no-tool-call turns</span> <b>{no_tool}</b>",
            f"<span>run status</span> <b>{esc(status or 'unknown')}</b>",
            f"<span>started</span> <b>{fmt_dt(started)}</b>",
            f"<span>finished</span> <b>{fmt_dt(finished)}</b>" + (f" <span>({duration})</span>" if duration else ""),
        ]
        if final_verifier is not None:
            stats.insert(
                6,
                "<span>final verifier (authoritative)</span> "
                f"<b>{fmt_score(final_verifier)}</b>",
            )
        if run.delivery_events:
            stats.append(f"<span>hook deliveries</span> <b>{deliveries_ok} ok / {deliveries_bad} failed</b>")
        if run.requests:
            first = run.requests[0]
            stats.append(f"<span>provider</span> <b>{esc(first.provider)}/{esc(first.model)}</b> <span>{esc(first.operation)}</span>")
        out.append('<div class="stats">' + "".join(f"<div>{s}</div>" for s in stats) + "</div>")
        if summary["cybersecurity_blocked"]:
            out.append(
                f'<div class="security">terminal reason: '
                f'{esc(summary["cybersecurity_stop_reason"])}</div>'
            )
        elif summary["budget_exhausted"]:
            out.append(
                f'<div class="term">terminal reason: '
                f'{esc(summary["budget_exhausted_reason"])}</div>'
            )
        elif error:
            out.append(f'<div class="err">error: {esc(error)}</div>')
        out.append("</header>")
        out.append(
            '<div class="controls"><span>View:</span>'
            '<button type="button" onclick="allFull(false)">delta only (all)</button>'
            '<button type="button" onclick="allFull(true)">full context (all)</button>'
            '<button type="button" onclick="allOpen(true)">expand all</button>'
            '<button type="button" onclick="allOpen(false)">collapse all</button>'
            '<span style="color:#6b7280">Cache ratio: <span class="ratio-red">&lt;50%</span> · '
            '<span class="ratio-amber">50–80%</span> · <span class="ratio-green">&gt;80%</span>. '
            "Dashed amber = harness-injected content.</span></div>"
        )
        out.append(self.render_evaluation_trajectory(markers, summary))
        out.append('<div class="page-shell"><main>')
        for warning in run.warnings:
            out.append(f'<div class="warn">{esc(warning)}</div>')
        if unplaced:
            out.append('<div class="rail"><h3>Events without a position in the request order</h3>')
            out.extend(self.render_marker(m) for m in unplaced)
            out.append("</div>")
        if not run.requests:
            out.append('<div class="warn">No model.request entries found.</div>')
        previous = None
        for view in run.requests:
            for marker in slots.get(view.index, []):
                out.append(self.render_marker(marker))
            out.append(self.render_card(view, previous))
            previous = view
        for marker in slots.get(len(run.requests) + 1, []):
            out.append(self.render_marker(marker))
        out.append("</main>")
        out.append(self.render_progress_sidebar(markers))
        out.append("</div>")
        out.append(f"<script>{JS}</script></body></html>")
        return "".join(out)


def budget_exhaustion_reason(events: list[dict[str, Any]]) -> str | None:
    for event in reversed(events):
        if event.get("event") != "budget_rejected":
            continue
        reason = str(event.get("reason") or "")
        lowered = reason.lower()
        if "budget" in lowered and "exhaust" in lowered:
            return reason or "configured budget exhausted"
    return None


def summarize_run(run: RunData) -> dict[str, Any]:
    """Machine-readable summary of a loaded run (used by the HTML header and the live server)."""
    data = run.record.get("data") if isinstance(run.record.get("data"), dict) else {}
    raw_status = data.get("status")
    exhausted_reason = budget_exhaustion_reason(run.gateway_events)
    security_reason = run.cybersecurity_stop_reason
    display_status = (
        CYBERSECURITY_STATUS
        if security_reason
        else "budget exhausted"
        if exhausted_reason
        else raw_status
    )
    total_usd = 0.0
    usd_seen = False
    total_in = 0
    total_cached = 0
    for view in run.requests:
        usd = view.accounting.get("usd")
        if usd is None:
            usd = view.accounting.get("normalized_usd")
        if isinstance(usd, (int, float)) and not isinstance(usd, bool):
            total_usd += float(usd)
            usd_seen = True
        if isinstance(view.accounting.get("input_tokens"), (int, float)):
            total_in += int(view.accounting["input_tokens"])
        if isinstance(view.accounting.get("cached_input_tokens"), (int, float)):
            total_cached += int(view.accounting["cached_input_tokens"])
    valid = [e for e in run.evals if is_ok_status(e.get("status"))]
    invalid = [e for e in run.evals if not is_ok_status(e.get("status"))]
    scores = [float(e["score"]) for e in valid if isinstance(e.get("score"), (int, float))]
    best = None
    if scores:
        best = min(scores) if run.metric_direction == "minimize" else max(scores)
    breaks = 0
    no_tool = 0
    previous: RequestView | None = None
    for view in run.requests:
        if previous is not None and not comparable(previous, view):
            previous = None
        delta = compute_delta(previous.messages if previous else None, view.messages)
        if delta.prefix_break_at is not None:
            breaks += 1
        if view.response.available and not view.response.tool_calls:
            no_tool += 1
        previous = view
    started = parse_ts(data.get("started_at")) or (run.requests[0].timestamp if run.requests else None)
    finished = parse_ts(data.get("finished_at")) or (run.requests[-1].response_timestamp if run.requests else None)
    last_request = run.requests[-1].timestamp if run.requests else None
    return {
        "run_id": run.run_id,
        "run_dir": str(run.run_dir),
        "status": display_status,
        "raw_status": raw_status,
        "error": data.get("error"),
        "cybersecurity_blocked": security_reason is not None,
        "cybersecurity_stop_reason": security_reason,
        "budget_exhausted": exhausted_reason is not None,
        "budget_exhausted_reason": exhausted_reason,
        "started_at": started.isoformat() if started else None,
        "finished_at": finished.isoformat() if finished else None,
        "last_request_at": last_request.isoformat() if last_request else None,
        "requests": len(run.requests),
        "total_usd": total_usd if usd_seen else None,
        "input_tokens": total_in,
        "cached_input_tokens": total_cached,
        "cache_ratio": (total_cached / total_in) if total_in else None,
        "evaluations": len(run.evals),
        "evaluations_valid": len(valid),
        "evaluations_invalid": len(invalid),
        "best_score": best,
        "best_evaluation_score": best,
        "final_verifier_score": run.verifier_score,
        "result_score": (
            run.verifier_score
            if run.verifier_score is not None
            else best
        ),
        "score_source": (
            "final verifier"
            if run.verifier_score is not None
            else "best evaluation"
            if best is not None
            else None
        ),
        "metric_direction": run.metric_direction,
        "prefix_breaks": breaks,
        "no_tool_call_turns": no_tool,
        "hook_deliveries_ok": sum(1 for e in run.delivery_events if e.get("status") == "success"),
        "hook_deliveries_failed": sum(1 for e in run.delivery_events if e.get("status") and e.get("status") != "success"),
        "provider": run.requests[0].provider if run.requests else None,
        "model": run.requests[0].model if run.requests else None,
    }


def render_run(run_dir: Path) -> str:
    """Load a run directory and return the complete HTML document."""
    run = load_run(run_dir)
    return Renderer(run).render()


def render_run_with_summary(run_dir: Path) -> tuple[str, dict[str, Any]]:
    """Load once; return (html, summary). Used by the live server."""
    run = load_run(run_dir)
    return Renderer(run).render(), summarize_run(run)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "run_dir",
        type=Path,
        help="run directory containing usage/events.jsonl (legacy logs also supported)",
    )
    parser.add_argument("-o", "--output", type=Path, default=None, help="output HTML path (default: <run>/transcript.html)")
    args = parser.parse_args(argv)
    run_dir: Path = args.run_dir
    if not run_dir.is_dir():
        print(f"error: {run_dir} is not a directory", file=sys.stderr)
        return 2
    output = args.output or (run_dir / "transcript.html")
    html_text = render_run(run_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_text, encoding="utf-8")
    print(f"wrote {output} ({len(html_text.encode('utf-8')):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
