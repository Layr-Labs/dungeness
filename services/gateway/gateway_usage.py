"""Canonical run events, budget accounting, and gateway metrics."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import secrets
import sys
import threading
from typing import Any
import uuid


_BILLED_AS_NORMALIZED = object()

REQUEST_ID_RE = re.compile(r"[A-Za-z0-9._-]{1,128}")
OPERATIONAL_LOG_LOCK = threading.Lock()
EVENT_SCHEMA_VERSION = 1
EVENT_TOKEN_FILENAME = ".event-token"
MAX_INTERNAL_EVENT_BYTES = 1024 * 1024
INTERNAL_EVENT_KINDS = {
    "evaluator": {"evaluation.completed", "evaluation.delivery"},
}
_ACTIVE_LEDGER: Any = None


def set_active_ledger(ledger: Any | None) -> None:
    """Select the ledger that receives process-local operational events."""

    global _ACTIVE_LEDGER
    _ACTIVE_LEDGER = ledger


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(
        timespec="milliseconds"
    ).replace("+00:00", "Z")


def append_jsonl_locked(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    with path.open("a", encoding="utf-8") as output:
        try:
            path.chmod(0o666)
        except OSError:
            pass
        fcntl.flock(output.fileno(), fcntl.LOCK_EX)
        try:
            output.write(encoded + "\n")
            output.flush()
        finally:
            fcntl.flock(output.fileno(), fcntl.LOCK_UN)


def log_event(event: str, **fields: Any) -> None:
    """Write one redaction-safe operational event to stderr as JSON."""

    record = {
        "timestamp": utc_now(),
        "level": fields.pop("level", "info"),
        "event": event,
        **fields,
    }
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
    print(encoded, file=sys.stderr, flush=True)

    try:
        with OPERATIONAL_LOG_LOCK:
            usage_directory = Path(
                os.environ.get(
                    "TESTBED_USAGE_DIR",
                    "/var/lib/testbed/usage",
                )
            )
            if (
                _ACTIVE_LEDGER is not None
                and _ACTIVE_LEDGER.directory == usage_directory
            ):
                _ACTIVE_LEDGER.emit(
                    source="gateway",
                    kind=f"gateway.{event}",
                    observed_at=record["timestamp"],
                    request_id=record.get("request_id"),
                    data={
                        key: value
                        for key, value in record.items()
                        if key
                        not in {"timestamp", "event", "request_id", "run_id"}
                    },
                )
            else:
                append_jsonl_locked(
                    usage_directory / "events.jsonl",
                    {
                        "schema_version": EVENT_SCHEMA_VERSION,
                        "run_id": fields.get(
                            "run_id",
                            os.environ.get("TESTBED_RUN_ID", "unknown"),
                        ),
                        "sequence": None,
                        "source": "gateway",
                        "kind": f"gateway.{event}",
                        "observed_at": record["timestamp"],
                        "recorded_at": record["timestamp"],
                        "request_id": record.get("request_id"),
                        "data": {
                            key: value
                            for key, value in record.items()
                            if key
                            not in {
                                "timestamp",
                                "event",
                                "request_id",
                                "run_id",
                            }
                        },
                    },
                )
    except OSError as error:
        # Operational logging must not turn a successful provider call into a
        # failed request. stderr remains available as a fallback signal.
        print(
            json.dumps(
                {
                    "timestamp": utc_now(),
                    "level": "error",
                    "event": "instrumentation_write_failed",
                    "error_type": type(error).__name__,
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
            flush=True,
        )


def safe_request_id(value: str | None) -> str:
    """Accept a bounded caller ID or generate one without logging raw input."""

    if value and REQUEST_ID_RE.fullmatch(value):
        return value
    return uuid.uuid4().hex


def bounded_model_name(value: Any) -> str:
    """Keep an agent-controlled model field useful without allowing huge logs."""

    if not isinstance(value, str) or not value:
        return "unknown"
    return value[:256]


def bounded_text(value: Any, limit: int = 1024) -> str:
    """Bound a free-text field (search query / fetch URL) for an audit record."""

    return value[:limit] if isinstance(value, str) else ""


def metric_labels(labels: dict[str, str]) -> str:
    if not labels:
        return ""
    encoded = []
    for name, value in sorted(labels.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        encoded.append(f'{name}="{escaped}"')
    return "{" + ",".join(encoded) + "}"


class Metrics:
    """Minimal in-process Prometheus counter and duration registry."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.values: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)

    def increment(
        self, name: str, *, labels: dict[str, str] | None = None, value: float = 1
    ) -> None:
        key = (name, tuple(sorted((labels or {}).items())))
        with self.lock:
            self.values[key] += value

    def observe_http(
        self, method: str, route: str, status: int, duration_seconds: float
    ) -> None:
        labels = {"method": method, "route": route, "status": str(status)}
        self.increment("testbed_gateway_http_requests_total", labels=labels)
        duration_labels = {"method": method, "route": route}
        self.increment(
            "testbed_gateway_http_request_duration_seconds_count",
            labels=duration_labels,
        )
        self.increment(
            "testbed_gateway_http_request_duration_seconds_sum",
            labels=duration_labels,
            value=duration_seconds,
        )

    def render(self, ledger: "UsageLedger") -> str:
        with self.lock:
            snapshot = list(self.values.items())
        lines = [
            "# Gateway process metrics. Queries, prompts, URLs, and secrets are never labels."
        ]
        for (name, label_items), value in sorted(snapshot):
            labels = metric_labels(dict(label_items))
            rendered = str(int(value)) if value.is_integer() else f"{value:.9f}"
            lines.append(f"{name}{labels} {rendered}")
        with ledger.lock:
            counts = dict(ledger.counts)
            limits = dict(ledger.limits)
        for name in sorted(counts):
            labels = metric_labels({"budget": name})
            lines.append(f"testbed_gateway_budget_used{labels} {counts[name]}")
            if limits[name] is not None:
                lines.append(f"testbed_gateway_budget_limit{labels} {limits[name]}")
        return "\n".join(lines) + "\n"


METRICS = Metrics()


class BudgetExceeded(RuntimeError):
    pass


class UsageLedger:
    """Process-local, thread-safe budget counters backed by append-only events."""

    def __init__(self, run_id: str, directory: Path):
        self.run_id = run_id
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.limits = {
            "searches": int(os.environ["MAX_SEARCHES"]),
            "fetches": int(os.environ["MAX_FETCHES"]),
            "model_requests": int(os.environ["MAX_MODEL_REQUESTS"]),
            "model_tokens": (int(os.environ["MAX_MODEL_TOKENS"])
                             if os.environ.get("MAX_MODEL_TOKENS") else None),
        }
        self.counts = {name: 0 for name in self.limits}
        # Optional USD cap on model spend (the fair, provider-neutral stopping
        # criterion). Unset -> effectively no cap; USD is still recorded.
        self.usd_limit = float(os.environ.get("MAX_MODEL_USD") or "inf")
        self.usd_spent = 0.0
        self.model_inflight: dict[str, float] = {}
        self.model_accounting_incomplete = False
        self.max_parallel_requests = int(os.environ.get("DUNGENESS_MAX_PARALLEL_REQUESTS", "4"))
        self.request_reservation_usd = float(os.environ.get("DUNGENESS_REQUEST_RESERVATION_USD", "1"))
        self.billed_usd_spent = 0.0
        self.billed_usd_known = True
        self.event_sequence = 0
        self.evaluation = {
            "submissions_used": 0,
            "submissions_limit": None,
            "best_score": None,
        }
        self.external_event_ids: set[tuple[str, str]] = set()
        self.event_token = secrets.token_urlsafe(32)
        token_path = self.directory / EVENT_TOKEN_FILENAME
        token_path.write_text(self.event_token + "\n", encoding="utf-8")
        token_path.chmod(0o644)
        self.flush_summary()

    def _usage_snapshot_locked(self) -> dict[str, Any]:
        return {
            **self.counts,
            "model_usd": round(self.usd_spent, 6),
            "normalized_usd": round(self.usd_spent, 6),
            "billed_usd": (
                None
                if not self.billed_usd_known
                else round(self.billed_usd_spent, 6)
            ),
            "accounting_method": "gateway",
            "model_accounting_state": ("incomplete" if self.model_accounting_incomplete
                                       else "pending" if self.model_inflight else "settled"),
        }

    def _write_summary_locked(self) -> None:
        # Replace the summary atomically so observers never see partial JSON.
        temporary = self.directory / ".summary.json.tmp"
        temporary.write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "usage": self._usage_snapshot_locked(),
                    "evaluation": dict(self.evaluation),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.directory / "summary.json")

    def flush_summary(self) -> None:
        with self.lock:
            self._write_summary_locked()

    def status(self) -> dict[str, Any]:
        """Return non-secret run usage, limits, and remaining budgets."""

        with self.lock:
            usd_limit = (
                None if self.usd_limit == float("inf") else round(self.usd_limit, 6)
            )
            usd_spent = round(self.usd_spent, 6)
            return {
                "run_id": self.run_id,
                "usage": {
                    **self.counts,
                    "normalized_usd": usd_spent,
                },
                "limits": {
                    **self.limits,
                    "normalized_usd": usd_limit,
                },
                "remaining": {
                    **{
                        name: (None if self.limits[name] is None else max(0, self.limits[name] - self.counts[name]))
                        for name in self.limits
                    },
                    "normalized_usd": (
                        None
                        if usd_limit is None
                        else round(max(0.0, usd_limit - usd_spent), 6)
                    ),
                },
            }

    def _apply_event_state_locked(
        self,
        source: str,
        kind: str,
        data: dict[str, Any],
    ) -> bool:
        if source != "evaluator" or kind != "evaluation.completed":
            return False
        submissions_used = data.get("submissions_used")
        if isinstance(submissions_used, int) and not isinstance(
            submissions_used,
            bool,
        ):
            self.evaluation["submissions_used"] = max(
                int(self.evaluation["submissions_used"]),
                submissions_used,
            )
        submissions_limit = data.get("submissions_limit")
        if isinstance(submissions_limit, int) and not isinstance(
            submissions_limit,
            bool,
        ):
            self.evaluation["submissions_limit"] = submissions_limit
        score = data.get("score")
        best_score = data.get("best_score")
        if isinstance(best_score, (int, float)) and not isinstance(
            best_score,
            bool,
        ):
            self.evaluation["best_score"] = float(best_score)
        elif (
            data.get("operation") == "score"
            and data.get("status") in {"ok", "valid"}
            and isinstance(score, (int, float))
            and not isinstance(score, bool)
            and self.evaluation["best_score"] is None
        ):
            self.evaluation["best_score"] = float(score)
        return True

    def emit(
        self,
        *,
        source: str,
        kind: str,
        data: dict[str, Any] | None = None,
        observed_at: str | None = None,
        event_id: str | None = None,
        request_id: str | None = None,
        include_usage: bool = False,
    ) -> dict[str, Any]:
        """Append one canonical run event in strict gateway order."""

        payload = dict(data or {})
        with self.lock:
            self.event_sequence += 1
            recorded_at = utc_now()
            record: dict[str, Any] = {
                "schema_version": EVENT_SCHEMA_VERSION,
                "run_id": self.run_id,
                "sequence": self.event_sequence,
                "source": source,
                "kind": kind,
                "observed_at": observed_at or recorded_at,
                "recorded_at": recorded_at,
                "data": payload,
            }
            if event_id:
                record["event_id"] = event_id
            if request_id:
                record["request_id"] = request_id
            if include_usage:
                record["usage"] = self._usage_snapshot_locked()
            state_changed = self._apply_event_state_locked(
                source,
                kind,
                payload,
            )
            append_jsonl_locked(self.directory / "events.jsonl", record)
            if state_changed:
                self._write_summary_locked()
        return record

    def ingest(self, document: dict[str, Any]) -> dict[str, Any]:
        source = str(document["source"])
        kind = str(document["kind"])
        data = document.get("data")
        if not isinstance(data, dict):
            data = {}
        event_id = (
            str(document["event_id"])
            if document.get("event_id")
            else None
        )
        with self.lock:
            event_key = (source, event_id) if event_id else None
            if event_key and event_key in self.external_event_ids:
                return {
                    "accepted": False,
                    "duplicate": True,
                    "event_id": event_id,
                }
            record = self.emit(
                source=source,
                kind=kind,
                data=data,
                observed_at=(
                    str(document["observed_at"])
                    if document.get("observed_at")
                    else None
                ),
                event_id=event_id,
                request_id=(
                    str(document["request_id"])
                    if document.get("request_id")
                    else None
                ),
                include_usage=(
                    source == "evaluator"
                    and kind == "evaluation.completed"
                ),
            )
            if event_key:
                self.external_event_ids.add(event_key)
            return {"accepted": True, **record}

    def reserve(self, name: str) -> None:
        # Count an attempt before forwarding it. Provider errors and timeouts still
        # consume a request/search budget and therefore cannot bypass hard limits.
        with self.lock:
            if self.limits[name] is not None and self.counts[name] >= self.limits[name]:
                raise BudgetExceeded(f"budget exhausted for {name}")
            if name == "model_requests":
                if (self.limits["model_tokens"] is not None
                        and self.counts["model_tokens"] >= self.limits["model_tokens"]):
                    raise BudgetExceeded("model token budget is exhausted")
                if self.usd_spent >= self.usd_limit:
                    raise BudgetExceeded("model USD budget is exhausted")
            self.counts[name] += 1
            self._write_summary_locked()

    def admit_model(self, request_id: str) -> None:
        """Reserve shared credits until the upstream stream has fully drained.

        A reservation is an admission allowance, not a provider billing promise.
        Providers without enforceable per-call limits can exceed it. Actual
        settled usage always wins; incomplete usage stops further admissions.
        """
        with self.lock:
            if self.model_accounting_incomplete:
                raise BudgetExceeded("model accounting is incomplete")
            if request_id in self.model_inflight:
                raise BudgetExceeded("duplicate active request")
            if len(self.model_inflight) >= self.max_parallel_requests:
                raise BudgetExceeded("model concurrency limit reached; retry after active calls settle")
            available = self.usd_limit - self.usd_spent - sum(self.model_inflight.values())
            if available <= 0:
                raise BudgetExceeded("model credits are reserved or exhausted")
            self.reserve("model_requests")
            self.model_inflight[request_id] = min(available, self.request_reservation_usd)
            self._write_summary_locked()

    def finish_model(self, request_id: str, *, accounted: bool) -> None:
        with self.lock:
            self.model_inflight.pop(request_id, None)
            if not accounted:
                self.model_accounting_incomplete = True
            self._write_summary_locked()

    def add_model_tokens(self, total: int) -> None:
        with self.lock:
            self.counts["model_tokens"] += max(0, total)
            self._write_summary_locked()

    def add_model_usd(
        self,
        normalized_usd: float,
        billed_usd: float | None | object = _BILLED_AS_NORMALIZED,
    ) -> None:
        with self.lock:
            normalized = max(0.0, normalized_usd)
            self.usd_spent += normalized
            if billed_usd is _BILLED_AS_NORMALIZED:
                billed_usd = normalized
            if billed_usd is None:
                self.billed_usd_known = False
            else:
                self.billed_usd_spent += max(0.0, float(billed_usd))
            self._write_summary_locked()

    def add_model_usage(
        self,
        *,
        billed_tokens: int,
        normalized_usd: float,
        billed_usd: float | None | object = _BILLED_AS_NORMALIZED,
    ) -> None:
        """Persist one response's token and cost accounting atomically."""

        with self.lock:
            self.counts["model_tokens"] += max(0, billed_tokens)
            normalized = max(0.0, normalized_usd)
            self.usd_spent += normalized
            if billed_usd is _BILLED_AS_NORMALIZED:
                billed_usd = normalized
            if billed_usd is None:
                self.billed_usd_known = False
            else:
                self.billed_usd_spent += max(0.0, float(billed_usd))
            self._write_summary_locked()

    def record(self, stream: str, event: dict[str, Any]) -> None:
        kinds = {
            "model": "model.accounting",
            "web": "web.accounting",
        }
        if stream not in kinds:
            raise ValueError(f"unsupported canonical accounting stream: {stream}")
        payload = dict(event)
        request_id = payload.pop("request_id", None)
        event_id = payload.pop("event_id", None)
        self.emit(
            source="gateway",
            kind=kinds[stream],
            data=payload,
            request_id=str(request_id) if request_id else None,
            event_id=str(event_id) if event_id else None,
        )

    def append(self, stream: str, event: dict[str, Any]) -> None:
        kinds = {
            "web-rejections": "web.rejection",
        }
        if stream not in kinds:
            raise ValueError(f"unsupported canonical event stream: {stream}")
        payload = dict(event)
        request_id = payload.pop("request_id", None)
        event_id = payload.pop("event_id", None)
        self.emit(
            source="gateway",
            kind=kinds[stream],
            data=payload,
            request_id=str(request_id) if request_id else None,
            event_id=str(event_id) if event_id else None,
        )

    def timeline(self, event: dict[str, Any]) -> None:
        """Append one content-bearing event to the canonical stream."""

        payload = dict(event)
        kind = str(payload.pop("kind"))
        request_id = payload.pop("request_id", None)
        event_id = payload.pop("event_id", None)
        self.emit(
            source="gateway",
            kind=kind,
            data=payload,
            request_id=str(request_id) if request_id else None,
            event_id=str(event_id) if event_id else None,
        )

    def close(self) -> None:
        try:
            (self.directory / EVENT_TOKEN_FILENAME).unlink()
        except FileNotFoundError:
            pass
