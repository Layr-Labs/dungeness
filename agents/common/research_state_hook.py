#!/usr/bin/env python3
"""Codex hook relay for the Dungeness research-state controller."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import PurePosixPath
import shlex
import sys
import time
import urllib.error
import urllib.request


def request_json(path: str, payload: dict[str, object] | None = None) -> dict:
    base = os.environ["DUNGENESS_RESEARCH_STATE_URL"].rstrip("/")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base + path,
        data=data,
        headers={"content-type": "application/json"},
        method="GET" if data is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        value = json.loads(response.read())
    if not isinstance(value, dict):
        raise ValueError("research-state response must be an object")
    return value


def knowledge_base_command_reason(hook_input: dict) -> str | None:
    """Reject KB invocations whose stdout may not reach model context."""

    if not os.environ.get("DUNGENESS_KNOWLEDGE_BASE_URL"):
        return None
    if hook_input.get("tool_name") != "Bash":
        return None
    tool_input = hook_input.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    if not isinstance(command, str):
        return None
    try:
        lexer = shlex.shlex(
            command,
            posix=True,
            punctuation_chars="|&;<>`$()",
        )
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        tokens = []
    kb_positions = [
        index
        for index, token in enumerate(tokens)
        if PurePosixPath(token).name == "knowledge-base"
    ]
    control_tokens = {
        token
        for token in tokens
        if token and set(token) <= set("|&;<>`$()")
    }
    invoked_positions = [
        index
        for index in kb_positions
        if index == 0
        or (
            index > 0
            and (
                tokens[index - 1] in control_tokens
                or tokens[index - 1] == "env"
                or all("=" in token for token in tokens[:index])
            )
        )
    ]
    wrapped_invocation = any(
        token.startswith(("knowledge-base ", "/usr/local/bin/knowledge-base "))
        for token in tokens
    )
    if not invoked_positions and not wrapped_invocation:
        return None
    if (
        "\n" in command
        or invoked_positions != [0]
        or wrapped_invocation
        or bool(control_tokens)
    ):
        return (
            "Run knowledge-base as one direct command so its output enters "
            "model context. Do not pipe, redirect, combine, wrap, or suppress it."
        )
    return None


def pre_tool_use(hook_input: dict) -> dict:
    reason = knowledge_base_command_reason(hook_input)
    if reason is None:
        return {}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def compact_context(view: dict) -> str:
    return (
        "## Current Dungeness research-effort state\n\n"
        "This state is maintained by Dungeness from authoritative gateway and "
        "evaluation observations. Use it when choosing whether to search, "
        "evaluate, or finalize. Distinct qualifying operations count; duplicate "
        "queries and unchanged candidates do not. Knowledge-base behavior "
        "feedback is driven only by qualifying inspiration lookups followed by "
        "real evaluator outcomes; it never changes the evaluator score.\n\n"
        "```json\n"
        + json.dumps(view, indent=2, sort_keys=True)
        + "\n```"
    )


def hook_context(event_name: str) -> dict:
    view = request_json("/model-view")
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": compact_context(view),
        }
    }


def completion_payload(hook_input: dict) -> dict[str, object]:
    stable = {
        "session_id": hook_input.get("session_id"),
        "turn_id": hook_input.get("turn_id"),
        "last_assistant_message": hook_input.get("last_assistant_message"),
    }
    attempt_id = hashlib.sha256(
        json.dumps(stable, sort_keys=True).encode("utf-8")
    ).hexdigest()
    deadline = os.environ.get("DUNGENESS_AGENT_DEADLINE_EPOCH")
    remaining = None
    if deadline:
        try:
            remaining = max(0, int(float(deadline) - time.time()))
        except ValueError:
            pass
    return {
        "attempt_id": attempt_id,
        "session_id": hook_input.get("session_id"),
        "turn_id": hook_input.get("turn_id"),
        "last_assistant_message": hook_input.get("last_assistant_message"),
        "time_remaining_sec": remaining,
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: research-state-hook EVENT")
    event = sys.argv[1]
    try:
        hook_input = json.load(sys.stdin)
        if not isinstance(hook_input, dict):
            raise ValueError("hook input must be an object")
        if event == "session-start":
            output = (
                hook_context("SessionStart")
                if os.environ.get("DUNGENESS_RESEARCH_STATE_URL")
                else {}
            )
        elif event == "pre-tool-use":
            output = pre_tool_use(hook_input)
        elif event == "stop":
            if os.environ.get("DUNGENESS_RESEARCH_STATE_URL"):
                decision = request_json(
                    "/completion-attempt", completion_payload(hook_input)
                )
                if decision.get("decision") == "block":
                    output = {
                        "decision": "block",
                        "reason": str(decision["reason"]),
                    }
                else:
                    output = {}
            else:
                output = {}
        else:
            raise ValueError(f"unknown hook event: {event}")
    except (
        KeyError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        urllib.error.URLError,
    ) as error:
        print(f"research-state hook failed open: {error}", file=sys.stderr)
        output = {}
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
