"""Native Gemini/Vertex policy and receipts. No conversation translation."""
from __future__ import annotations

import json
import math
import re
from urllib.parse import quote

import httpx
from gateway_security import MAX_RESPONSE_BYTES, ResponseLimitExceeded
from gateway_stream import _END_EVENT

OPERATIONS = {"generateContent", "streamGenerateContent"}
MODEL_ID = r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}"


def require(ok, message="Unsupported Google protocol structure"):
    if not ok:
        raise ValueError(message)


def obj(value, keys):
    require(isinstance(value, dict))
    # Protobuf JSON and Google's SDK use both lowerCamelCase and snake_case.
    # This view is only for validation; the original request is forwarded intact.
    names = {alias: key for key in keys for alias in (key, re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower())}
    require(not set(value) - names.keys())
    checked = {names[key]: entry for key, entry in value.items()}
    require(len(checked) == len(value), "Duplicate Google field aliases")
    return checked


def text(value):
    require(isinstance(value, str))
    return value


def parse_path(path):
    match = re.fullmatch(r"models/(" + MODEL_ID + r"):(generateContent|streamGenerateContent)", path)
    require(match is not None, "Use models/{model}:generateContent or :streamGenerateContent")
    return match.group(1), match.group(2)


def validate_parts(parts, *, responses=False):
    require(isinstance(parts, list) and bool(parts))
    for part in parts:
        part = obj(part, {"text", "thought", "thoughtSignature", "functionCall"} | ({"functionResponse"} if responses else set()))
        kinds = set(part) & {"text", "functionCall", "functionResponse"}
        require(len(kinds) == 1 or not kinds and bool(part.get("thoughtSignature")))
        if "text" in part:
            text(part["text"])
        if "thought" in part:
            require(type(part["thought"]) is bool)
        if "thoughtSignature" in part:
            require(bool(text(part["thoughtSignature"])))
        for kind, field in (("functionCall", "args"), ("functionResponse", "response")):
            if kind in part:
                call = obj(part[kind], {"id", "name", field})
                require(bool(text(call.get("name"))) and isinstance(call.get(field, {}), dict))
                if "id" in call:
                    require(bool(text(call["id"])))


def validate_request(payload):
    """Inspect native fields for policy; never reconstruct conversation history."""
    payload = obj(payload, {"contents", "systemInstruction", "tools", "toolConfig", "generationConfig", "safetySettings"})
    contents = payload.get("contents")
    require(isinstance(contents, list) and bool(contents))
    for content in contents:
        content = obj(content, {"role", "parts"})
        require(content.get("role", "user") in ("user", "model"))
        validate_parts(content.get("parts"), responses=True)
    if "systemInstruction" in payload:
        system = obj(payload["systemInstruction"], {"role", "parts"})
        require(isinstance(system.get("parts"), list) and bool(system["parts"]))
        for part in system["parts"]:
            obj(part, {"text"}); text(part.get("text"))
    tools = payload.get("tools", [])
    require(isinstance(tools, list))
    for tool in tools:
        tool = obj(tool, {"functionDeclarations"})
        declarations = tool.get("functionDeclarations")
        require(isinstance(declarations, list) and bool(declarations))
        for declaration in declarations:
            declaration = obj(declaration, {"name", "description", "parameters", "parametersJsonSchema", "response", "responseJsonSchema", "behavior"})
            require(bool(text(declaration.get("name"))))
            if "description" in declaration:
                text(declaration["description"])
            for field in ("parameters", "parametersJsonSchema", "response", "responseJsonSchema"):
                if field in declaration:
                    require(isinstance(declaration[field], dict))
            require(declaration.get("behavior", "BLOCKING") in ("BLOCKING", "NON_BLOCKING"))
    if "toolConfig" in payload:
        config = obj(payload["toolConfig"], {"functionCallingConfig"})
        calling = obj(config.get("functionCallingConfig", {}), {"mode", "allowedFunctionNames"})
        require(calling.get("mode", "AUTO") in ("AUTO", "ANY", "NONE", "VALIDATED"))
        if "allowedFunctionNames" in calling:
            require(isinstance(calling["allowedFunctionNames"], list)
                    and all(isinstance(v, str) and v for v in calling["allowedFunctionNames"]))
    config = obj(payload.get("generationConfig", {}), {
        "temperature", "topP", "topK", "candidateCount", "maxOutputTokens", "stopSequences",
        "presencePenalty", "frequencyPenalty", "seed", "responseMimeType", "responseSchema",
        "responseJsonSchema", "responseModalities", "thinkingConfig", "responseLogprobs", "logprobs"})
    require(type(config.get("candidateCount", 1)) is int and config.get("candidateCount", 1) == 1)
    require(config.get("responseModalities", ["TEXT"]) == ["TEXT"])
    for field in ("temperature", "topP", "presencePenalty", "frequencyPenalty"):
        if field in config:
            require(type(config[field]) in (int, float) and abs(config[field]) <= 1e6 and math.isfinite(config[field]))
    for field in ("topK", "maxOutputTokens", "seed", "logprobs"):
        if field in config:
            require(type(config[field]) is int and abs(config[field]) < 2**31)
    if "maxOutputTokens" in config:
        require(config["maxOutputTokens"] > 0)
    if "responseLogprobs" in config:
        require(type(config["responseLogprobs"]) is bool)
    if "stopSequences" in config:
        require(isinstance(config["stopSequences"], list) and all(isinstance(v, str) for v in config["stopSequences"]))
    require(config.get("responseMimeType", "text/plain") in ("text/plain", "application/json", "text/x.enum"))
    for field in ("responseSchema", "responseJsonSchema"):
        if field in config:
            require(isinstance(config[field], dict))
    if "thinkingConfig" in config:
        thinking = obj(config["thinkingConfig"], {"thinkingLevel", "thinkingBudget", "includeThoughts"})
        require(not {"thinkingLevel", "thinkingBudget"} <= set(thinking))
        if "thinkingLevel" in thinking:
            require(thinking["thinkingLevel"] in ("MINIMAL", "LOW", "MEDIUM", "HIGH", "XHIGH"))
        if "thinkingBudget" in thinking:
            require(type(thinking["thinkingBudget"]) is int and -1 <= thinking["thinkingBudget"] < 2**31)
        if "includeThoughts" in thinking:
            require(type(thinking["includeThoughts"]) is bool)
    settings = payload.get("safetySettings", [])
    require(isinstance(settings, list))
    for setting in settings:
        setting = obj(setting, {"category", "threshold", "method"})
        for value in setting.values(): text(value)


def upstream_request(config, operation, model, headers):
    require(operation in OPERATIONS and isinstance(model, str) and re.fullmatch(MODEL_ID, model),
            "Use a direct Google model ID")
    base = config["upstream_default"].rstrip("/")
    if "project_header" in config:
        project = headers.get(config["project_header"])
        require(isinstance(project, str) and re.fullmatch(r"(?:[a-z][a-z0-9-]{4,28}[a-z0-9]|[0-9]{1,20})", project),
                "Vertex project ID is missing or invalid")
        base += f"/projects/{project}/locations/global/publishers/google"
    return f"{base}/models/{quote(model, safe='')}:{operation}", ({"alt": "sse"} if operation == "streamGenerateContent" else {})


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



class NativeReceipt:
    """Track cumulative native receipts independently of the returned wire format."""
    def __init__(self):
        self.usage = {}
        self.high_water = 0
        self.complete = False

    def consume(self, value):
        require(isinstance(value, dict) and "error" not in value)
        require(not value.get("automaticFunctionCallingHistory"))
        candidates = value.get("candidates", [])
        require(isinstance(candidates, list) and len(candidates) <= 1)
        for candidate in candidates:
            require(isinstance(candidate, dict) and candidate.get("index", 0) == 0)
            require(not candidate.get("groundingMetadata") and not candidate.get("urlContextMetadata"))
            content = candidate.get("content", {})
            require(isinstance(content, dict) and content.get("role", "model") == "model")
            if content.get("parts"):
                validate_parts(content["parts"])
                require(not self.complete, "Content after completion")
                self.usage = {}  # Earlier receipt cannot cover later output.
            if candidate.get("finishReason"):
                require(isinstance(candidate["finishReason"], str))
                self.complete = True
        feedback = value.get("promptFeedback", {})
        require(isinstance(feedback, dict))
        if feedback.get("blockReason"):
            self.complete = True
        if "usageMetadata" in value:
            self.usage = normalize_usage(value["usageMetadata"])
            if self.usage:
                if self.usage["total_tokens"] < self.high_water:
                    self.usage = {}
                else:
                    self.high_water = self.usage["total_tokens"]


def event_document(frame):
    data = []
    for line in frame.splitlines():
        field, sep, value = line.partition(b":")
        if sep and field == b"data":
            data.append(value[1:] if value.startswith(b" ") else value)
    return json.loads(b"\n".join(data)) if data else None


def extract_usage(body, content_type):
    receipt = NativeReceipt()
    try:
        if "text/event-stream" in content_type:
            start = 0
            for match in _END_EVENT.finditer(body):
                value = event_document(body[start:match.end()])
                if value is not None: receipt.consume(value)
                start = match.end()
            # An unterminated event is not a complete provider receipt.
            if body[start:].strip(): return {}
        else:
            receipt.consume(json.loads(body))
    except (ValueError, TypeError, KeyError, RecursionError):
        return {}
    return receipt.usage if receipt.complete else {}


class NativeGoogleResponse:
    """Validate native responses, forwarding their exact JSON/SSE bytes.

    No generated IDs, event conversion, signature packing or usage rewriting.
    The ordinary gateway completion barrier and accounting lifecycle still apply.
    """
    def __init__(self, source):
        self.source = source
        self.status_code, self.headers = source.status_code, source.headers
        self.is_success = source.is_success

    async def aclose(self):
        await self.source.aclose()

    async def aiter_bytes(self):
        pending = bytearray()
        count = 0
        streaming = "text/event-stream" in self.headers.get("content-type", "")
        receipt = NativeReceipt()
        try:
            async for chunk in self.source.aiter_bytes():
                count += len(chunk)
                if count > MAX_RESPONSE_BYTES: raise ResponseLimitExceeded()
                pending.extend(chunk)
                if streaming:
                    while match := _END_EVENT.search(pending):
                        end = match.end()
                        if end == len(pending) and pending[-1] == 13: break
                        frame = bytes(pending[:end])
                        value = event_document(frame)
                        if value is not None: receipt.consume(value)
                        del pending[:end]
                        yield frame
            if streaming:
                if pending.strip():
                    # A final CR delimiter may have waited for a possible LF.
                    match = _END_EVENT.search(pending)
                    require(match is not None and match.end() == len(pending), "Incomplete Google stream")
                    value = event_document(bytes(pending))
                    if value is not None: receipt.consume(value)
                if pending: yield bytes(pending)
                require(receipt.complete, "Incomplete Google stream")
            else:
                receipt.consume(json.loads(pending))
                require(receipt.complete, "Incomplete Google response")
                yield bytes(pending)
        except (ValueError, TypeError, KeyError, RecursionError):
            raise httpx.RemoteProtocolError("Invalid or unsupported Google response") from None
