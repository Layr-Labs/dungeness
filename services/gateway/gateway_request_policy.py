"""Trusted, harness-independent policy for inference-only provider requests.

These are intentionally reviewed subsets of the provider APIs, not passthrough
schemas. Unknown control fields fail closed. Prompt text, tool arguments and
JSON schemas are data: their vocabulary is not a search-policy signal.
"""
from __future__ import annotations

from typing import Any


# Increment when the supported history contract changes. Kept in safe rejection
# diagnostics; the exact gateway revision is recorded in the runtime manifest.
HISTORY_SCHEMA_VERSION = 1
MAX_MODEL_REQUEST_BYTES = 8 * 1024 * 1024


class HistoryPolicyError(ValueError):
    """Safe diagnostics: fixed labels and positions, never history or arbitrary keys."""

    def __init__(self, reason: str, message: str, index: int | None = None, *, field=None, field_index=None, location="input"):
        super().__init__(message)
        self.diagnostic = {"code": "conversation_history_rejected", "reason": reason,
                           "location": location, "history_schema_version": HISTORY_SCHEMA_VERSION}
        if index is not None:
            self.diagnostic.update(item_index=index, item_type="reasoning")
        if field is not None:
            self.diagnostic["field"] = field
        if field_index is not None:
            self.diagnostic["field_index"] = field_index


def reasoning_history(item: dict, provider: str, index: int) -> None:
    """Validate a reviewed history envelope without treating it as request controls.

    OpenRouter adds format/signature to the standard Responses reasoning item.
    Do not accept these fields at the request root or on tool definitions. Unknown
    fields remain explicit errors, rather than silently dropping evidence. Format
    is bounded, inert metadata, not a capability or a model-routing selector.
    """
    allowed = {"type", "id", "status", "summary", "content", "encrypted_content"}
    if provider == "openrouter":
        allowed |= {"format", "signature"}
    for position, key in enumerate(sorted(item)):
        if key not in allowed:
            raise HistoryPolicyError("unsupported_history_field",
                "Unsupported reasoning history field; check the gateway's history compatibility schema.",
                index, field_index=position)

    def invalid(field):
        return HistoryPolicyError("invalid_history_field",
            "Invalid reasoning history field type or structure.", index, field=field)

    for name in ("id", "encrypted_content", "signature"):
        if item.get(name) is not None and not isinstance(item[name], str):
            raise invalid(name)
    status = item.get("status")
    if status is not None and (not isinstance(status, str)
                              or status not in {"in_progress", "incomplete", "completed"}):
        raise invalid("status")
    format_name = item.get("format")
    if format_name is not None and (not isinstance(format_name, str) or not 1 <= len(format_name) <= 128):
        raise invalid("format")
    for name, kind in (("summary", "summary_text"), ("content", "reasoning_text")):
        value = item.get(name)
        if value is None:
            continue
        if not isinstance(value, list):
            raise invalid(name)
        for block in value:
            if (not isinstance(block, dict) or set(block) != {"type", "text"}
                    or block.get("type") != kind or not isinstance(block.get("text"), str)):
                raise invalid(name)


def chat_reasoning_history(value: Any, provider: str, index: int) -> None:
    """OpenRouter Chat Completions uses reasoning_details, not Responses items."""
    if value is None:
        return
    def invalid(field=None):
        return HistoryPolicyError("invalid_history_field",
            "Invalid Chat Completions reasoning history.", index, field=field, location="messages")
    if provider != "openrouter" or not isinstance(value, list):
        raise invalid()
    for item in value:
        if not isinstance(item, dict):
            raise invalid()
        kind = item.get("type")
        shapes = {"reasoning.text": {"text", "signature"},
                  "reasoning.summary": {"summary"}, "reasoning.encrypted": {"data"}}
        if not isinstance(kind, str) or kind not in shapes:
            raise invalid()
        if set(item) - ({"type", "id", "format", "index"} | shapes[kind]):
            raise invalid()
        for key in ({"id", "format"} | shapes[kind]):
            if item.get(key) is not None and not isinstance(item[key], str):
                raise invalid(key if key in {"id", "format", "signature", "summary"} else None)
        if item.get("format") is not None and not 1 <= len(item["format"]) <= 128:
            raise invalid("format")
        if item.get("index") is not None and (type(item["index"]) is not int or item["index"] < 0):
            raise invalid()


RESPONSES_FIELDS = frozenset("""
model input instructions tools tool_choice parallel_tool_calls stream
stream_options max_output_tokens temperature top_p reasoning text truncation
store metadata include user safety_identifier prompt_cache_key
prompt_cache_retention service_tier background previous_response_id conversation
max_tool_calls top_logprobs
""".split())
CHAT_FIELDS = frozenset("""
model messages tools tool_choice functions function_call parallel_tool_calls
stream stream_options max_tokens max_completion_tokens temperature top_p n stop
logprobs top_logprobs logit_bias presence_penalty frequency_penalty seed user
response_format reasoning_effort service_tier metadata store modalities
""".split())
MESSAGES_FIELDS = frozenset("""
model messages max_tokens system tools tool_choice thinking output_config
output_format stop_sequences temperature top_p top_k metadata stream service_tier
cache_control context_management
""".split())
COMPLETIONS_FIELDS = frozenset("""
model prompt best_of echo frequency_penalty logit_bias logprobs max_tokens n
presence_penalty seed stop stream suffix temperature top_p user
""".split())
OPENROUTER_FIELDS = frozenset("""
reasoning provider top_k min_p top_a repetition_penalty cache_control session_id
""".split())
LOCAL_BUILTINS = {
    "local_shell", "shell", "apply_patch",
    "bash_20250124", "text_editor_20250124", "text_editor_20250429",
    "text_editor_20250728", "memory_20250818",
}
# Opt-in protocol features are also request controls. A new beta must be
# reviewed here rather than gaining upstream capabilities through a header.
SUPPORTED_BETAS = {
    "openai-beta": {"responses=experimental"},
    "anthropic-beta": {
        "prompt-caching-2024-07-31", "token-counting-2024-11-01",
        "output-128k-2025-02-19", "interleaved-thinking-2025-05-14",
        "fine-grained-tool-streaming-2025-05-14", "context-1m-2025-08-07",
        "context-management-2025-06-27", "structured-outputs-2025-11-13",
        "effort-2025-11-24", "oauth-2025-04-20", "claude-code-20250219",
    },
}


def fields(value: Any, allowed: set[str] | frozenset[str], where: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be an object")
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"unsupported {where} fields: {', '.join(sorted(unknown))}")
    return value


def sequence(value: Any, where: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{where} must be a list")
    return value


def cache_control(value: Any) -> None:
    if value is None:
        return
    obj = fields(value, {"type", "ttl"}, "cache_control")
    if obj.get("type") != "ephemeral" or obj.get("ttl") not in (None, "5m", "1h"):
        raise ValueError("unsupported cache_control")


def local_tools(items: Any, depth: int = 0) -> None:
    if depth > 16:
        raise ValueError("tool namespaces are too deeply nested")
    for tool in sequence(items, "tools"):
        if not isinstance(tool, dict):
            raise ValueError("tool must be an object")
        kind = tool.get("type", "custom" if "input_schema" in tool else "function")
        if not isinstance(kind, str):
            raise ValueError("tool type must be a string")
        if kind == "namespace":
            fields(tool, {"type", "name", "description", "tools"}, "namespace tool")
            local_tools(tool.get("tools", []), depth + 1)
            continue
        common = {"type", "name", "description", "cache_control", "strict",
                  "defer_loading", "allowed_callers", "input_examples"}
        if kind == "function" and "function" in tool:
            fields(tool, {"type", "function", "cache_control"}, "function tool")
            fields(tool["function"], {"name", "description", "parameters", "strict"}, "function")
        elif kind == "function":
            fields(tool, common | {"parameters"}, "function tool")
        elif kind == "custom" and "input_schema" in tool:
            fields(tool, common | {"input_schema", "eager_input_streaming"}, "client tool")
        elif kind == "custom":
            fields(tool, {"type", "name", "description", "format", "defer_loading"}, "custom tool")
            if tool.get("format") is not None:
                fmt = fields(tool["format"], {"type", "syntax", "definition"}, "custom format")
                if fmt.get("type") not in ("text", "grammar"):
                    raise ValueError("unsupported custom tool format")
        elif kind == "shell":
            fields(tool, {"type", "environment"}, "shell tool")
            # Omission can select a provider-hosted container. Require local.
            if tool.get("environment") != {"type": "local"}:
                raise ValueError("shell tools require an explicit local environment")
        elif kind == "tool_search":
            fields(tool, {"type", "execution", "description", "parameters"}, "tool discovery")
            if tool.get("execution") != "client":
                raise ValueError("tool discovery must be executed by the harness")
        elif kind in LOCAL_BUILTINS:
            fields(tool, common | {"max_characters"}, "local tool")
        else:
            raise ValueError("only harness-executed tools are permitted")
        if tool.get("allowed_callers", ["direct"]) != ["direct"]:
            raise ValueError("tools must be executed directly by the harness")
        cache_control(tool.get("cache_control"))


def tool_choice(value: Any, depth: int = 0) -> None:
    if depth > 16:
        raise ValueError("tool choice is too deeply nested")
    if value is None or isinstance(value, str) and value in {"none", "auto", "required", "any"}:
        return
    obj = fields(value, {"type", "name", "namespace", "function", "mode", "tools",
                         "disable_parallel_tool_use"}, "tool_choice")
    kind = obj.get("type")
    if kind == "allowed_tools":
        fields(obj, {"type", "mode", "tools"}, "allowed_tools choice")
        if obj.get("mode") not in ("auto", "required"):
            raise ValueError("unsupported allowed_tools mode")
        for choice in sequence(obj.get("tools"), "allowed_tools"):
            tool_choice(choice, depth + 1)
    elif kind in ("function", "custom", "tool"):
        fields(obj, {"type", "name", "namespace", "function", "disable_parallel_tool_use"}, "local tool choice")
        if "function" in obj:
            fields(obj["function"], {"name"}, "chosen function")
    elif isinstance(kind, str) and kind in LOCAL_BUILTINS | {"auto", "any", "none"}:
        fields(obj, {"type", "disable_parallel_tool_use"}, "local tool choice")
    else:
        raise ValueError("only harness-executed tool choices are permitted")


def text_format(value: Any) -> None:
    obj = fields(value, {"type", "name", "description", "schema", "strict", "json_schema"}, "text format")
    if obj.get("type") not in ("text", "json_object", "json_schema"):
        raise ValueError("unsupported text format")
    if "json_schema" in obj:
        fields(obj["json_schema"], {"name", "description", "schema", "strict"}, "json_schema format")


def content_blocks(value: Any, depth: int = 0) -> None:
    """Validate protocol envelopes, leaving local tool inputs/results opaque."""
    if depth > 32:
        raise ValueError("message content is too deeply nested")
    if isinstance(value, str) or value is None:
        return
    for block in sequence(value, "message content"):
        if isinstance(block, str):
            continue
        if not isinstance(block, dict):
            raise ValueError("content block must be an object")
        kind = block.get("type")
        if kind in ("text", "input_text", "output_text"):
            fields(block, {"type", "text", "cache_control", "annotations", "logprobs", "citations"}, "text block")
            # Anthropic-compatible responses can include empty citation metadata.
            # Round-tripping it does not request a server tool or remote resource.
            if "citations" in block and block["citations"] not in (None, []):
                raise ValueError("only empty citation metadata is supported")
        elif kind in ("thinking", "redacted_thinking", "reasoning"):
            fields(block, {"type", "thinking", "signature", "data", "text"}, "thinking block")
        elif kind == "tool_use":
            fields(block, {"type", "id", "name", "input", "cache_control", "caller"}, "local tool call")
            if block.get("caller", {"type": "direct"}) != {"type": "direct"}:
                raise ValueError("only directly executed local tool history is permitted")
        elif kind == "tool_result":
            fields(block, {"type", "tool_use_id", "content", "is_error", "cache_control"}, "local tool result")
            content_blocks(block.get("content"), depth + 1)
        elif kind == "refusal":
            fields(block, {"type", "refusal"}, "refusal")
        else:
            # Includes server_tool_use, MCP/tool-search outputs and remote
            # image/document URLs. Add a reviewed inline-media schema if needed.
            raise ValueError("unsupported content block; remote content and server tools are disabled")
        cache_control(block.get("cache_control"))


def messages(value: Any, provider: str = "openai", operation: str = "messages") -> None:
    for index, message in enumerate(sequence(value, "messages")):
        obj = fields(message, {"role", "content", "name", "tool_calls", "tool_call_id",
                               "function_call", "reasoning_content", "reasoning",
                               "reasoning_details", "cache_control", "refusal"}, "message")
        if obj.get("role") not in ("system", "developer", "user", "assistant", "tool", "function"):
            raise ValueError("unsupported message role")
        content_blocks(obj.get("content"))
        if obj.get("reasoning_details") is not None:
            if operation != "chat/completions":
                raise ValueError("reasoning_details requires Chat Completions")
            chat_reasoning_history(obj["reasoning_details"], provider, index)
        if "tool_calls" in obj:
            for call in sequence(obj["tool_calls"], "tool_calls"):
                fields(call, {"id", "type", "function", "index"}, "tool call")
                if call.get("type") != "function":
                    raise ValueError("only local function call history is permitted")
                fields(call.get("function"), {"name", "arguments"}, "function call")
        if obj.get("function_call") is not None:
            fields(obj["function_call"], {"name", "arguments"}, "function call")
        cache_control(obj.get("cache_control"))


def response_input(value: Any, provider: str = "openai") -> None:
    if isinstance(value, str) or value is None:
        return
    history_fields = {
        "compaction": {"encrypted_content"},
        "function_call": {"name", "namespace", "arguments", "call_id"},
        "function_call_output": {"call_id", "output"},
        "custom_tool_call": {"name", "namespace", "input", "call_id"},
        "custom_tool_call_output": {"call_id", "output"},
        "local_shell_call": {"call_id", "action"},
        "local_shell_call_output": {"call_id", "output"},
        "shell_call": {"call_id", "action", "environment"},
        "shell_call_output": {"call_id", "output", "max_output_length"},
        "apply_patch_call": {"call_id", "operation"},
        "apply_patch_call_output": {"call_id", "output"},
    }
    for index, item in enumerate(sequence(value, "input")):
        if not isinstance(item, dict):
            raise ValueError("input item must be an object")
        kind = item.get("type", "message")
        if kind == "reasoning":
            reasoning_history(item, provider, index)
        elif kind == "message":
            fields(item, {"type", "id", "role", "content", "status", "phase"}, "input message")
            if item.get("role") not in ("system", "developer", "user", "assistant"):
                raise ValueError("unsupported input message role")
            content_blocks(item.get("content"))
        elif kind in ("tool_search_call", "tool_search_output"):
            fields(item, {"type", "id", "call_id", "status", "execution",
                          "arguments" if kind == "tool_search_call" else "tools"}, "tool discovery history")
            if item.get("execution") != "client":
                raise ValueError("only harness-executed tool discovery history is permitted")
            if kind == "tool_search_output":
                local_tools(item.get("tools", []))
        elif isinstance(kind, str) and kind in history_fields:
            fields(item, {"type", "id", "status"} | history_fields[kind], "input item")
            if kind == "shell_call" and item.get("environment") not in (None, {"type": "local"}):
                raise ValueError("only local shell history is permitted")
            if kind == "shell_call_output" and isinstance(item.get("output"), list):
                for output in item["output"]:
                    fields(output, {"stdout", "stderr", "outcome"}, "shell output")
                    outcome = fields(output.get("outcome"), {"type", "exit_code"}, "shell outcome")
                    if outcome.get("type") not in ("exit", "timeout"):
                        raise ValueError("unsupported shell outcome")
            elif kind.endswith("_output") and isinstance(item.get("output"), list):
                content_blocks(item["output"])
        else:
            raise ValueError("unsupported input item; provider-side references and tools are disabled")


def text_or_tokens(value: Any) -> None:
    """Embedding/completion inputs are text or token IDs, never URL envelopes."""
    def tokens(item: Any) -> bool:
        return isinstance(item, list) and all(type(token) is int for token in item)
    if isinstance(value, str) or tokens(value):
        return
    if isinstance(value, list) and all(isinstance(item, str) or tokens(item) for item in value):
        return
    raise ValueError("input must contain text or token IDs")


def validate_model_request(provider: str, operation: str, payload: Any) -> None:
    """All model routes call this before accounting, translation or forwarding."""
    if operation == "responses":
        allowed = RESPONSES_FIELDS
    elif operation == "responses/compact":
        allowed = frozenset({"model", "input", "instructions"})
    elif operation == "chat/completions":
        allowed = CHAT_FIELDS
    elif operation in ("messages", "messages/count_tokens"):
        allowed = MESSAGES_FIELDS
    elif operation == "completions":
        allowed = COMPLETIONS_FIELDS
    elif operation == "embeddings":
        allowed = frozenset({"model", "input", "encoding_format", "dimensions", "user"})
    else:
        raise ValueError("unsupported model operation")
    if provider == "openrouter":
        allowed |= OPENROUTER_FIELDS
    stack = [(payload, 0)]
    while stack:
        value, depth = stack.pop()
        if depth > 64:
            raise ValueError("model request exceeds maximum nesting depth")
        if isinstance(value, dict):
            stack.extend((entry, depth + 1) for entry in value.values())
        elif isinstance(value, list):
            stack.extend((entry, depth + 1) for entry in value)
    fields(payload, allowed, f"{operation} request")
    model = payload.get("model")
    if not isinstance(model, str) or not model:
        raise ValueError("model must be a nonempty string")
    if ":online" in model.lower() or "@" in model:
        raise ValueError("search-enabled model aliases and provider presets are disabled")
    if payload.get("previous_response_id") is not None or payload.get("conversation") is not None:
        raise ValueError("provider-side conversation references are disabled; send explicit local history")
    if payload.get("background") not in (None, False):
        raise ValueError("background inference is disabled")
    if payload.get("modalities", ["text"]) != ["text"]:
        raise ValueError("only text inference is supported by this request policy")
    for include in sequence(payload.get("include", []), "include"):
        if include not in ("reasoning.encrypted_content", "message.output_text.logprobs"):
            raise ValueError("unsupported response include")
    local_tools(payload.get("tools", []))
    tool_choice(payload.get("tool_choice"))
    if "functions" in payload:
        for function in sequence(payload["functions"], "functions"):
            fields(function, {"name", "description", "parameters", "strict"}, "function")
    choice = payload.get("function_call")
    if choice is not None and choice not in ("none", "auto"):
        fields(choice, {"name"}, "function_call")
    try:
        if "messages" in payload:
            messages(payload["messages"], provider, operation)
        if "system" in payload:
            content_blocks(payload["system"])
        if operation.startswith("responses"):
            response_input(payload.get("input"), provider)
    except HistoryPolicyError:
        raise
    except ValueError as error:
        # Do not echo arbitrary field names/values from untrusted history.
        raise HistoryPolicyError("unsupported_history_structure",
            "Gateway rejected conversation history; check the supported provider/API history schema.",
            location="input" if operation.startswith("responses") else "messages") from error
    if operation == "embeddings":
        text_or_tokens(payload.get("input"))
    elif operation == "completions":
        text_or_tokens(payload.get("prompt"))
    for name, keys in {
        "reasoning": {"effort", "summary", "generate_summary", "max_tokens", "enabled", "exclude"},
        "thinking": {"type", "budget_tokens"},
        "stream_options": {"include_usage", "include_obfuscation"},
        "text": {"format", "verbosity"},
        "output_config": {"effort", "format"},
        "provider": {"order", "only", "ignore", "allow_fallbacks", "require_parameters",
                     "data_collection", "sort", "quantizations", "zdr", "max_price"},
    }.items():
        if payload.get(name) is not None:
            fields(payload[name], keys, name)
    routing = payload.get("provider") or {}
    if isinstance(routing.get("sort"), dict):
        fields(routing["sort"], {"by", "partition"}, "provider sort")
    if routing.get("max_price") is not None:
        fields(routing["max_price"], {"prompt", "completion", "request"}, "provider max_price")
    for parent in ("text", "output_config"):
        if (payload.get(parent) or {}).get("format") is not None:
            text_format(payload[parent]["format"])
    for name in ("response_format", "output_format"):
        if payload.get(name) is not None:
            text_format(payload[name])
    cache_control(payload.get("cache_control"))
    if payload.get("context_management") is not None:
        obj = fields(payload["context_management"], {"edits"}, "context_management")
        for edit in sequence(obj.get("edits", []), "context edits"):
            fields(edit, {"type", "trigger", "keep", "clear_at_least", "clear_tool_inputs",
                          "exclude_tools"}, "context edit")
            if edit.get("type") not in ("clear_tool_uses_20250919", "clear_thinking_20251015"):
                raise ValueError("unsupported context edit")


def validate_model_transport(operation: str, method: str, query: list[tuple[str, str]], body: bytes) -> None:
    if len(body) > MAX_MODEL_REQUEST_BYTES:
        raise ValueError("model request exceeds the 8 MiB gateway limit")
    if operation == "models":
        if method != "GET" or query or body:
            raise ValueError("model listing accepts only GET without a body or query")
        return
    if method != "POST":
        raise ValueError("model inference requires POST")
    # Anthropic SDK beta endpoints use this marker. No arbitrary query options
    # may be forwarded around the body schema, including duplicate parameters.
    if query and not (operation in ("messages", "messages/count_tokens") and query == [("beta", "true")]):
        raise ValueError("unsupported model query parameters")


def validate_model_headers(headers: Any) -> None:
    for name, supported in SUPPORTED_BETAS.items():
        for value in headers.getlist(name):
            if any(part.strip() not in supported for part in value.split(",")):
                raise ValueError(f"unsupported {name} feature")
    for value in headers.getlist("anthropic-version"):
        if value != "2023-06-01":
            raise ValueError("unsupported anthropic-version")
