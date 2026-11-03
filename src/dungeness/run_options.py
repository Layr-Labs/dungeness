"""Execution permissions, without agent research-strategy profiles."""
from __future__ import annotations

from typing import Any


def resolve_web_access(value: Any) -> dict[str, str]:
    if value is None:
        return {"mode": "disabled"}
    if not isinstance(value, dict):
        raise ValueError("run spec web_search must be a mapping")
    # External web access is retired. Accept old access-only settings but never
    # let optional mode re-enable it. Older OpenRSI releases emit these references.
    # They resolve without loading a profile, prompt, or other repository file.
    if set(value) == {"profile"}:
        aliases = {
            "web-search-profile:system/dungeness/disabled-v1": "disabled",
            "web-search-profile:system/dungeness/optional-v1": "optional",
        }
        profile = value["profile"]
        if isinstance(profile, str) and profile in aliases:
            return {"mode": "disabled"}
        raise ValueError(
            "Research-strategy web profiles have been removed; put search strategy "
            "in the harness and use web_search.mode: optional or disabled."
        )
    if set(value) != {"mode"} or value["mode"] not in ("optional", "disabled"):
        raise ValueError("web_search must contain only mode: optional or disabled")
    return {"mode": "disabled"}


def reject_evaluation_strategy(document: dict[str, Any]) -> None:
    if "evaluation" in document:
        raise ValueError(
            "Run-spec evaluation profiles have been removed; evaluation cadence "
            "belongs to the harness. Trusted evaluation remains configured by the task."
        )
