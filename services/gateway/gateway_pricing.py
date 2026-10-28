"""Trusted model-pricing policy and per-request cost calculation."""

from __future__ import annotations

import os
import math
from pathlib import Path
from typing import Any

import yaml


PRICING_PATH = Path(
    os.environ.get("MODEL_PRICING_PATH")
    or Path(__file__).with_name("pricing.yaml")
)
PRICING_RATE_FIELDS = (
    "input_per_mtok",
    "cached_read_per_mtok",
    "output_per_mtok",
)
_CACHED_TOKEN_WEIGHT_OVERRIDE = os.environ.get("CACHED_TOKEN_WEIGHT")
CACHED_TOKEN_WEIGHT = float(_CACHED_TOKEN_WEIGHT_OVERRIDE or "0.1")


def validate_pricing_rates(
    rates: dict[str, Any],
    *,
    path: Path,
    context: str,
) -> None:
    for key in PRICING_RATE_FIELDS:
        value = rates.get(key)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(
                f"invalid model pricing field {context}.{key}: "
                f"{value!r} in {path}"
            )
    cache_write = rates.get("cache_write_per_mtok")
    if cache_write is not None and (
        not isinstance(cache_write, (int, float))
        or isinstance(cache_write, bool)
        or not math.isfinite(cache_write)
        or cache_write < 0
    ):
        raise ValueError(
            "invalid model pricing field "
            f"{context}.cache_write_per_mtok: {cache_write!r} in {path}"
        )
    hour = rates.get("cache_write_1h_per_mtok")
    if "cache_write_1h_per_mtok" in rates and (
        type(hour) not in (int, float) or not math.isfinite(hour) or hour < 0
    ):
        raise ValueError(f"invalid model pricing field {context}.cache_write_1h_per_mtok in {path}")


def load_model_pricing(path: Path = PRICING_PATH) -> list[dict[str, Any]]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if (
        not isinstance(document, dict)
        or document.get("schema_version") != 1
        or document.get("type") != "policy"
        or document.get("namespace") != "system/dungeness"
        or document.get("id") != "model-pricing"
    ):
        raise ValueError(f"invalid trusted model pricing policy: {path}")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"model pricing entries must be a list: {path}")
    validated: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f"model pricing entry must be a mapping: {path}")
        if not isinstance(entry.get("request_models"), list):
            raise ValueError(f"model pricing request_models must be a list: {path}")
        validate_pricing_rates(entry, path=path, context="base")
        long_context = entry.get("long_context")
        if long_context is not None:
            if not isinstance(long_context, dict):
                raise ValueError(
                    f"model pricing long_context must be a mapping: {path}"
                )
            threshold = long_context.get("threshold_input_tokens")
            if (
                not isinstance(threshold, int)
                or isinstance(threshold, bool)
                or threshold < 1
            ):
                raise ValueError(
                    "model pricing long_context.threshold_input_tokens must be "
                    f"a positive integer: {path}"
                )
            validate_pricing_rates(
                long_context,
                path=path,
                context="long_context",
            )
        validated.append(entry)
    return validated


MODEL_PRICING = load_model_pricing()


def pricing_for_request(provider: str, model: str) -> dict[str, Any]:
    matches = [
        entry
        for entry in MODEL_PRICING
        if entry.get("provider") == provider
        and model in (entry.get("request_models") or [])
    ]
    if len(matches) != 1:
        raise ValueError(
            f"model is not present in trusted pricing policy: {provider}/{model}"
        )
    return matches[0]


def request_pricing_rates(
    usage: dict[str, int],
    pricing: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    """Select the full-request pricing tier from provider-reported input usage."""

    long_context = pricing.get("long_context")
    input_tokens = max(0, int(usage.get("input_tokens", 0) or 0))
    if (
        isinstance(long_context, dict)
        and input_tokens > int(long_context["threshold_input_tokens"])
    ):
        return long_context, "long_context"
    return pricing, "base"


def input_token_buckets(usage: dict[str, int]) -> tuple[int, int, int]:
    """Return disjoint ordinary, cache-read, and cache-write input buckets."""

    input_tokens = max(0, int(usage.get("input_tokens", 0) or 0))
    cached = min(
        input_tokens,
        max(0, int(usage.get("cached_input_tokens", 0) or 0)),
    )
    cache_write = min(
        input_tokens - cached,
        max(0, int(usage.get("cache_write_input_tokens", 0) or 0)),
    )
    ordinary = input_tokens - cached - cache_write
    return ordinary, cached, cache_write


def hour_write_tokens(usage: dict[str, int], rates: dict[str, Any], writes: int) -> int:
    hour = usage.get("cache_write_1h_input_tokens", 0)
    if type(hour) is not int or not 0 <= hour <= writes:
        raise ValueError("Invalid one-hour cache-write usage")
    if writes and "cache_write_1h_per_mtok" in rates and "cache_write_1h_input_tokens" not in usage:
        raise ValueError("Missing cache-duration usage for duration-priced cache writes")
    if hour and "cache_write_1h_per_mtok" not in rates:
        raise ValueError("Unpriced one-hour cache writes")
    return hour


def request_usd(usage: dict[str, int], pricing: dict[str, Any]) -> float:
    """Calculate one request's USD from disjoint usage buckets and its tier.

    ``input_tokens`` includes ordinary input, cache reads, and cache writes.
    Reasoning tokens are a subset of ``output_tokens``, so they are observed
    separately but never added to the bill a second time.
    """

    rates, _ = request_pricing_rates(usage, pricing)
    ordinary, cached, cache_write = input_token_buckets(usage)
    output = max(0, int(usage.get("output_tokens", 0) or 0))
    cache_write_rate = float(
        rates.get("cache_write_per_mtok", rates["input_per_mtok"])
    )
    hour = hour_write_tokens(usage, rates, cache_write)
    return (
        ordinary * float(rates["input_per_mtok"]) / 1e6
        + cached * float(rates["cached_read_per_mtok"]) / 1e6
        + (cache_write - hour) * cache_write_rate / 1e6
        + hour * float(rates.get("cache_write_1h_per_mtok", 0)) / 1e6
        + output * float(rates["output_per_mtok"]) / 1e6
    )


def request_budget_tokens(
    usage: dict[str, int],
    pricing: dict[str, Any] | None,
) -> int:
    """Return cost-proxy tokens while preserving the historical output weight."""

    ordinary, cached, cache_write = input_token_buckets(usage)
    output = max(0, int(usage.get("output_tokens", 0) or 0))
    reported_total = max(0, int(usage.get("total_tokens", 0) or 0))
    unclassified = max(
        0,
        reported_total - ordinary - cached - cache_write - output,
    )
    if pricing is None:
        hour = 0
        hour_weight = 1.0
        cached_weight = CACHED_TOKEN_WEIGHT
        cache_write_weight = 1.0
    else:
        rates, _ = request_pricing_rates(usage, pricing)
        hour = hour_write_tokens(usage, rates, cache_write)
        input_rate = float(rates["input_per_mtok"])
        if input_rate > 0:
            cached_weight = (
                CACHED_TOKEN_WEIGHT
                if _CACHED_TOKEN_WEIGHT_OVERRIDE is not None
                else float(rates["cached_read_per_mtok"]) / input_rate
            )
            cache_write_weight = float(
                rates.get("cache_write_per_mtok", input_rate)
            ) / input_rate
            hour_weight = float(rates.get("cache_write_1h_per_mtok", input_rate)) / input_rate
        else:
            cached_weight = CACHED_TOKEN_WEIGHT
            cache_write_weight = 1.0
            hour_weight = 1.0
    return max(
        0,
        round(
            ordinary
            + cached * cached_weight
            + (cache_write - hour) * cache_write_weight
            + hour * hour_weight
            + output
            + unclassified
        ),
    )
