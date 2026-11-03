"""Harbor execution boundary: rendering, invocation and result interpretation.

Inputs are already validated by Dungeness. This module does not read run specs,
choose model policy, import submitted code, or import the Harbor SDK. The trusted
SDK-dependent CommandAgent stays at adapters/harbor for its stable import path.
"""
from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

HARBOR_VERSION = "0.18.0"
LITELLM_VERSION = "1.88.6"

# Preserve the existing control-plane credential filtering policy. Credential
# selection and model request authentication belong to the gateway, not Harbor.
HOST_ENV_SCRUB_PREFIXES = ("ANTHROPIC_", "CLAUDE_", "CLAUDECODE", "AWS_")
HOST_ENV_SCRUB_KEYS = frozenset({"MAX_THINKING_TOKENS", "DISABLE_PROMPT_CACHING"})


def build_job(
    *, run_id: str, task_path: Path, run_dir: Path,
    execution: dict[str, Any], models: list[dict[str, Any]],
    task_input: dict[str, Any], continuation: dict[str, int] | None = None,
) -> str:
    """Render one trial from validated execution inputs; no repository globals."""
    if continuation and continuation.get("max_resumes", 0) and not execution.get("resume_entrypoint"):
        raise ValueError("command continuation requires execution.resume_entrypoint")
    kwargs = {"execution": execution, "models": models, "task_input": task_input}
    if continuation:
        kwargs.update({f"continuation_{key}": value for key, value in continuation.items()})
    return yaml.safe_dump({
        "job_name": run_id, "jobs_dir": str((run_dir / "harbor").resolve()),
        "n_attempts": 1, "n_concurrent_trials": 1,
        "agents": [{"import_path": "command_agent:CommandAgent",
                    "model_name": models[0]["request_model"], "kwargs": kwargs,
                    "env": {}}],
        "tasks": [{"path": str(task_path.resolve())}],
    }, sort_keys=False)


def launch_command(job_path: Path, env_file: Path | str) -> list[str]:
    """Build argv for the pinned execution framework; never invoke a shell."""
    return [
        "uvx", "--python", "3.12", "--from", f"harbor=={HARBOR_VERSION}",
        "--with", f"litellm=={LITELLM_VERSION}", "harbor", "run",
        "--env-file", str(env_file), "--config", str(job_path),
    ]


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def build_task_toml(
    task_id: str,
    namespace: str,
    baseline_commit: str,
    evaluator_commit: str,
    candidate_paths: list[PurePosixPath],
    agent_id: str | None,
    description: str,
    keywords: list[str],
    agent_res: dict[str, int],
    verifier_res: dict[str, int],
    resume_meta: dict[str, Any] | None = None,
    checkpoint_meta: dict[str, Any] | None = None,
    web_cutoff: str | None = None,
    labels: dict[str, str] | None = None,
    *, workspace_root: str = "/workspace/repo",
) -> str:
    artifact_lines = ",\n  ".join(
        toml_string(f"{workspace_root}/{path.as_posix()}")
        for path in candidate_paths
    )
    keyword_line = ", ".join(toml_string(k) for k in keywords)
    # Resume lineage: record where a warm-started run's workspace came from, so
    # the provenance is machine-auditable from the job config (not only implicit
    # in the seeded files). Absent for fresh runs.
    resume_lines = ""
    if resume_meta is not None:
        resume_lines = f"\nresumed_from = {toml_string(resume_meta['run_id'])}"
        best = resume_meta.get("best_score")
        if isinstance(best, (int, float)) and not isinstance(best, bool):
            resume_lines += f"\nresumed_best_score = {best!r}"
        shas = resume_meta.get("candidate_sha256") or {}
        if len(shas) == 1:
            resume_lines += (
                f"\nresumed_candidate_sha256 = {toml_string(next(iter(shas.values())))}"
            )
        elif shas:
            inline = ", ".join(
                f"{toml_string(k)} = {toml_string(v)}" for k, v in sorted(shas.items())
            )
            resume_lines += f"\nresumed_candidate_sha256 = {{ {inline} }}"
    # Public sample provenance and whether the candidate was kept or blanked.
    checkpoint_lines = ""
    if checkpoint_meta is not None:
        checkpoint_lines = (
            f"\ncheckpoint = {toml_string(checkpoint_meta['id'])}"
            f"\ninitialization = {toml_string(checkpoint_meta['initialization'])}"
        )
    cutoff_line = (
        f"\nweb_cutoff = {toml_string(web_cutoff)}" if web_cutoff is not None else ""
    )
    # k8s-style run labels: key=value organizing metadata, its own [metadata.labels]
    # table so runs are filterable without touching universal record fields.
    labels_block = ""
    if labels:
        labels_block = "\n\n[metadata.labels]\n" + "".join(
            f"{toml_string(k)} = {toml_string(v)}\n" for k, v in sorted(labels.items())
        )
    return f'''schema_version = "1.3"
artifacts = [
  {artifact_lines},
]

[task]
name = {toml_string(f"research-testbed/{task_id}")}
description = {toml_string(description)}
keywords = [{keyword_line}]

[metadata]
type = "run"
namespace = {toml_string(namespace)}
task_id = {toml_string(task_id)}
start_commit = {toml_string(baseline_commit)}
evaluator_commit = {toml_string(evaluator_commit)}
agent_network = "gateway-mediated"
agent = {toml_string(agent_id or "unspecified")}{cutoff_line}{checkpoint_lines}{resume_lines}{labels_block}

[agent]
timeout_sec = {agent_res["timeout_sec"]}

[environment]
build_timeout_sec = {agent_res["build_timeout_sec"]}
# The Compose file applies the stricter per-service boundary: main is internal
# only, while the gateway alone joins the egress network.
network_mode = "public"
cpus = {agent_res["cpus"]}
memory_mb = {agent_res["memory_mb"]}
storage_mb = {agent_res["storage_mb"]}

[verifier]
timeout_sec = {verifier_res["timeout_sec"]}
environment_mode = "separate"

[verifier.environment]
build_timeout_sec = {verifier_res["build_timeout_sec"]}
# The verifier's generated Compose file applies `network_mode: none`.
# Harbor's Docker network-policy sidecar is unavailable on some Docker Desktop
# kernels, so keep its baseline public and enforce isolation at the service.
network_mode = "public"
cpus = {verifier_res["cpus"]}
memory_mb = {verifier_res["memory_mb"]}
storage_mb = {verifier_res["storage_mb"]}
'''


def build_verifier_compose() -> str:
    return """services:
  main:
    network_mode: none
"""


def harbor_result_outcome(
    harbor_result: dict[str, object],
) -> tuple[str | None, str | None]:
    stats = harbor_result.get("stats")
    if not isinstance(stats, dict):
        return None, None

    errored = stats.get("n_errored_trials", 0)
    cancelled = stats.get("n_cancelled_trials", 0)
    running = stats.get("n_running_trials", 0)
    pending = stats.get("n_pending_trials", 0)

    if isinstance(errored, int) and not isinstance(errored, bool) and errored > 0:
        exception_types: set[str] = set()
        evals = stats.get("evals")
        if isinstance(evals, dict):
            for evaluation in evals.values():
                if not isinstance(evaluation, dict):
                    continue
                exception_stats = evaluation.get("exception_stats")
                if isinstance(exception_stats, dict):
                    exception_types.update(
                        key for key in exception_stats if isinstance(key, str)
                    )
        detail = (
            f": {', '.join(sorted(exception_types))}" if exception_types else ""
        )
        noun = "trial" if errored == 1 else "trials"
        return "failed", f"Harbor reported {errored} errored {noun}{detail}"

    if (
        isinstance(cancelled, int)
        and not isinstance(cancelled, bool)
        and cancelled > 0
    ):
        return "cancelled", f"Harbor reported {cancelled} cancelled trial(s)"

    unfinished = sum(
        value
        for value in (running, pending)
        if isinstance(value, int) and not isinstance(value, bool) and value > 0
    )
    if unfinished:
        return "failed", f"Harbor exited with {unfinished} unfinished trial(s)"

    return None, None


def validate_command_job(job_path: Path) -> None:
    """Only the trusted command adapter may execute a submitted harness."""
    job = yaml.safe_load(job_path.read_text(encoding="utf-8"))
    agents = job.get("agents") if isinstance(job, dict) else None
    if (not isinstance(agents, list) or len(agents) != 1
            or agents[0].get("import_path") != "command_agent:CommandAgent"
            or "name" in agents[0] or agents[0].get("env")):
        raise RuntimeError("Only dungeness-command-v1 jobs are supported; rebuild the harness job.")


def harbor_launch_environment(
    base: Mapping[str, str],
    control_plane_environment: Mapping[str, str],
    *, adapter_path: Path | None = None,
) -> tuple[dict[str, str], list[str]]:
    """Return (env for `harbor run`, names of host variables that were dropped)."""

    scrubbed = sorted(
        key
        for key in base
        if key.startswith(HOST_ENV_SCRUB_PREFIXES) or key in HOST_ENV_SCRUB_KEYS
    )
    environment = {key: value for key, value in base.items() if key not in scrubbed}
    environment.update(control_plane_environment)
    if adapter_path is not None:
        existing = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = str(adapter_path) + (os.pathsep + existing if existing else "")
    return environment, scrubbed
