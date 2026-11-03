"""Persist run records and capture source provenance without loading execution.

Callers supply the run storage root, launcher metadata and result interpreter.
Historical evidence is read for compatibility; no services or containers start here.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
import uuid

NAMESPACE_RE = re.compile(r"[a-z0-9][a-z0-9._-]*(?:/[a-z0-9][a-z0-9._-]*)*")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def require_namespace(value: object, field: str = "namespace") -> str:
    if not isinstance(value, str) or not NAMESPACE_RE.fullmatch(value):
        raise SystemExit(
            f"{field} must be slash-separated lowercase namespace segments: {value!r}"
        )
    return value


def read_json(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object in {path}")
    return value


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def repository_provenance(repository_root: Path) -> dict[str, object]:
    """Describe the exact Dungeness Git state used to launch a run."""

    def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
        environment = os.environ.copy()
        environment["GIT_OPTIONAL_LOCKS"] = "0"
        return subprocess.run(
            ["git", "-C", str(repository_root), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=environment,
        )

    head = git("rev-parse", "--verify", "HEAD")
    if head.returncode != 0:
        error = head.stderr.decode("utf-8", errors="replace").strip()
        return {
            "vcs": "git",
            "root": ".",
            "available": False,
            "reproducible_from_commit": False,
            "error": error[:1000] or "could not resolve Git HEAD",
        }

    commit = head.stdout.decode("ascii", errors="replace").strip()
    branch_result = git("symbolic-ref", "--quiet", "--short", "HEAD")
    branch = (
        branch_result.stdout.decode("utf-8", errors="replace").strip()
        if branch_result.returncode == 0
        else None
    )

    status = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    tracked_diff = git("diff", "--binary", "--no-ext-diff", "HEAD", "--")
    tracked_names = git("diff", "--name-only", "-z", "HEAD", "--")
    untracked_names = git("ls-files", "--others", "--exclude-standard", "-z")
    capture_results = {
        "status": status,
        "tracked_diff": tracked_diff,
        "tracked_names": tracked_names,
        "untracked_names": untracked_names,
    }
    errors = {
        name: result.stderr.decode("utf-8", errors="replace").strip()[:1000]
        for name, result in capture_results.items()
        if result.returncode != 0
    }
    capture_complete = not errors
    dirty = bool(status.stdout) if status.returncode == 0 else None

    tracked_files = (
        sorted(
            os.fsdecode(value)
            for value in tracked_names.stdout.split(b"\0")
            if value
        )
        if tracked_names.returncode == 0
        else []
    )
    untracked_files: list[dict[str, object]] = []
    if untracked_names.returncode == 0:
        for raw_path in untracked_names.stdout.split(b"\0"):
            if not raw_path:
                continue
            relative = os.fsdecode(raw_path)
            path = repository_root / relative
            entry: dict[str, object] = {"path": relative}
            try:
                if path.is_symlink():
                    target = os.readlink(path)
                    encoded_target = os.fsencode(target)
                    entry.update(
                        {
                            "kind": "symlink",
                            "size_bytes": len(encoded_target),
                            "sha256": hashlib.sha256(encoded_target).hexdigest(),
                        }
                    )
                elif path.is_file():
                    digest = hashlib.sha256()
                    with path.open("rb") as source:
                        for chunk in iter(lambda: source.read(1024 * 1024), b""):
                            digest.update(chunk)
                    entry.update(
                        {
                            "kind": "file",
                            "size_bytes": path.stat().st_size,
                            "sha256": digest.hexdigest(),
                        }
                    )
                else:
                    entry["kind"] = "other"
            except OSError as error:
                entry.update({"kind": "unreadable", "error": str(error)[:1000]})
            untracked_files.append(entry)

    result: dict[str, object] = {
        "vcs": "git",
        "root": ".",
        "available": True,
        "commit": commit,
        "branch": branch,
        "capture_complete": capture_complete,
        "dirty": dirty,
        "reproducible_from_commit": capture_complete and dirty is False,
        "status_sha256": (
            hashlib.sha256(status.stdout).hexdigest()
            if status.returncode == 0
            else None
        ),
        "tracked_diff_sha256": (
            hashlib.sha256(tracked_diff.stdout).hexdigest()
            if tracked_diff.returncode == 0 and tracked_diff.stdout
            else None
        ),
        "tracked_diff_bytes": (
            len(tracked_diff.stdout) if tracked_diff.returncode == 0 else None
        ),
        "tracked_files": tracked_files,
        "untracked_files": untracked_files,
    }
    if errors:
        result["capture_errors"] = errors
    return result


def start_run_record(
    rendered_path: Path,
    run_id: str,
    *,
    runs_root: Path,
    repository: dict[str, object],
    launcher: dict[str, object],
) -> Path:
    source = rendered_path / "resolved-run.json"
    record = read_json(source)
    if record is None:
        raise RuntimeError(f"renderer did not produce a resolved run record at {source}")
    data = record.get("data")
    if not isinstance(data, dict) or data.get("run_id") != run_id:
        raise RuntimeError(f"resolved run record identity mismatch in {source}")
    namespace = record.get("namespace")
    if not isinstance(namespace, str):
        raise RuntimeError(f"resolved run record has no namespace in {source}")
    started_at = utc_now()
    record["created_at"] = started_at
    data["status"] = "running"
    data["started_at"] = started_at
    configuration = data.get("configuration")
    if isinstance(configuration, dict):
        configuration["repository"] = repository
        configuration["launcher"] = launcher
        if repository.get("available") is not True:
            print(
                ">> warning: Dungeness Git provenance could not be captured; "
                "this run is not reproducible from a recorded framework commit",
                file=sys.stderr,
            )
        elif repository.get("dirty") is True:
            print(
                ">> warning: Dungeness worktree is dirty; the run records the "
                "HEAD commit and change fingerprints, but exact reproduction "
                "requires preserving the uncommitted changes",
                file=sys.stderr,
            )
    record_path = runs_root.joinpath(
        *require_namespace(namespace, "run namespace").split("/"), run_id, "record.json"
    )
    write_json(record_path, record)
    return record_path


def finalize_run_record(
    record_path: Path,
    *,
    status: str,
    execution_outcome: Callable[[dict[str, object]], tuple[str | None, str | None]],
    error: str | None = None,
) -> None:
    record = read_json(record_path)
    if record is None:
        raise RuntimeError(f"run record disappeared: {record_path}")
    data = record.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"run record has no data object: {record_path}")
    run_id = data.get("run_id")
    if not isinstance(run_id, str):
        raise RuntimeError(f"run record has no run id: {record_path}")
    run_dir = record_path.parent

    finished_at = utc_now()
    record["published_at"] = finished_at
    data["finished_at"] = finished_at

    usage_summary = read_json(run_dir / "usage" / "summary.json")
    if usage_summary is not None and isinstance(usage_summary.get("usage"), dict):
        data["usage"] = usage_summary["usage"]

    evaluation_summary: dict[str, Any] = {}
    if usage_summary is not None and isinstance(
        usage_summary.get("evaluation"),
        dict,
    ):
        evaluation_summary.update(usage_summary["evaluation"])
    events_path = run_dir / "usage" / "events.jsonl"
    if events_path.is_file():
        try:
            event_file = events_path.open(encoding="utf-8")
        except OSError:
            event_file = None
        if event_file is not None:
            with event_file:
                for line in event_file:
                    if "evaluation.completed" not in line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if (
                        not isinstance(event, dict)
                        or event.get("source") != "evaluator"
                        or event.get("kind") != "evaluation.completed"
                    ):
                        continue
                    event_data = event.get("data")
                    if not isinstance(event_data, dict):
                        continue
                    for key in (
                        "submissions_used",
                        "submissions_limit",
                        "best_score",
                    ):
                        if key in event_data:
                            evaluation_summary[key] = event_data[key]
    if not evaluation_summary:
        legacy_evaluation = read_json(run_dir / "usage" / "eval-summary.json")
        if legacy_evaluation is not None:
            evaluation_summary.update(
                {
                    key: value
                    for key, value in legacy_evaluation.items()
                    if key != "run_id"
                }
            )
    if evaluation_summary:
        data["evaluation"] = evaluation_summary
        best_score = evaluation_summary.get("best_score")
        metric = data.get("metric")
        if (
            isinstance(best_score, (int, float))
            and not isinstance(best_score, bool)
            and isinstance(metric, dict)
            and isinstance(metric.get("name"), str)
        ):
            data["metrics"] = {metric["name"]: best_score}

    # Read-only compatibility for retained historical runs; no controller is launched.
    research_state_summary = read_json(
        run_dir / "usage" / "research-state-summary.json"
    )
    if research_state_summary is not None:
        data["research_state"] = {
            key: value
            for key, value in research_state_summary.items()
            if key != "run_id"
        }

    harbor_result = read_json(run_dir / "harbor" / run_id / "result.json")
    if harbor_result is not None:
        data["execution"] = {
            key: harbor_result[key]
            for key in (
                "id",
                "started_at",
                "updated_at",
                "finished_at",
                "n_total_trials",
                "stats",
            )
            if key in harbor_result
        }
        if status == "completed":
            harbor_status, harbor_error = execution_outcome(harbor_result)
            if harbor_status is not None:
                status = harbor_status
                error = error or harbor_error

    data["status"] = status
    if error is not None:
        data["error"] = error
    write_json(record_path, record)

