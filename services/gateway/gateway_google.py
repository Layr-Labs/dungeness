"""Text/function-call translation for the Gemini and Vertex APIs.

No login, refresh, account discovery, CLI subprocess or provider-side tools.
Destinations and authentication are supplied by the trusted route registry.
"""
from __future__ import annotations

import json
import math
import re
from urllib.parse import quote

import httpx

from gateway_security import MAX_RESPONSE_BYTES, ResponseLimitExceeded


def require(ok, message="Unsupported Google protocol structure"):
    if not ok:
        raise ValueError(message)


def obj(value, keys):
    require(isinstance(value, dict) and not set(value) - set(keys))
    return value


def text(value):
    require(isinstance(value, str))
    return value


def validate_parts(parts):
    """Only model text/thoughts and locally executed function calls are history."""
    require(isinstance(parts, list) and bool(parts))
    for part in parts:
        obj(part, {"text", "thought", "thoughtSignature", "functionCall"})
        require(("text" in part) != ("functionCall" in part))
        if "text" in part:
            text(part["text"])
        if "thought" in part:
            require(type(part["thought"]) is bool and "text" in part)
        if "thoughtSignature" in part:
            require(bool(text(part["thoughtSignature"])))
        if "functionCall" in part:
            call = obj(part["functionCall"], {"id", "name", "args"})
            require(bool(text(call.get("name"))) and isinstance(call.get("args"), dict))
            if "id" in call:
                require(bool(text(call["id"])))


def normalize_usage(raw):
    """Google candidates exclude thoughts; our output count includes both.

    Counters are cumulative snapshots, not stream deltas. Missing/inconsistent
    receipts stay unknown. Cached tokens are a subset of prompt tokens.
    """
    if not isinstance(raw, dict) or not {"promptTokenCount", "totalTokenCount"} <= set(raw):
        return {}
    keys = ("promptTokenCount", "candidatesTokenCount", "thoughtsTokenCount",
            "cachedContentTokenCount", "totalTokenCount", "toolUsePromptTokenCount")
    values = [raw.get(key, 0) for key in keys]
    if any(type(value) is not int or not 0 <= value <= 2**53 - 1 for value in values):
        return {}
    prompt, answer, thoughts, cached, total, server_tools = values
    if cached > prompt or total != prompt + answer + thoughts or server_tools:
        return {}
    return {"input_tokens": prompt, "cached_input_tokens": cached,
            "cache_write_input_tokens": 0, "output_tokens": answer + thoughts,
            "reasoning_tokens": thoughts, "total_tokens": total}


def chat_usage(usage):
    return {"prompt_tokens": usage["input_tokens"], "completion_tokens": usage["output_tokens"],
            "total_tokens": usage["total_tokens"],
            "prompt_tokens_details": {"cached_tokens": usage["cached_input_tokens"]},
            "completion_tokens_details": {"reasoning_tokens": usage["reasoning_tokens"]}}


def message_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    require(isinstance(content, list))
    chunks = []
    for block in content:
        obj(block, {"type", "text"})
        require(block.get("type") == "text")
        chunks.append(text(block.get("text")))
    return "".join(chunks)


def call_data(call):
    obj(call, {"id", "type", "function", "extra_content", "index"})
    require(call.get("type") == "function" and bool(text(call.get("id"))))
    function = obj(call.get("function"), {"name", "arguments"})
    name = text(function.get("name"))
    try:
        args = json.loads(text(function.get("arguments")))
    except (ValueError, TypeError, RecursionError):
        raise ValueError("Function arguments must be a JSON object") from None
    require(bool(name) and isinstance(args, dict))
    return name, args


def request_body(payload):
    """Reject unmapped options before admission rather than silently dropping them."""
    obj(payload, {"model", "messages", "tools", "tool_choice", "stream", "stream_options",
                  "max_tokens", "max_completion_tokens", "temperature", "top_p", "stop", "n",
                  "seed", "response_format", "reasoning_effort", "extra_body",
                  "parallel_tool_calls"})
    require(type(payload.get("stream", False)) is bool)
    require(type(payload.get("n", 1)) is int and payload.get("n", 1) == 1)
    require(payload.get("parallel_tool_calls", True) is True,
            "Google translation cannot enforce serial tool calls")
    if "stream_options" in payload:
        obj(payload["stream_options"], {"include_usage"})
    generation = {}
    for source, destination in (("temperature", "temperature"), ("top_p", "topP"), ("seed", "seed"),
                                ("max_tokens", "maxOutputTokens"), ("max_completion_tokens", "maxOutputTokens")):
        if source in payload:
            require(destination not in generation, "Use a single output-token limit")
            value = payload[source]
            require(type(value) in (int, float) and (type(value) is int or math.isfinite(value)))
            if source in ("seed", "max_tokens", "max_completion_tokens"):
                require(type(value) is int)
            if source in ("max_tokens", "max_completion_tokens"):
                require(1 <= value <= 2**31 - 1)
            generation[destination] = payload[source]
    if "stop" in payload:
        stops = payload["stop"]
        generation["stopSequences"] = [stops] if isinstance(stops, str) else stops
        require(isinstance(generation["stopSequences"], list)
                and all(isinstance(stop, str) for stop in generation["stopSequences"]))
    thinking = {}
    config = payload.get("extra_body", {}).get("google", {}).get("thinking_config", {})
    for source, destination in (("thinking_level", "thinkingLevel"), ("thinking_budget", "thinkingBudget"),
                                ("include_thoughts", "includeThoughts")):
        if source in config:
            thinking[destination] = config[source].upper() if source == "thinking_level" else config[source]
    effort = payload.get("reasoning_effort")
    if effort is not None:
        require(isinstance(effort, str) and effort in {"none", "minimal", "low", "medium", "high", "xhigh"})
        thinking.update({"thinkingBudget": 0} if effort == "none" else {"thinkingLevel": effort.upper()})
    if thinking:
        generation["thinkingConfig"] = thinking
    if "response_format" in payload:
        form = obj(payload["response_format"], {"type", "json_schema"})
        if form.get("type") == "json_object":
            generation["responseMimeType"] = "application/json"
        elif form.get("type") == "json_schema":
            schema = obj(form.get("json_schema"), {"name", "description", "schema", "strict"})
            require(isinstance(schema.get("schema"), dict))
            generation.update(responseMimeType="application/json", responseJsonSchema=schema["schema"])
        else:
            require(form == {"type": "text"})

    body, system, contents, calls = {}, [], [], {}
    for message in payload["messages"]:
        obj(message, {"role", "content", "tool_calls", "tool_call_id", "name",
                      "reasoning_content", "extra_content"})
        role = message["role"]
        require(role == "tool" or "name" not in message)
        content = message_text(message.get("content"))
        if role in ("system", "developer"):
            require(not contents and not set(message) - {"role", "content"},
                    "System instructions must precede conversation history")
            system.append({"text": content})
            continue
        if role == "tool":
            require(not set(message) - {"role", "content", "tool_call_id", "name"})
            key = message.get("tool_call_id")
            require(isinstance(key, str) and key in calls, "Tool result has no matching local call")
            name, native_id = calls.pop(key)
            require(message.get("name", name) == name)
            response = {"name": name, "response": {"output": content}}
            if native_id is not None:
                response["id"] = native_id
            parts = [{"functionResponse": response}]
            native_role = "user"
        else:
            require(role in ("user", "assistant"))
            extra = message.get("extra_content", {}).get("google", {})
            tool_calls = message.get("tool_calls", [])
            require(isinstance(tool_calls, list))
            if "parts" in extra:
                # Our translated response carries exact native parts so multiple
                # signatures and signed thought/text boundaries survive replay.
                parts = extra["parts"]
                validate_parts(parts)
                visible = "".join(p["text"] for p in parts if "text" in p and not p.get("thought"))
                thoughts = "".join(p["text"] for p in parts if p.get("thought"))
                native_calls = [p["functionCall"] for p in parts if "functionCall" in p]
                require(visible == content and thoughts == message.get("reasoning_content", "")
                        and len(native_calls) == len(tool_calls), "Google history was altered; retain complete assistant messages")
                for call, native in zip(tool_calls, native_calls):
                    name, args = call_data(call)
                    require(name == native["name"] and args == native["args"], "Google tool history does not match native parts")
                    require(call["id"] not in calls, "Duplicate pending tool-call ID")
                    calls[call["id"]] = (name, native.get("id"))
            else:
                parts = []
                if message.get("reasoning_content"):
                    parts.append({"text": text(message["reasoning_content"]), "thought": True})
                if content or not tool_calls:
                    parts.append({"text": content})
                if "thought_signature" in extra:
                    require(bool(parts))
                    parts[-1]["thoughtSignature"] = extra["thought_signature"]
                for call in tool_calls:
                    name, args = call_data(call)
                    require(call["id"] not in calls, "Duplicate pending tool-call ID")
                    native = {"id": call["id"], "name": name, "args": args}
                    part = {"functionCall": native}
                    sig = call.get("extra_content", {}).get("google", {}).get("thought_signature")
                    if sig is not None:
                        part["thoughtSignature"] = sig
                    parts.append(part)
                    calls[call["id"]] = (name, call["id"])
            require(role == "assistant" or not set(message) - {"role", "content"})
            native_role = "model" if role == "assistant" else "user"
        if contents and contents[-1]["role"] == native_role:
            contents[-1]["parts"].extend(parts)
        else:
            contents.append({"role": native_role, "parts": list(parts)})
    require(bool(contents))
    body["contents"] = contents
    if system:
        body["systemInstruction"] = {"parts": system}
    if generation:
        body["generationConfig"] = generation
    declarations = []
    for tool in payload.get("tools", []):
        obj(tool, {"type", "function"})
        require(tool.get("type") == "function", "Google translation supports local function tools")
        function = obj(tool.get("function"), {"name", "description", "parameters", "strict"})
        declaration = {"name": text(function.get("name"))}
        if "description" in function:
            declaration["description"] = text(function["description"])
        if "parameters" in function:
            require(isinstance(function["parameters"], dict))
            declaration["parametersJsonSchema"] = function["parameters"]
        require(function.get("strict") in (None, False), "Google translation cannot enforce strict function schemas")
        declarations.append(declaration)
    if declarations:
        body["tools"] = [{"functionDeclarations": declarations}]
    choice = payload.get("tool_choice", "auto")
    if isinstance(choice, str):
        require(choice in ("auto", "none", "required"))
        calling = {"mode": {"auto": "AUTO", "none": "NONE", "required": "ANY"}[choice]}
    else:
        obj(choice, {"type", "function"})
        require(choice.get("type") == "function")
        function = obj(choice.get("function"), {"name"})
        name = text(function.get("name"))
        require(name in {item["name"] for item in declarations})
        calling = {"mode": "ANY", "allowedFunctionNames": [name]}
    if declarations or "tool_choice" in payload:
        body["toolConfig"] = {"functionCallingConfig": calling}
    return body


def upstream_request(config, payload, model, request_id, headers=None):
    require(isinstance(model, str) and re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", model),
            "Use a direct Google model ID")
    body = request_body(payload)
    method = "streamGenerateContent" if payload.get("stream") else "generateContent"
    base = config["upstream_default"].rstrip("/")
    if "project_header" in config:
        project = (headers or {}).get(config["project_header"])
        require(isinstance(project, str) and re.fullmatch(r"(?:[a-z][a-z0-9-]{4,28}[a-z0-9]|[0-9]{1,20})", project),
                "Vertex project ID is missing or invalid")
        base += f"/projects/{project}/locations/global/publishers/google"
    url = f"{base}/models/{quote(model, safe='')}:{method}"
    return url, {"alt": "sse"} if payload.get("stream") else {}, body


def protocol_error():
    return httpx.RemoteProtocolError("Invalid or unsupported Google response")


class ResponseTranslator:
    def __init__(self, model, request_id):
        self.model, self.request_id = model, request_id
        self.call_index = 0
        self.finish_reason = None
        self.usage = {}
        self.usage_high_water = 0
        self.parts = []

    def consume(self, value):
        try:
            require(isinstance(value, dict))
            require(isinstance(value, dict) and "error" not in value)
            # Accounting is not a signal that provider-side tool execution is allowed.
            require(not value.get("automaticFunctionCallingHistory"))
            candidates = value.get("candidates", [])
            require(isinstance(candidates, list) and len(candidates) <= 1)
            delta = {"role": "assistant"}
            if candidates:
                candidate = candidates[0]
                require(isinstance(candidate, dict) and candidate.get("index", 0) == 0)
                require(not candidate.get("groundingMetadata") and not candidate.get("urlContextMetadata"))
                content = candidate.get("content", {})
                require(isinstance(content, dict) and content.get("role", "model") == "model")
                parts = content.get("parts", [])
                if parts:
                    validate_parts(parts)
                    require(self.finish_reason is None, "Content after completion")
                    # A receipt preceding more output cannot account for it.
                    self.usage = {}
                    self.parts.extend(parts)
                    delta["extra_content"] = {"google": {"parts": parts}}
                    for part in parts:
                        if "text" in part:
                            key = "reasoning_content" if part.get("thought") else "content"
                            delta[key] = delta.get(key, "") + part["text"]
                        if "functionCall" in part:
                            native = part["functionCall"]
                            call = {"index": self.call_index, "id": native.get("id", f"call_{self.request_id}_{self.call_index}"),
                                    "type": "function", "function": {
                                        "name": native["name"], "arguments": json.dumps(native["args"], separators=(",", ":"))}}
                            if "thoughtSignature" in part:
                                call["extra_content"] = {"google": {"thought_signature": part["thoughtSignature"]}}
                            delta.setdefault("tool_calls", []).append(call)
                            self.call_index += 1
                if candidate.get("finishReason"):
                    reason = candidate["finishReason"]
                    require(reason in {"STOP", "MAX_TOKENS", "SAFETY", "RECITATION", "BLOCKLIST",
                                       "PROHIBITED_CONTENT", "SPII"})
                    self.finish_reason = ("tool_calls" if self.call_index else "stop") if reason == "STOP" else (
                        "length" if reason == "MAX_TOKENS" else "content_filter")
            elif value.get("promptFeedback", {}).get("blockReason"):
                self.finish_reason = "content_filter"
            if "usageMetadata" in value:
                self.usage = normalize_usage(value["usageMetadata"])
                if self.usage:
                    if self.usage["total_tokens"] < self.usage_high_water:
                        self.usage = {}
                    else:
                        self.usage_high_water = self.usage["total_tokens"]
            return delta
        except (ValueError, TypeError, KeyError, AttributeError):
            self.usage = {}
            raise protocol_error() from None

    def chunk(self, choices, **extra):
        return {"id": "chatcmpl-" + self.request_id, "object": "chat.completion.chunk",
                "created": 0, "model": self.model, "choices": choices, **extra}

    def finish(self):
        if self.finish_reason is None:
            raise protocol_error()
        return self.chunk([{"index": 0, "delta": {}, "finish_reason": self.finish_reason}],
                          **({"usage": chat_usage(self.usage)} if self.usage else {}))


class GoogleResponse:
    """Adapt a streamed HTTP response while retaining the gateway's one-request lifecycle."""
    def __init__(self, source, payload, request_id):
        self.source = source
        self.streaming = payload.get("stream", False)
        self.headers = httpx.Headers({"content-type": "text/event-stream" if self.streaming else "application/json"})
        self.status_code, self.is_success = source.status_code, source.is_success
        self.translator = ResponseTranslator(payload["model"], request_id)

    async def aclose(self):
        await self.source.aclose()

    async def documents(self):
        pending, size = bytearray(), 0
        sse = "text/event-stream" in self.source.headers.get("content-type", "")
        async for chunk in self.source.aiter_bytes():
            size += len(chunk)
            if size > MAX_RESPONSE_BYTES:
                raise ResponseLimitExceeded()
            pending.extend(chunk)
            if sse:
                while match := re.search(rb"\r?\n\r?\n", pending):
                    frame = bytes(pending[:match.start()])
                    del pending[:match.end()]
                    lines = [line.partition(b":")[2].removeprefix(b" ")
                             for line in frame.splitlines() if line.startswith(b"data:")]
                    if lines:
                        try:
                            yield json.loads(b"\n".join(lines))
                        except (ValueError, UnicodeError, RecursionError):
                            raise protocol_error() from None
        if sse:
            if pending.strip():
                raise protocol_error()  # A truncated event is not a final usage receipt.
        else:
            try:
                yield json.loads(pending)
            except (ValueError, UnicodeError, RecursionError):
                raise protocol_error() from None

    async def aiter_bytes(self):
        def encode(value):
            return ("data: " + json.dumps(value, ensure_ascii=False) + "\n\n").encode()
        deltas = []
        async for document in self.documents():
            delta = self.translator.consume(document)
            if self.streaming:
                yield encode(self.translator.chunk([{"index": 0, "delta": delta}]))
            else:
                deltas.append(delta)
        final = self.translator.finish()
        if self.streaming:
            yield encode(final)
            yield b"data: [DONE]\n\n"
        else:
            message = {"role": "assistant", "content": ""}
            for delta in deltas:
                for key in ("content", "reasoning_content"):
                    if key in delta:
                        message[key] = message.get(key, "") + delta[key]
                for call in delta.get("tool_calls", []):
                    message.setdefault("tool_calls", []).append({key: value for key, value in call.items() if key != "index"})
            if self.translator.parts:
                message["extra_content"] = {"google": {"parts": self.translator.parts}}
            yield json.dumps({**final, "object": "chat.completion", "choices": [
                {"index": 0, "message": message, "finish_reason": self.translator.finish_reason}
            ]}, ensure_ascii=False).encode()
