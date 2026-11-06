"""Keep protocol completion behind accounting without buffering ordinary output."""

import json
import re


# Do not mistake the two bytes of one CRLF for an empty line. SSE also permits
# lone CR and LF line endings, including a delimiter split across reads.
_END_EVENT = re.compile(rb"(?:\r\n|\r(?!\n)|\n)(?:\r\n|\r(?!\n)|\n)")


def completes_response(frame: bytes, operation: str) -> bool:
    data, event = [], None
    for line in frame.splitlines():
        field, sep, value = line.partition(b":")
        if value.startswith(b" "):
            value = value[1:]
        if sep and field == b"data":
            data.append(value)
        elif sep and field == b"event":
            event = value
    payload = b"\n".join(data)
    if payload == b"[DONE]":
        return True
    terminal = ({b"response.completed", b"response.incomplete", b"response.failed", b"error"}
                if operation == "responses" else {b"message_stop", b"error"}
                if operation == "messages" else {b"error"})
    if event in terminal:
        return True
    try:
        document = json.loads(payload)
    except (ValueError, UnicodeError):
        return False
    if not isinstance(document, dict):
        return False
    kind = document.get("type")
    if isinstance(kind, str) and kind.encode() in terminal:
        return True
    if operation in {"chat/completions", "completions"}:
        choices = document.get("choices")
        return isinstance(choices, list) and any(
            isinstance(choice, dict) and choice.get("finish_reason") is not None
            for choice in choices)
    return False


class CompletionBarrier:
    """Relay exact SSE bytes until completion, then hold the suffix for settlement.

    The caller enforces the existing total response byte limit before feed().
    No history, signature or usage fields are rewritten. Holding the suffix also
    preserves usage events delivered after the terminal model-output event.
    """

    def __init__(self, operation: str):
        self.operation = operation
        self.pending = bytearray()
        self.completed = False
        self.scan_from = 0

    def feed(self, chunk: bytes, *, final: bool = False) -> bytes:
        self.pending.extend(chunk)
        if self.completed:
            return b""
        emitted = 0
        scan = self.scan_from
        while match := _END_EVENT.search(self.pending, scan):
            end = match.end()
            if not final and end == len(self.pending) and self.pending[-1] == 13:
                # A trailing CR may be the first byte of a fragmented CRLF.
                break
            if completes_response(bytes(self.pending[emitted:end]), self.operation):
                self.completed = True
                break
            emitted = end
            scan = end
        if final and not self.completed:
            if completes_response(bytes(self.pending[emitted:]), self.operation):
                self.completed = True
            else:
                emitted = len(self.pending)
        output = bytes(self.pending[:emitted])
        del self.pending[:emitted]
        self.scan_from = max(0, len(self.pending) - 3)
        return output

    def settled(self) -> bytes:
        output = bytes(self.pending)
        self.pending.clear()
        return output
