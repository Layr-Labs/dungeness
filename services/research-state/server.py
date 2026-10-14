#!/usr/bin/env python3
"""Run-scoped state for web, evaluation, and knowledge-base controls."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
import re
import signal
import socket
import threading
import time
from typing import Any
import unicodedata
import urllib.error
import urllib.request
import uuid


PORT = int(os.environ.get("RESEARCH_STATE_PORT", "8079"))
USAGE_DIR = Path(os.environ.get("TESTBED_USAGE_DIR", "/var/lib/testbed/usage"))
MAX_BODY_BYTES = 64 * 1024
MODES = {"observe", "prompt_only", "enforce_minimum"}
LEVELS = {"low", "medium", "high"}
EVENT_SCHEMA_VERSION = 1
EVENT_TOKEN_FILENAME = ".event-token"
DEFAULT_EVENT_URL = "http://gateway:8080/internal/events"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def append_jsonl_locked(path: Path, record: dict[str, Any]) -> None:
    encoded = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    with path.open("a+", encoding="utf-8") as output:
        try:
            path.chmod(0o666)
        except OSError:
            pass
        fcntl.flock(output.fileno(), fcntl.LOCK_EX)
        try:
            event_id = record.get("event_id")
            if event_id:
                event_needle = (
                    '"event_id":'
                    + json.dumps(event_id, ensure_ascii=False)
                )
                source_needle = (
                    '"source":'
                    + json.dumps(record.get("source"), ensure_ascii=False)
                )
                output.seek(0)
                for line in output:
                    if event_needle in line and source_needle in line:
                        return
            output.seek(0, os.SEEK_END)
            output.write(encoded + "\n")
            output.flush()
        finally:
            fcntl.flock(output.fileno(), fcntl.LOCK_UN)


def normalize_query(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.rstrip(" \t\r\n.!?。！？")


def query_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require_int(value: Any, field: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"{field} must be an integer >= {minimum}")
    return value


def require_number(
    value: Any,
    field: str,
    *,
    minimum: float = 0,
) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        or value < minimum
    ):
        raise ValueError(f"{field} must be a finite number >= {minimum}")
    return float(value)


@dataclass(frozen=True)
class Control:
    mode: str
    level: str
    minimum: int
    soft_min: int
    soft_max: int
    global_limit: int

    @classmethod
    def parse(cls, value: Any, field: str) -> "Control":
        if not isinstance(value, dict):
            raise ValueError(f"{field} must be an object")
        mode = value.get("mode")
        level = value.get("level")
        if mode not in MODES:
            raise ValueError(f"{field}.mode must be one of {sorted(MODES)}")
        if level not in LEVELS:
            raise ValueError(f"{field}.level must be one of {sorted(LEVELS)}")
        minimum = require_int(value.get("minimum"), f"{field}.minimum")
        soft_min = require_int(value.get("soft_min"), f"{field}.soft_min")
        soft_max = require_int(value.get("soft_max"), f"{field}.soft_max")
        global_limit = require_int(
            value.get("global_limit"), f"{field}.global_limit", minimum=1
        )
        if not minimum <= soft_min <= soft_max <= global_limit:
            raise ValueError(
                f"{field} must satisfy minimum <= soft_min <= soft_max "
                "<= global_limit"
            )
        return cls(
            mode=mode,
            level=level,
            minimum=minimum,
            soft_min=soft_min,
            soft_max=soft_max,
            global_limit=global_limit,
        )


class ResearchState:
    """Single-writer logical state guarded for concurrent HTTP requests."""

    def __init__(self, config: dict[str, Any], usage_dir: Path):
        self.run_id = str(config["run_id"])
        controls = config.get("controls")
        if not isinstance(controls, dict):
            raise ValueError("controls must be an object")
        self.web_control = Control.parse(
            controls.get("web_search"), "controls.web_search"
        )
        self.evaluation_control = Control.parse(
            controls.get("evaluation"), "controls.evaluation"
        )
        feedback = config.get("kb_behavior_feedback")
        if feedback is None:
            feedback = {"enabled": False, "mode": "off"}
        if not isinstance(feedback, dict):
            raise ValueError("kb_behavior_feedback must be an object")
        feedback_mode = feedback.get("mode", "off")
        if feedback_mode not in {"off", "shadow", "visible"}:
            raise ValueError(
                "kb_behavior_feedback.mode must be off, shadow, or visible"
            )
        minimum_improvement = feedback.get("minimum_improvement", 0)
        baseline_score = feedback.get("baseline_score")
        self.kb_behavior_feedback_config = {
            "enabled": (
                bool(feedback.get("enabled", False))
                and feedback_mode != "off"
            ),
            "mode": feedback_mode,
            "minimum_improvement": require_number(
                minimum_improvement,
                "kb_behavior_feedback.minimum_improvement",
                minimum=0,
            ),
            "attribution_window": require_int(
                feedback.get("kb_attribution_window_evaluations", 1),
                "kb_behavior_feedback.kb_attribution_window_evaluations",
                minimum=1,
            ),
            "stick_threshold": require_int(
                feedback.get("no_progress_evaluations", 3),
                "kb_behavior_feedback.no_progress_evaluations",
                minimum=1,
            ),
            "expose_pre_stick_counter": bool(
                feedback.get("expose_pre_stick_counter", True)
            ),
            # The checkpoint reference score, when the run has one. Seeding the
            # best score means the first evaluation can already earn a carrot
            # instead of being spent establishing a baseline the run knew.
            "baseline_score": (
                None
                if baseline_score is None
                else require_number(
                    baseline_score, "kb_behavior_feedback.baseline_score"
                )
            ),
        }
        safeguards = config.get("safeguards")
        if not isinstance(safeguards, dict):
            raise ValueError("safeguards must be an object")
        self.max_stop_interventions = require_int(
            safeguards.get("max_stop_interventions"),
            "safeguards.max_stop_interventions",
            minimum=1,
        )
        self.max_stalled_interventions = require_int(
            safeguards.get("max_stalled_interventions"),
            "safeguards.max_stalled_interventions",
            minimum=1,
        )
        self.finalization_reserve_sec = require_int(
            safeguards.get("finalization_reserve_sec"),
            "safeguards.finalization_reserve_sec",
        )
        self.profile = str(config["profile"])
        self.profile_sha256 = str(config["profile_sha256"])
        self.metric_direction = str(config.get("metric_direction", "minimize"))
        if self.metric_direction not in {"minimize", "maximize"}:
            raise ValueError("metric_direction must be minimize or maximize")
        self.agent_timeout_sec = require_int(
            config.get("agent_timeout_sec"), "agent_timeout_sec", minimum=1
        )
        model_budget = config.get("model_budget")
        if not isinstance(model_budget, dict):
            raise ValueError("model_budget must be an object")
        self.model_token_budget = require_int(
            model_budget.get("total_tokens"),
            "model_budget.total_tokens",
            minimum=1,
        )
        normalized_usd = model_budget.get("normalized_usd")
        self.model_usd_budget = (
            None
            if normalized_usd is None
            else require_number(
                normalized_usd,
                "model_budget.normalized_usd",
                minimum=0.000001,
            )
        )
        self.started_monotonic = time.monotonic()
        self.usage_dir = usage_dir
        self.usage_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.seen_event_ids: set[str] = set()
        self.search_queries: set[str] = set()
        self.candidate_digests: set[str] = set()
        self.web = {
            "attempts": 0,
            "successful": 0,
            "qualifying_distinct": 0,
            "duplicates": 0,
            "failed_or_rejected": 0,
        }
        self.evaluation = {
            "attempts": 0,
            "qualifying_distinct": 0,
            "duplicates": 0,
            "valid": 0,
            "invalid": 0,
            "failed_or_rejected": 0,
            "best_score": None,
            "best_candidate_sha256": None,
        }
        self.kb_behavior_feedback: dict[str, Any] = {
            "enabled": self.kb_behavior_feedback_config["enabled"],
            "mode": self.kb_behavior_feedback_config["mode"],
            "condition": "kb-carrot-stick-v1",
            "evaluation_index": 0,
            "last_score": None,
            "best_score": self.kb_behavior_feedback_config["baseline_score"],
            "no_progress_streak": 0,
            "uninspired_stall_count": 0,
            "evaluations_since_qualifying_kb_lookup": None,
            "kb_attribution_evaluations_remaining": 0,
            "last_qualifying_kb_lookup_id": None,
            "pending_kb_lookup_ids": [],
            "last_feedback_type": "none",
            "latest_feedback": None,
            "carrot_count": 0,
            "stick_count": 0,
            "qualifying_kb_lookup_count": 0,
            "post_kb_improvement_count": 0,
            "lookup_attempt_count": 0,
            "nonqualifying_lookup_count": 0,
            "recent_valid_scores": [],
        }
        self.model_usage = {
            "requests": 0,
            "tokens": 0,
            "normalized_usd": 0.0,
        }
        self.stop_interventions = 0
        self.stalled_interventions = 0
        self.last_intervention_progress: tuple[int, ...] | None = None
        self.completion_results: dict[str, dict[str, Any]] = {}
        self.status = "active"
        self.safeguard_triggered: str | None = None
        self._write_summary_locked()

    def _append_event_locked(self, event: dict[str, Any]) -> None:
        observed_at = utc_now()
        payload = dict(event)
        raw_kind = str(payload.pop("kind", "event"))
        raw_event_id = payload.pop("event_id", None)
        event_id = (
            raw_event_id
            if isinstance(raw_event_id, str) and raw_event_id
            else f"research-state:{uuid.uuid4().hex}"
        )
        kind = f"research_state.{raw_kind}"
        document = {
            "run_id": self.run_id,
            "source": "research-state",
            "kind": kind,
            "observed_at": observed_at,
            "event_id": event_id,
            "data": payload,
        }
        try:
            token = (
                self.usage_dir / EVENT_TOKEN_FILENAME
            ).read_text(encoding="utf-8").strip()
            if not token:
                raise OSError("empty gateway event token")
            request = urllib.request.Request(
                os.environ.get("DUNGENESS_EVENT_URL", DEFAULT_EVENT_URL),
                data=json.dumps(document, separators=(",", ":")).encode("utf-8"),
                headers={
                    "content-type": "application/json",
                    "x-dungeness-event-token": token,
                },
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=2):
                return
        except (OSError, urllib.error.URLError, TypeError, ValueError):
            pass

        record: dict[str, Any] = {
            "schema_version": EVENT_SCHEMA_VERSION,
            "run_id": self.run_id,
            "sequence": None,
            "source": "research-state",
            "kind": kind,
            "observed_at": observed_at,
            "recorded_at": utc_now(),
            "event_id": event_id,
            "data": payload,
        }
        try:
            append_jsonl_locked(self.usage_dir / "events.jsonl", record)
        except OSError:
            pass

    def _write_summary_locked(self) -> None:
        temporary = self.usage_dir / ".research-state-summary.json.tmp"
        temporary.write_text(
            json.dumps(self.summary_locked(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.usage_dir / "research-state-summary.json")

    def _remaining_time_locked(self) -> int:
        elapsed = int(time.monotonic() - self.started_monotonic)
        return max(0, self.agent_timeout_sec - elapsed)

    def _model_budget_progress_locked(self) -> float:
        fractions = [
            self.model_usage["tokens"] / self.model_token_budget,
        ]
        if self.model_usd_budget is not None:
            fractions.append(
                self.model_usage["normalized_usd"] / self.model_usd_budget
            )
        return min(1.0, max(fractions))

    def _control_cadence_locked(
        self,
        control: Control,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        progress = self._model_budget_progress_locked()
        minimum = control.minimum
        required_now = (
            0 if progress <= 0 or minimum <= 0 else math.ceil(minimum * progress)
        )
        completed = state["qualifying_distinct"]
        return {
            "budget_progress": round(progress, 6),
            "required_now": required_now,
            "debt": max(0, required_now - completed),
            "remaining_final_minimum": max(0, minimum - completed),
        }

    @staticmethod
    def _control_view(
        control: Control, state: dict[str, Any]
    ) -> dict[str, Any]:
        view: dict[str, Any] = {
            "qualifying_completed": state["qualifying_distinct"],
            "remaining_global_budget": max(
                0, control.global_limit - state["attempts"]
            ),
        }
        if control.mode != "observe":
            view.update(
                {
                    "level": control.level,
                    "soft_target": [control.soft_min, control.soft_max],
                    "minimum": control.minimum,
                }
            )
        return view

    def model_view_locked(self) -> dict[str, Any]:
        web = self._control_view(self.web_control, self.web)
        web["duplicates"] = self.web["duplicates"]
        if self.web_control.mode != "observe":
            web["cadence"] = self._control_cadence_locked(
                self.web_control,
                self.web,
            )
        evaluation = self._control_view(
            self.evaluation_control, self.evaluation
        )
        evaluation.update(
            {
                "duplicates": self.evaluation["duplicates"],
                "valid": self.evaluation["valid"],
                "invalid": self.evaluation["invalid"],
                "best_score": self.evaluation["best_score"],
                "best_candidate_sha256": self.evaluation[
                    "best_candidate_sha256"
                ],
            }
        )
        if self.evaluation_control.mode != "observe":
            evaluation["cadence"] = self._control_cadence_locked(
                self.evaluation_control,
                self.evaluation,
            )
        deficits = self._deficits_locked()
        view = {
            "schema_version": 1,
            "run_id": self.run_id,
            "web_search": web,
            "evaluation": evaluation,
            "model_usage": {
                **self.model_usage,
                "token_budget": self.model_token_budget,
                "normalized_usd_budget": self.model_usd_budget,
                "remaining_tokens": max(
                    0, self.model_token_budget - self.model_usage["tokens"]
                ),
                "remaining_normalized_usd": (
                    None
                    if self.model_usd_budget is None
                    else round(
                        max(
                            0.0,
                            self.model_usd_budget
                            - self.model_usage["normalized_usd"],
                        ),
                        6,
                    )
                ),
            },
            "time_remaining_sec": self._remaining_time_locked(),
            "completion_eligible": not deficits,
            "unmet_enforced_minimums": deficits,
        }
        # Shadow mode records carrot/stick telemetry without ever showing it to
        # the model, so only visible mode may reach the model view.
        if (
            self.kb_behavior_feedback_config["enabled"]
            and self.kb_behavior_feedback_config["mode"] == "visible"
        ):
            view["kb_behavior_feedback"] = dict(self.kb_behavior_feedback)
        return view

    def model_view(self) -> dict[str, Any]:
        with self.lock:
            return self.model_view_locked()

    def _deficits_locked(self) -> dict[str, int]:
        deficits: dict[str, int] = {}
        for name, control, state in (
            ("web_search", self.web_control, self.web),
            ("evaluation", self.evaluation_control, self.evaluation),
        ):
            if control.mode == "enforce_minimum":
                remaining = max(
                    0, control.minimum - state["qualifying_distinct"]
                )
                if remaining:
                    deficits[name] = remaining
        return deficits

    def apply_web_event(self, event: dict[str, Any]) -> dict[str, Any]:
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id must be non-empty text")
        status = event.get("status")
        if status not in {"success", "failed", "rejected", "budget_rejected"}:
            raise ValueError("invalid web-search status")
        query = event.get("query")
        with self.lock:
            if event_id in self.seen_event_ids:
                return {"accepted": False, "duplicate_event": True}
            self.seen_event_ids.add(event_id)
            self.web["attempts"] += 1
            normalized = normalize_query(query) if isinstance(query, str) else ""
            audit = {
                "kind": "web_search",
                "event_id": event_id,
                "status": status,
                "query_sha256": query_digest(normalized) if normalized else None,
            }
            if status == "success" and normalized:
                self.web["successful"] += 1
                if normalized in self.search_queries:
                    self.web["duplicates"] += 1
                    audit["qualifying"] = False
                    audit["duplicate"] = True
                else:
                    self.search_queries.add(normalized)
                    self.web["qualifying_distinct"] += 1
                    audit["qualifying"] = True
                    audit["duplicate"] = False
            else:
                self.web["failed_or_rejected"] += 1
                audit["qualifying"] = False
            self._append_event_locked(audit)
            self._write_summary_locked()
            return {"accepted": True, "model_view": self.model_view_locked()}

    def apply_knowledge_base_inspiration_event(
        self, event: dict[str, Any]
    ) -> dict[str, Any]:
        if not self.kb_behavior_feedback_config["enabled"]:
            return {"accepted": False, "disabled": True}
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id must be non-empty text")
        lookup_id = event.get("kb_lookup_id")
        query = event.get("query")
        query_sha256 = event.get("query_sha256")
        qualifying = event.get("qualifying")
        takeaway = event.get("takeaway")
        planned_change = event.get("planned_change")
        new_passage_count = event.get("new_passage_count")
        if not isinstance(lookup_id, str) or not lookup_id:
            raise ValueError("kb_lookup_id must be non-empty text")
        if not isinstance(query, str) or not 1 <= len(query) <= 4096:
            raise ValueError("query must be bounded non-empty text")
        if not isinstance(query_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", query_sha256
        ):
            raise ValueError("query_sha256 must be a sha256 digest")
        if not isinstance(qualifying, bool):
            raise ValueError("qualifying must be boolean")
        if not isinstance(takeaway, str) or not takeaway.strip():
            raise ValueError("takeaway must be non-empty text")
        if not isinstance(planned_change, str) or not planned_change.strip():
            raise ValueError("planned_change must be non-empty text")
        new_passage_count = require_int(
            new_passage_count, "new_passage_count"
        )
        with self.lock:
            if event_id in self.seen_event_ids:
                return {"accepted": False, "duplicate_event": True}
            self.seen_event_ids.add(event_id)
            feedback = self.kb_behavior_feedback
            feedback["lookup_attempt_count"] += 1
            if qualifying:
                feedback["qualifying_kb_lookup_count"] += 1
                feedback["last_qualifying_kb_lookup_id"] = lookup_id
                # The carrot message quotes exactly one lookup, so attribute to
                # exactly one lookup: the most recent qualifying one.
                feedback["pending_kb_lookup_ids"] = [lookup_id]
                feedback["last_kb_query"] = query
                feedback["last_kb_takeaway"] = takeaway.strip()
                feedback["last_kb_planned_change"] = planned_change.strip()
                feedback["evaluations_since_qualifying_kb_lookup"] = 0
                feedback["kb_attribution_evaluations_remaining"] = (
                    self.kb_behavior_feedback_config["attribution_window"]
                )
                feedback["uninspired_stall_count"] = 0
                # A stick says "go consult the knowledge base". Once that has
                # happened the message has been answered, so stop replaying it
                # on every later model call.
                feedback["latest_feedback"] = None
                feedback["last_feedback_type"] = "none"
            else:
                feedback["nonqualifying_lookup_count"] += 1
            self._append_event_locked({
                "kind": "kb_lookup_completed",
                "event_id": event_id,
                "kb_lookup_id": lookup_id,
                "evaluation_index_before_lookup": feedback["evaluation_index"],
                "query": query,
                "query_sha256": query_sha256,
                "new_passage_count": new_passage_count,
                "qualifying": qualifying,
                "takeaway_present": bool(takeaway.strip()),
                "planned_change_present": bool(planned_change.strip()),
                "reason": event.get("reason"),
            })
            self._write_summary_locked()
            return {"accepted": True, "model_view": self.model_view_locked()}

    def apply_model_usage_event(self, event: dict[str, Any]) -> dict[str, Any]:
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id must be non-empty text")
        requests = require_int(
            event.get("model_requests"), "model_requests"
        )
        tokens = require_int(event.get("model_tokens"), "model_tokens")
        normalized_usd = require_number(
            event.get("normalized_usd"), "normalized_usd"
        )
        with self.lock:
            if event_id in self.seen_event_ids:
                return {"accepted": False, "duplicate_event": True}
            self.seen_event_ids.add(event_id)
            self.model_usage["requests"] = max(
                self.model_usage["requests"], requests
            )
            self.model_usage["tokens"] = max(
                self.model_usage["tokens"], tokens
            )
            self.model_usage["normalized_usd"] = max(
                self.model_usage["normalized_usd"], normalized_usd
            )
            self._append_event_locked(
                {
                    "kind": "model_usage",
                    "event_id": event_id,
                    "model_requests": requests,
                    "model_tokens": tokens,
                    "normalized_usd": normalized_usd,
                    "web_search_cadence": self._control_cadence_locked(
                        self.web_control,
                        self.web,
                    ),
                    "evaluation_cadence": self._control_cadence_locked(
                        self.evaluation_control,
                        self.evaluation,
                    ),
                }
            )
            self._write_summary_locked()
            return {"accepted": True, "model_view": self.model_view_locked()}

    def _emit_behavior_feedback_locked(
        self,
        feedback_type: str,
        reason_code: str,
        message: str,
        **fields: Any,
    ) -> None:
        visible = self.kb_behavior_feedback_config["mode"] == "visible"
        feedback = {
            "type": feedback_type,
            "reason_code": reason_code,
            "evaluation_index": self.kb_behavior_feedback["evaluation_index"],
            "visible_to_agent": visible,
            "message": message,
            **fields,
        }
        self.kb_behavior_feedback["last_feedback_type"] = feedback_type
        self.kb_behavior_feedback["latest_feedback"] = feedback
        self._append_event_locked({
            "kind": "behavior_feedback_emitted",
            "feedback_type": feedback_type,
            "reason_code": reason_code,
            "evaluation_index": feedback["evaluation_index"],
            "visible_to_agent": visible,
            **fields,
        })

    def _improves(self, score: float, best: float, margin: float = 0.0) -> bool:
        """Is `score` better than `best` by more than `margin`?

        One definition of "better" for every caller, so the carrot/stick
        controller and the best-score tracker can never disagree about which
        way the benchmark metric points.
        """

        if self.metric_direction == "maximize":
            return score > best + margin
        return score < best - margin

    def _apply_behavior_evaluation_locked(self, score: float) -> None:
        if not self.kb_behavior_feedback_config["enabled"]:
            return
        state = self.kb_behavior_feedback
        state["evaluation_index"] += 1
        state["last_score"] = score
        state["recent_valid_scores"].append(score)
        state["recent_valid_scores"] = state["recent_valid_scores"][-3:]
        previous_best = state["best_score"]
        if previous_best is None:
            state["best_score"] = score
            state["latest_feedback"] = None
            state["last_feedback_type"] = "none"
            if state["evaluations_since_qualifying_kb_lookup"] is not None:
                state["evaluations_since_qualifying_kb_lookup"] += 1
            if state["kb_attribution_evaluations_remaining"] > 0:
                state["kb_attribution_evaluations_remaining"] -= 1
            if state["kb_attribution_evaluations_remaining"] == 0:
                state["pending_kb_lookup_ids"] = []
            self._append_event_locked({
                "kind": "lm_evaluation_completed",
                "evaluation_index": state["evaluation_index"],
                "score": score,
                "previous_best_score": None,
                "progress": False,
                "reason": "baseline_established",
            })
            return

        progress = self._improves(
            score,
            previous_best,
            self.kb_behavior_feedback_config["minimum_improvement"],
        )
        attributed = state["kb_attribution_evaluations_remaining"] > 0
        attributed_ids = list(state["pending_kb_lookup_ids"]) if attributed else []
        self._append_event_locked({
            "kind": "lm_evaluation_completed",
            "evaluation_index": state["evaluation_index"],
            "score": score,
            "previous_best_score": previous_best,
            "progress": progress,
            "attributed_to_kb_lookup_ids": attributed_ids,
        })

        if progress:
            state["best_score"] = score
            state["no_progress_streak"] = 0
            state["uninspired_stall_count"] = 0
            if attributed:
                improvement = abs(score - previous_best)
                state["carrot_count"] += 1
                state["post_kb_improvement_count"] += 1
                self._emit_behavior_feedback_locked(
                    "carrot",
                    "KB_ATTRIBUTED_SCORE_IMPROVEMENT",
                    (
                        "BEHAVIOR FEEDBACK: CARROT\n\n"
                        "Good use of the knowledge base. You consulted:\n"
                        f"{state.get('last_kb_query', '')}\n\n"
                        f"Takeaway: {state.get('last_kb_takeaway', '')}\n"
                        f"Planned change: {state.get('last_kb_planned_change', '')}\n\n"
                        "The next LM evaluation improved the best score:\n"
                        f"- Previous best: {previous_best}\n"
                        f"- New best: {score}\n"
                        f"- Improvement: {improvement}\n\n"
                        "Preserve the successful idea and continue from this approach."
                    ),
                    previous_best_score=previous_best,
                    new_best_score=score,
                    improvement=improvement,
                    kb_lookup_ids=attributed_ids,
                )
            else:
                state["latest_feedback"] = None
                state["last_feedback_type"] = "none"
        else:
            state["no_progress_streak"] += 1
            state["uninspired_stall_count"] += 1
            if state["uninspired_stall_count"] >= (
                self.kb_behavior_feedback_config["stick_threshold"]
            ):
                recent = list(state["recent_valid_scores"])
                state["stick_count"] += 1
                self._emit_behavior_feedback_locked(
                    "stick",
                    "THREE_UNINSPIRED_NO_PROGRESS_EVALUATIONS",
                    (
                        "BEHAVIOR FEEDBACK: STICK\n\n"
                        "You completed three consecutive LM evaluations without "
                        f"improving the best score: {recent}.\n\n"
                        "No qualifying knowledge-base lookup occurred during this "
                        "stalled sequence. You are repeating an unproductive "
                        "approach without seeking new inspiration.\n\n"
                        "Consult the knowledge base for a different, concrete "
                        "implementation idea before continuing."
                    ),
                    recent_scores=recent,
                    best_score=previous_best,
                )
                state["uninspired_stall_count"] = 0
            else:
                counter = (
                    "No-progress evaluations without a qualifying KB "
                    f"lookup: {state['uninspired_stall_count']}/"
                    f"{self.kb_behavior_feedback_config['stick_threshold']}."
                    if self.kb_behavior_feedback_config[
                        "expose_pre_stick_counter"
                    ]
                    else "The current evaluation did not improve the best score."
                )
                self._emit_behavior_feedback_locked(
                    "neutral",
                    (
                        "KB_ATTRIBUTED_NO_PROGRESS"
                        if attributed
                        else "NO_PROGRESS"
                    ),
                    (
                        "BEHAVIOR FEEDBACK: NEUTRAL\n\n"
                        + (
                            "The KB-attributed evaluation did not improve the "
                            "best score. No carrot is awarded. "
                            if attributed
                            else ""
                        )
                        + counter
                    ),
                    best_score=previous_best,
                    score=score,
                    uninspired_stall_count=state["uninspired_stall_count"],
                )

        if state["evaluations_since_qualifying_kb_lookup"] is not None:
            state["evaluations_since_qualifying_kb_lookup"] += 1
        if state["kb_attribution_evaluations_remaining"] > 0:
            state["kb_attribution_evaluations_remaining"] -= 1
        if state["kb_attribution_evaluations_remaining"] == 0:
            state["pending_kb_lookup_ids"] = []

    def apply_evaluation_event(self, event: dict[str, Any]) -> dict[str, Any]:
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id must be non-empty text")
        status = event.get("status")
        if status not in {
            "valid",
            "invalid",
            "failed",
            "budget_rejected",
        }:
            raise ValueError("invalid evaluation status")
        candidate = event.get("candidate_sha256")
        score = event.get("score")
        if (
            score is not None
            and (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not math.isfinite(score)
            )
        ):
            raise ValueError("score must be numeric or null")
        with self.lock:
            if event_id in self.seen_event_ids:
                return {"accepted": False, "duplicate_event": True}
            self.seen_event_ids.add(event_id)
            self.evaluation["attempts"] += 1
            audit = {
                "kind": "evaluation",
                "event_id": event_id,
                "status": status,
                "candidate_sha256": candidate,
                "score": score,
            }
            if status in {"valid", "invalid"} and isinstance(candidate, str) and candidate:
                if candidate in self.candidate_digests:
                    self.evaluation["duplicates"] += 1
                    audit["qualifying"] = False
                    audit["duplicate"] = True
                else:
                    self.candidate_digests.add(candidate)
                    self.evaluation["qualifying_distinct"] += 1
                    self.evaluation[status] += 1
                    audit["qualifying"] = True
                    audit["duplicate"] = False
                    if status == "valid" and score is not None:
                        best = self.evaluation["best_score"]
                        if best is None or self._improves(score, best):
                            self.evaluation["best_score"] = score
                            self.evaluation["best_candidate_sha256"] = candidate
                        # Only distinct candidates advance the carrot/stick
                        # clock; re-evaluating the same bytes is not a new
                        # attempt at the problem.
                        self._apply_behavior_evaluation_locked(float(score))
            else:
                self.evaluation["failed_or_rejected"] += 1
                audit["qualifying"] = False
            self._append_event_locked(audit)
            self._write_summary_locked()
            return {"accepted": True, "model_view": self.model_view_locked()}

    def completion_attempt(self, request: dict[str, Any]) -> dict[str, Any]:
        attempt_id = request.get("attempt_id")
        if not isinstance(attempt_id, str) or not attempt_id:
            raise ValueError("attempt_id must be non-empty text")
        supplied_remaining = request.get("time_remaining_sec")
        with self.lock:
            existing = self.completion_results.get(attempt_id)
            if existing is not None:
                return existing
            remaining = self._remaining_time_locked()
            if isinstance(supplied_remaining, int) and not isinstance(
                supplied_remaining, bool
            ):
                remaining = min(remaining, max(0, supplied_remaining))
            deficits = self._deficits_locked()
            result: dict[str, Any]
            safeguard = None
            if not deficits:
                self.status = "completed_compliant"
                result = {
                    "decision": "accept",
                    "compliance": True,
                    "model_view": self.model_view_locked(),
                }
            else:
                progress = (
                    self.web["qualifying_distinct"],
                    self.evaluation["qualifying_distinct"],
                )
                if self.last_intervention_progress == progress:
                    self.stalled_interventions += 1
                else:
                    self.stalled_interventions = 0
                if remaining <= self.finalization_reserve_sec:
                    safeguard = "finalization_reserve"
                elif self.stop_interventions >= self.max_stop_interventions:
                    safeguard = "max_stop_interventions"
                elif self.stalled_interventions >= self.max_stalled_interventions:
                    safeguard = "max_stalled_interventions"
                if safeguard is not None:
                    self.status = "completed_noncompliant"
                    self.safeguard_triggered = safeguard
                    result = {
                        "decision": "accept",
                        "compliance": False,
                        "safeguard_triggered": safeguard,
                        "model_view": self.model_view_locked(),
                    }
                else:
                    self.stop_interventions += 1
                    self.last_intervention_progress = progress
                    deficit_text = ", ".join(
                        f"{name.replace('_', ' ')}: {count} more"
                        for name, count in sorted(deficits.items())
                    )
                    result = {
                        "decision": "block",
                        "compliance": False,
                        "reason": (
                            "Dungeness research-effort state is incomplete. "
                            f"Remaining distinct qualifying work: {deficit_text}. "
                            "Continue with useful, non-duplicate research or "
                            "candidate evaluation before leaving the best valid "
                            "candidate for final verification."
                        ),
                        "model_view": self.model_view_locked(),
                    }
            self.completion_results[attempt_id] = result
            self._append_event_locked(
                {
                    "kind": "completion_attempt",
                    "attempt_id": attempt_id,
                    "decision": result["decision"],
                    "deficits": deficits,
                    "safeguard_triggered": safeguard,
                }
            )
            self._write_summary_locked()
            return result

    def summary_locked(self) -> dict[str, Any]:
        summary = {
            "schema_version": 1,
            "run_id": self.run_id,
            "profile": self.profile,
            "profile_sha256": self.profile_sha256,
            "status": self.status,
            "web_search": {
                "mode": self.web_control.mode,
                "assigned_level": self.web_control.level,
                "required_minimum": self.web_control.minimum,
                **self.web,
                "minimum_met": (
                    self.web["qualifying_distinct"] >= self.web_control.minimum
                ),
                "cadence": self._control_cadence_locked(
                    self.web_control,
                    self.web,
                ),
            },
            "evaluation": {
                "mode": self.evaluation_control.mode,
                "assigned_level": self.evaluation_control.level,
                "required_minimum": self.evaluation_control.minimum,
                **self.evaluation,
                "minimum_met": (
                    self.evaluation["qualifying_distinct"]
                    >= self.evaluation_control.minimum
                ),
                "cadence": self._control_cadence_locked(
                    self.evaluation_control,
                    self.evaluation,
                ),
            },
            "model_usage": {
                **self.model_usage,
                "token_budget": self.model_token_budget,
                "normalized_usd_budget": self.model_usd_budget,
                "budget_progress": round(
                    self._model_budget_progress_locked(), 6
                ),
            },
            "completion": {
                "stop_interventions": self.stop_interventions,
                "stalled_interventions": self.stalled_interventions,
                "safeguard_triggered": self.safeguard_triggered,
                "eligible": not self._deficits_locked(),
            },
            "time_remaining_sec": self._remaining_time_locked(),
        }
        if self.kb_behavior_feedback_config["enabled"]:
            summary["kb_behavior_feedback"] = dict(
                self.kb_behavior_feedback
            )
        return summary

    def summary(self) -> dict[str, Any]:
        with self.lock:
            return self.summary_locked()

    def finalize(self) -> dict[str, Any]:
        with self.lock:
            if self.status == "active":
                self.status = (
                    "completed_compliant"
                    if not self._deficits_locked()
                    else "completed_noncompliant"
                )
            self._append_event_locked(
                {"kind": "finalized", "status": self.status}
            )
            self._write_summary_locked()
            final_path = self.usage_dir / "research-state-final.json"
            final_path.write_text(
                json.dumps(self.summary_locked(), indent=2, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
            return self.summary_locked()

    def interrupt(self) -> dict[str, Any]:
        with self.lock:
            if self.status == "active":
                self.status = "interrupted"
                self._append_event_locked(
                    {"kind": "interrupted", "status": self.status}
                )
                self._write_summary_locked()
            return self.summary_locked()


def load_config() -> dict[str, Any]:
    raw = os.environ.get("RESEARCH_STATE_CONFIG_JSON")
    if not raw:
        raise ValueError("RESEARCH_STATE_CONFIG_JSON is required")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("RESEARCH_STATE_CONFIG_JSON must contain an object")
    return value


STATE = ResearchState(load_config(), USAGE_DIR)
TRUSTED_EVENT_HOSTS = tuple(
    value.strip()
    for value in os.environ.get(
        "RESEARCH_STATE_TRUSTED_EVENT_HOSTS",
        "gateway,dev-scorer,knowledge-base",
    ).split(",")
    if value.strip()
)


class Handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, document: dict[str, Any]) -> None:
        body = json.dumps(document, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0"))
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("request body is oversized")
        body = self.rfile.read(length)
        value = json.loads(body or b"{}")
        if not isinstance(value, dict):
            raise ValueError("request body must be a JSON object")
        return value

    def _trusted_event_source(self) -> bool:
        trusted_addresses: set[str] = set()
        for host in TRUSTED_EVENT_HOSTS:
            try:
                trusted_addresses.update(
                    result[4][0]
                    for result in socket.getaddrinfo(
                        host,
                        None,
                        type=socket.SOCK_STREAM,
                    )
                )
            except OSError:
                continue
        return self.client_address[0] in trusted_addresses

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._reply(200, {"status": "ok", "run_id": STATE.run_id})
        elif self.path in {"/model-view", "/status"}:
            self._reply(200, STATE.model_view())
        elif self.path == "/summary":
            self._reply(200, STATE.summary())
        else:
            self._reply(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            document = self._read_json()
            if self.path == "/events/web-search":
                if not self._trusted_event_source():
                    self._reply(403, {"error": "untrusted event source"})
                    return
                result = STATE.apply_web_event(document)
            elif self.path == "/events/evaluation":
                if not self._trusted_event_source():
                    self._reply(403, {"error": "untrusted event source"})
                    return
                result = STATE.apply_evaluation_event(document)
            elif self.path == "/events/model-usage":
                if not self._trusted_event_source():
                    self._reply(403, {"error": "untrusted event source"})
                    return
                result = STATE.apply_model_usage_event(document)
            elif self.path == "/events/knowledge-base-inspiration":
                if not self._trusted_event_source():
                    self._reply(403, {"error": "untrusted event source"})
                    return
                result = STATE.apply_knowledge_base_inspiration_event(document)
            elif self.path == "/completion-attempt":
                result = STATE.completion_attempt(document)
            elif self.path == "/finalize":
                result = STATE.finalize()
            else:
                self._reply(404, {"error": "not found"})
                return
        except (ValueError, json.JSONDecodeError) as error:
            self._reply(400, {"error": str(error)})
            return
        except OSError as error:
            self._reply(500, {"error": f"state persistence failed: {error}"})
            return
        self._reply(200, result)

    def log_message(self, format: str, *args: Any) -> None:
        message = format % args
        print(f"research-state: {message}", file=os.sys.stderr)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)

    def stop_server(_signum: int, _frame: Any) -> None:
        STATE.interrupt()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop_server)
    signal.signal(signal.SIGINT, stop_server)
    try:
        server.serve_forever()
    finally:
        server.server_close()
