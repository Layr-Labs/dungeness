#!/usr/bin/env python3
"""Show run-scoped budgets and research-agent time remaining."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


def fetch_json(url: str) -> dict[str, object] | None:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            value = json.loads(response.read())
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def main() -> None:
    gateway = os.environ.get("TESTBED_GATEWAY_URL", "http://gateway:8080")
    document: dict[str, object] = {
        "gateway": fetch_json(gateway.rstrip("/") + "/status")
    }

    scorer = os.environ.get("DEV_SCORER_URL")
    if scorer:
        document["evaluation"] = fetch_json(scorer.rstrip("/") + "/status")


    deadline = os.environ.get("DUNGENESS_AGENT_DEADLINE_EPOCH")
    if deadline:
        try:
            seconds = max(0, int(float(deadline) - time.time()))
        except ValueError:
            seconds = None
    else:
        seconds = None
    document["agent_time"] = {
        "seconds_remaining": seconds,
        "configured_seconds": int(
            os.environ.get("DUNGENESS_AGENT_TIMEOUT_SEC", "0")
        )
        or None,
        "phase": "research-agent",
        "excludes": [
            "image-build",
            "service-startup",
            "final-verification",
        ],
    }
    print(json.dumps(document, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
