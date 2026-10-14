"""Codex Responses to Kimi Chat Completions protocol adapter."""

from __future__ import annotations

from collections import deque
from collections.abc import AsyncIterator, Callable
from typing import Any
import uuid

import litellm
from litellm.responses.litellm_completion_transformation.streaming_iterator import (
    LiteLLMCompletionStreamingIterator,
)
from litellm.responses.litellm_completion_transformation.transformation import (
    LiteLLMCompletionResponsesConfig,
)
from litellm.types.llms.openai import ResponsesAPIResponse
from litellm.types.utils import ModelResponse


TraceWriter = Callable[[dict[str, Any]], None]


def model_dump(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        dumped = value.model_dump(exclude_none=True)
        if isinstance(dumped, dict):
            return dumped
    if hasattr(value, "dict"):
        dumped = value.dict(exclude_none=True)
        if isinstance(dumped, dict):
            return dumped
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"cannot serialize adapter value: {type(value).__name__}")


def _reasoning_text(item: Any) -> str:
    if not isinstance(item, dict) or item.get("type") != "reasoning":
        return ""
    parts = item.get("summary") or item.get("content") or []
    if isinstance(parts, str):
        return parts
    if not isinstance(parts, list):
        return ""
    text: list[str] = []
    for part in parts:
        if isinstance(part, str):
            text.append(part)
        elif isinstance(part, dict) and isinstance(part.get("text"), str):
            text.append(part["text"])
    return "".join(text)


def _native_reasoning_item(
    item: Any,
    *,
    item_id: str | None = None,
    text: str | None = None,
) -> dict[str, Any] | None:
    if not isinstance(item, dict) or item.get("type") != "reasoning":
        return None
    reasoning_text = text if text is not None else _reasoning_text(item)
    native = {
        "id": item_id or str(item.get("id") or f"rs_{uuid.uuid4()}"),
        "type": "reasoning",
        "summary": [],
    }
    if reasoning_text:
        native["summary"] = [
            {
                "type": "summary_text",
                "text": reasoning_text,
            }
        ]
    encrypted_content = item.get("encrypted_content")
    if isinstance(encrypted_content, str) and encrypted_content:
        native["encrypted_content"] = encrypted_content
    return native


def _normalize_response_reasoning(
    response: dict[str, Any],
    *,
    item_id: str | None = None,
    text: str | None = None,
) -> dict[str, Any]:
    output = response.get("output")
    if not isinstance(output, list):
        return response

    normalized: list[Any] = []
    found_reasoning = False
    for item in output:
        native = _native_reasoning_item(
            item,
            item_id=item_id if not found_reasoning else None,
            text=text if not found_reasoning else None,
        )
        if native is None:
            normalized.append(item)
            continue
        found_reasoning = True
        normalized.append(native)
    if not found_reasoning and text:
        normalized.insert(
            0,
            _native_reasoning_item(
                {"type": "reasoning"},
                item_id=item_id,
                text=text,
            ),
        )
    response["output"] = normalized
    return response


def _restore_reasoning_history(
    raw_input: Any,
    messages: list[Any],
) -> None:
    """Attach returned Kimi reasoning to the following assistant tool call.

    Kimi requires the complete prior assistant message, including
    ``reasoning_content``, on tool-call continuations. LiteLLM intentionally
    drops Responses reasoning items while converting request history, so restore
    them onto the corresponding assistant tool-call messages here.
    """

    if not isinstance(raw_input, list):
        return
    reasoning_turns: list[str] = []
    pending_reasoning = ""
    in_tool_call_turn = False
    for item in raw_input:
        text = _reasoning_text(item)
        if text:
            pending_reasoning = text
            in_tool_call_turn = False
            continue
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "function_call" and not in_tool_call_turn:
            reasoning_turns.append(pending_reasoning)
            pending_reasoning = ""
            in_tool_call_turn = True
        elif item_type not in {"function_call", "function_call_output"}:
            # A message or other output closes a non-tool reasoning turn. It
            # must not be attached to a later, unrelated assistant tool call.
            pending_reasoning = ""
            in_tool_call_turn = False

    if not reasoning_turns:
        return
    tool_messages = [
        message
        for message in messages
        if isinstance(message, dict)
        and message.get("role") == "assistant"
        and message.get("tool_calls")
    ]
    for message, text in zip(tool_messages, reasoning_turns, strict=False):
        if text:
            message["reasoning_content"] = text


def _chat_content_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return ""
    parts: list[str] = []
    for part in value:
        if isinstance(part, str):
            parts.append(part)
        elif isinstance(part, dict):
            text = part.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "".join(parts)


def _normalize_kimi_messages(messages: list[Any]) -> None:
    """Make Responses-derived history valid Kimi Chat Completions history."""

    for message in messages:
        if isinstance(message, dict) and message.get("role") == "developer":
            message["role"] = "system"
            message["content"] = _chat_content_text(message.get("content"))

    index = 0
    while index < len(messages):
        message = messages[index]
        if (
            not isinstance(message, dict)
            or message.get("role") != "assistant"
            or not message.get("tool_calls")
        ):
            index += 1
            continue

        for tool_call in message["tool_calls"]:
            if isinstance(tool_call, dict):
                tool_call.pop("index", None)

        content = [_chat_content_text(message.get("content"))]
        following = index + 1
        while following < len(messages):
            next_message = messages[following]
            if (
                not isinstance(next_message, dict)
                or next_message.get("role") != "assistant"
                or next_message.get("tool_calls")
            ):
                break
            content.append(_chat_content_text(next_message.get("content")))
            messages.pop(following)

        combined = "\n".join(part for part in content if part)
        message["content"] = combined or None
        index += 1


def build_chat_request(payload: dict[str, Any]) -> dict[str, Any]:
    model = payload.get("model")
    if not isinstance(model, str) or not model:
        raise ValueError("Kimi request requires a model")
    raw_input = payload.get("input", "")
    optional = {
        key: value
        for key, value in payload.items()
        if key not in {"input", "model"}
    }
    request = (
        LiteLLMCompletionResponsesConfig
        .transform_responses_api_request_to_chat_completion_request(
            model=model,
            input=raw_input,
            responses_api_request=optional,
            custom_llm_provider="openai",
            stream=bool(payload.get("stream")),
        )
    )
    messages = request.get("messages")
    if isinstance(messages, list):
        _restore_reasoning_history(raw_input, messages)
        _normalize_kimi_messages(messages)

    # Codex exposes grouped capabilities as Responses API `namespace` tools.
    # Kimi's Chat Completions endpoint rejects that tool type, so retain the
    # ordinary function tools needed by the coding loop and omit namespaces.
    tools = request.get("tools")
    if isinstance(tools, list):
        request["tools"] = [
            tool
            for tool in tools
            if isinstance(tool, dict) and tool.get("type") == "function"
        ]
        if not request["tools"]:
            request.pop("tools")
            request.pop("tool_choice", None)
            request.pop("parallel_tool_calls", None)

    # Kimi K3 documents max_completion_tokens rather than max_tokens and fixes
    # the sampling parameters. Do not send defaults that the upstream rejects.
    max_tokens = request.pop("max_tokens", None)
    if max_tokens is not None:
        request["max_completion_tokens"] = max_tokens
    for fixed in ("temperature", "top_p", "frequency_penalty", "presence_penalty"):
        request.pop(fixed, None)
    return request


class RecordingStream:
    """Proxy a LiteLLM chat stream while recording decoded upstream chunks."""

    def __init__(self, stream: Any, trace: TraceWriter) -> None:
        self._stream = stream
        self._iterator = stream.__aiter__()
        self._trace = trace

    def __getattr__(self, name: str) -> Any:
        return getattr(self._stream, name)

    def __aiter__(self) -> "RecordingStream":
        return self

    async def __anext__(self) -> Any:
        chunk = await self._iterator.__anext__()
        try:
            self._trace(
                {
                    "stage": "upstream",
                    "protocol": "openai-chat-completions",
                    "event": model_dump(chunk),
                }
            )
        except (OSError, TypeError, ValueError):
            pass
        return chunk


class NativeReasoningStream:
    """Normalize LiteLLM's Kimi reasoning into native Responses items."""

    _INITIAL_EVENTS = {
        "response.created",
        "response.in_progress",
    }
    _REASONING_EVENTS = {
        "response.reasoning_summary_part.added",
        "response.reasoning_summary_part.done",
        "response.reasoning_summary_text.delta",
        "response.reasoning_summary_text.done",
    }

    def __init__(self, stream: AsyncIterator[Any]) -> None:
        self._iterator = stream.__aiter__()
        self._pending: deque[dict[str, Any]] = deque()
        self._buffered_output_setup: list[dict[str, Any]] = []
        self._reasoning_item_id: str | None = None
        self._reasoning_parts: list[str] = []
        self._reasoning_finished = False

    def __aiter__(self) -> "NativeReasoningStream":
        return self

    def _start_reasoning(self, preferred_id: Any = None) -> None:
        if self._reasoning_item_id is not None:
            return
        self._reasoning_item_id = (
            str(preferred_id)
            if isinstance(preferred_id, str) and preferred_id
            else f"rs_{uuid.uuid4()}"
        )
        self._pending.extend(
            [
                {
                    "type": "response.output_item.added",
                    "output_index": 0,
                    "item": {
                        "id": self._reasoning_item_id,
                        "type": "reasoning",
                        "summary": [],
                    },
                },
                {
                    "type": "response.reasoning_summary_part.added",
                    "item_id": self._reasoning_item_id,
                    "output_index": 0,
                    "summary_index": 0,
                    "part": {"type": "summary_text", "text": ""},
                },
            ]
        )

    def _finish_reasoning(self) -> None:
        if self._reasoning_item_id is None or self._reasoning_finished:
            return
        text = "".join(self._reasoning_parts)
        self._pending.extend(
            [
                {
                    "type": "response.reasoning_summary_text.done",
                    "item_id": self._reasoning_item_id,
                    "output_index": 0,
                    "summary_index": 0,
                    "text": text,
                },
                {
                    "type": "response.reasoning_summary_part.done",
                    "item_id": self._reasoning_item_id,
                    "output_index": 0,
                    "summary_index": 0,
                    "part": {"type": "summary_text", "text": text},
                },
                {
                    "type": "response.output_item.done",
                    "output_index": 0,
                    "item": {
                        "id": self._reasoning_item_id,
                        "type": "reasoning",
                        "summary": [
                            {
                                "type": "summary_text",
                                "text": text,
                            }
                        ],
                    },
                },
            ]
        )
        self._reasoning_finished = True

    def _shift_non_reasoning_output(self, event: dict[str, Any]) -> dict[str, Any]:
        if self._reasoning_item_id is None:
            return event
        output_index = event.get("output_index")
        if isinstance(output_index, int):
            event["output_index"] = output_index + 1
        return event

    def _flush_buffered_output_setup(self) -> None:
        for event in self._buffered_output_setup:
            self._pending.append(self._shift_non_reasoning_output(event))
        self._buffered_output_setup.clear()

    def _normalize_completed(self, event: dict[str, Any]) -> dict[str, Any]:
        response = event.get("response")
        if isinstance(response, dict):
            _normalize_response_reasoning(
                response,
                item_id=self._reasoning_item_id,
                text="".join(self._reasoning_parts) or None,
            )
        return event

    async def __anext__(self) -> dict[str, Any]:
        while True:
            if self._pending:
                return self._pending.popleft()

            try:
                event = model_dump(await self._iterator.__anext__())
            except StopAsyncIteration:
                self._finish_reasoning()
                self._flush_buffered_output_setup()
                if self._pending:
                    return self._pending.popleft()
                raise

            raw_event_type = event.get("type")
            event_type = str(
                getattr(raw_event_type, "value", raw_event_type) or ""
            )
            event["type"] = event_type
            item = event.get("item")
            item_type = item.get("type") if isinstance(item, dict) else None

            if event_type in self._INITIAL_EVENTS:
                return event

            if (
                event_type == "response.output_item.added"
                and item_type == "reasoning"
            ):
                self._start_reasoning(item.get("id"))
                continue

            if event_type == "response.reasoning_summary_text.delta":
                self._start_reasoning(event.get("item_id"))
                delta = event.get("delta")
                if isinstance(delta, str):
                    self._reasoning_parts.append(delta)
                self._pending.append(
                    {
                        **event,
                        "item_id": self._reasoning_item_id,
                        "output_index": 0,
                    }
                )
                continue

            if event_type in self._REASONING_EVENTS or (
                event_type == "response.output_item.done"
                and item_type == "reasoning"
            ):
                self._finish_reasoning()
                continue

            if (
                self._reasoning_item_id is None
                and event_type
                in {
                    "response.output_item.added",
                    "response.content_part.added",
                }
            ):
                self._buffered_output_setup.append(event)
                continue

            if event_type == "response.completed":
                self._finish_reasoning()
                self._flush_buffered_output_setup()
                self._pending.append(self._normalize_completed(event))
                continue

            if self._reasoning_item_id is not None:
                self._finish_reasoning()
            self._flush_buffered_output_setup()
            self._pending.append(self._shift_non_reasoning_output(event))


async def request_kimi(
    payload: dict[str, Any],
    *,
    api_base: str,
    api_key: str,
    trace: TraceWriter,
) -> ResponsesAPIResponse | AsyncIterator[Any]:
    chat_request = build_chat_request(payload)
    raw_input = payload.get("input", "")
    optional = {
        key: value
        for key, value in payload.items()
        if key not in {"input", "model"}
    }
    response = await litellm.acompletion(
        **chat_request,
        api_base=api_base,
        api_key=api_key,
        drop_params=True,
    )
    if isinstance(response, ModelResponse):
        trace(
            {
                "stage": "upstream",
                "protocol": "openai-chat-completions",
                "event": model_dump(response),
            }
        )
        transformed = (
            LiteLLMCompletionResponsesConfig
            .transform_chat_completion_response_to_responses_api_response(
                chat_completion_response=response,
                request_input=raw_input,
                responses_api_request=optional,
            )
        )
        normalized = _normalize_response_reasoning(model_dump(transformed))
        return ResponsesAPIResponse(**normalized)
    if isinstance(response, litellm.CustomStreamWrapper):
        recorded = RecordingStream(response, trace)
        return NativeReasoningStream(
            LiteLLMCompletionStreamingIterator(
                model=str(payload["model"]),
                litellm_custom_stream_wrapper=recorded,
                request_input=raw_input,
                responses_api_request=optional,
                custom_llm_provider="openai",
            )
        )
    raise TypeError(f"unexpected Kimi response: {type(response).__name__}")
