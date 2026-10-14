# /// script
# requires-python = ">=3.11"
# dependencies = ["litellm==1.86.2"]
# ///
"""Estimate a run's model cost in USD from its captured token usage.

Reads ``usage/events.jsonl`` for new runs and the legacy
``usage/model-events.jsonl`` otherwise. New runs use the gateway-recorded
``normalized_usd`` value, which includes model-specific cache-write and
long-context tiers. Legacy events fall back to LiteLLM pricing.

Requests whose usage was never captured -- the agent disconnected before the
provider's final usage event, or the request errored -- are counted and reported
as an explicit error bar: the captured cost is a FLOOR, and the provider's usage
dashboard is ground truth. (The gateway now drains upstream on disconnect, so
this gap should be ~0 for runs made after that fix.)

Usage: uv run adapters/harbor/cost.py <run-id> [<run-id> ...]
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

import litellm

REPO = Path(__file__).resolve().parents[2]


def find_run_directory(run_id: str) -> Path | None:
    root = REPO / "runs"
    legacy = root / run_id
    matches = [legacy] if legacy.is_dir() else []
    for record_path in root.rglob("record.json"):
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data = record.get("data")
        recorded_id = (
            data.get("run_id")
            if isinstance(data, dict) and isinstance(data.get("run_id"), str)
            else record.get("id")
        )
        if recorded_id == run_id and record_path.parent not in matches:
            matches.append(record_path.parent)
    if len(matches) > 1:
        raise ValueError(f"run id is ambiguous across namespaces: {run_id}")
    return matches[0] if matches else None


def request_cost(event: dict) -> float | None:
    recorded = event.get("normalized_usd")
    if (
        isinstance(recorded, (int, float))
        and not isinstance(recorded, bool)
        and recorded >= 0
    ):
        return float(recorded)

    model = event.get("model") or "unknown"
    prompt = event.get("input_tokens", 0) or 0
    completion = event.get("output_tokens", 0) or 0
    cache_read = event.get("cached_input_tokens", 0) or 0
    for kwargs in (
        {},  # litellm knows our models by name
        {"custom_llm_provider": event.get("provider")},  # fallback: force provider
    ):
        try:
            prompt_cost, completion_cost = litellm.cost_per_token(
                model=model,
                prompt_tokens=prompt,
                completion_tokens=completion,
                cache_read_input_tokens=cache_read,
                **kwargs,
            )
            return prompt_cost + completion_cost
        except Exception:  # noqa: BLE001 - try the fallback, else give up (unpriced)
            continue
    return None


def report(run_id: str) -> dict | None:
    run_dir = find_run_directory(run_id)
    usage_dir = (
        run_dir / "usage"
        if run_dir is not None
        else REPO / "runs" / run_id / "usage"
    )
    canonical_path = usage_dir / "events.jsonl"
    legacy_path = usage_dir / "model-events.jsonl"
    if canonical_path.is_file():
        events = []
        with canonical_path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                if "model.accounting" not in line:
                    continue
                event = json.loads(line)
                if event.get("kind") != "model.accounting":
                    continue
                data = event.get("data")
                if isinstance(data, dict):
                    events.append(data)
        source_path = canonical_path
    else:
        events = []
        source_path = legacy_path
    if not events and legacy_path.is_file():
        with legacy_path.open(encoding="utf-8") as handle:
            events = [
                json.loads(line)
                for line in handle
                if line.strip()
            ]
        source_path = legacy_path
    if not events:
        print(f"{run_id}: no model accounting events")
        return None

    priced: list[float] = []
    unpriced = 0
    uncaptured = {"stream_interrupted": 0, "error": 0, "other": 0}
    for event in events:
        if (event.get("total_tokens", 0) or 0) > 0:
            cost = request_cost(event)
            if cost is None:
                unpriced += 1
            else:
                priced.append(cost)
        else:
            status = event.get("status")
            uncaptured[status if status in uncaptured else "other"] += 1

    captured = sum(priced)
    # Interrupted requests were billed but not captured; estimate their cost with
    # the median captured per-request cost as an explicit error bar.
    median = statistics.median(priced) if priced else 0.0
    missing = uncaptured["stream_interrupted"] + uncaptured["other"]
    est_missing = median * missing
    result = {
        "run_id": run_id,
        "requests": len(events),
        "priced_requests": len(priced),
        "captured_usd": round(captured, 4),
        "uncaptured_interrupted": missing,
        "uncaptured_error": uncaptured["error"],
        "estimated_uncaptured_usd": round(est_missing, 4),
        "estimate_low_usd": round(captured, 2),
        "estimate_high_usd": round(captured + est_missing, 2),
        "unpriced_requests": unpriced,
        "note": (
            "captured_usd is a FLOOR; interrupted requests were billed but their "
            "usage was not captured (errors are likely unbilled). Ground truth is "
            "the provider usage dashboard."
        ),
    }
    (source_path.parent / "cost.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )

    line = f"{run_id}: ${captured:.2f} captured ({len(priced)} priced reqs)"
    if missing:
        line += (
            f"  ± ~${est_missing:.2f} for {missing} uncaptured/interrupted"
            f" → ~${captured:.2f}–{captured + est_missing:.2f}"
        )
    if uncaptured["error"]:
        line += f"  [{uncaptured['error']} errored, ~unbilled]"
    if unpriced:
        line += f"  [{unpriced} unpriced: unknown model]"
    print(line)
    return result


def main() -> None:
    run_ids = sys.argv[1:]
    if not run_ids:
        print("usage: uv run adapters/harbor/cost.py <run-id> [<run-id> ...]")
        raise SystemExit(2)
    low = high = 0.0
    for run_id in run_ids:
        result = report(run_id)
        if result:
            low += result["estimate_low_usd"]
            high += result["estimate_high_usd"]
    if len(run_ids) > 1:
        print(f"TOTAL: ~${low:.2f}–{high:.2f}")


if __name__ == "__main__":
    main()
