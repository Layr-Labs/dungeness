"""Read challenge-defined display metrics without interpreting their meaning."""
from __future__ import annotations

import math


# Older evaluators wrote metrics alongside this event metadata. New evaluators
# supply an explicit metrics mapping, which is authoritative even when empty.
EVENT_FIELDS = frozenset({
    "schema_version", "run_id", "sequence", "source", "kind", "event_id",
    "request_id", "observed_at", "recorded_at", "timestamp", "operation",
    "status", "score", "best_score", "candidate_sha256", "source_sha256",
    "submissions_used", "submissions_limit", "submissions_remaining",
    "duration_ms", "usage", "cumulative_usage", "error", "message", "metrics",
})


def evaluation_metrics(event: dict[str, object]) -> dict[str, int | float]:
    """Return finite numeric metrics; never treat strings or booleans as scores."""
    values = event.get("metrics") if "metrics" in event else {
        key: value for key, value in event.items() if key not in EVENT_FIELDS
    }
    if not isinstance(values, dict):
        return {}
    result = {}
    for name, value in values.items():
        if not isinstance(name, str) or not name or type(value) not in (int, float):
            continue
        try:
            if not math.isfinite(value):
                continue
        except OverflowError:
            continue
        result[name] = value
    return result
