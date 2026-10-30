"""Execute a compiled Harbor run and release its resources on every exit path.

The caller resolves configuration and provides record persistence callbacks.
This layer owns orchestration, not record schemas, CLI arguments or model policy.
"""
from __future__ import annotations

from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Protocol

from .timing import StartupTiming
from . import environments
from .credentials import gateway_credentials
from .harbor import harbor_launch_environment, launch_command, validate_command_job
from .process import stream_command, termination_as_interrupt


class StartRecord(Protocol):
    def __call__(
        self, rendered_path: Path, run_id: str, *, environment_file: str,
        keep_images: bool, control_plane_environment: dict[str, str],
        scrubbed_host_environment: list[str],
    ) -> Path: ...


class FinalizeRecord(Protocol):
    def __call__(self, record_path: Path, *, status: str, error: str | None) -> None: ...


def dispose_render(
    rendered_path: Path,
    run_id: str,
    run_dir: Path,
    *,
    keep: bool,
) -> Path | None:
    resolved_render = rendered_path.resolve()
    render_root = resolved_render.parent
    temporary_root = Path(tempfile.gettempdir()).resolve()
    if (
        resolved_render.name != "task"
        or render_root.parent != temporary_root
        or not render_root.name.startswith(f"dungeness-{run_id}-")
    ):
        raise RuntimeError(
            f"refusing to remove unexpected render path: {resolved_render}"
        )

    retained_path = None
    if keep:
        retained_path = run_dir / "debug" / "harbor-task"
        retained_path.parent.mkdir(parents=True, exist_ok=True)
        if retained_path.exists():
            raise RuntimeError(f"debug render already exists: {retained_path}")
        shutil.move(resolved_render, retained_path)
    shutil.rmtree(render_root, ignore_errors=True)
    return retained_path


@termination_as_interrupt()
def execute(
    *, repository_root: Path, render_command: list[str], run_id: str,
    run_dir: Path, environment_file: str, keep_render: bool, keep_images: bool,
    start_record: StartRecord, finalize_record: FinalizeRecord,
) -> int:
    """Render and execute one run; preserve failure/cancellation when finalizing."""
    environments.check_docker_network_capacity()

    rendered_path: Path | None = None
    record_path: Path | None = None
    final_status = "failed"
    failure: str | None = None
    credentials = ExitStack()
    timing = StartupTiming(run_dir / "startup.jsonl")
    try:
        print(">> rendering temporary run task", flush=True)
        timing.mark("render_started")
        rendered_text = stream_command(render_command, cwd=repository_root)
        rendered_path = Path(rendered_text)
        if not rendered_path.is_absolute():
            rendered_path = repository_root / rendered_path
        timing.mark("render_finished")
        timing.watch_containers(rendered_path)
        job_path = rendered_path / "harbor-job.yaml"
        if not job_path.is_file():
            raise RuntimeError(
                f"renderer did not produce a Harbor job at {job_path}"
            )
        validate_command_job(job_path)
        control_plane_env = {}
        environment, scrubbed_host_env = harbor_launch_environment(
            os.environ, control_plane_env, adapter_path=repository_root / "adapters/harbor"
        )
        record_path = start_record(
            rendered_path,
            run_id,
            environment_file=environment_file,
            keep_images=keep_images,
            control_plane_environment=control_plane_env,
            scrubbed_host_environment=scrubbed_host_env,
        )
        print(f">> recorded run {run_id}", flush=True)

        if scrubbed_host_env:
            print(
                ">> dropping host provider variables from the Harbor control plane: "
                + ", ".join(scrubbed_host_env),
                flush=True,
            )
        for key, value in control_plane_env.items():
            print(f">> exporting {key}={value} to the Harbor control plane", flush=True)
        print(f">> executing run from {job_path}", flush=True)
        environment, safe_env_file = credentials.enter_context(gateway_credentials(
            rendered_path, repository_root / environment_file, environment))
        timing.mark("harbor_started")
        stream_command(launch_command(job_path, safe_env_file), cwd=repository_root, env=environment)
        timing.mark("harbor_finished")
        final_status = "completed"
    except KeyboardInterrupt:
        final_status = "cancelled"
        failure = "interrupted"
        raise
    except BaseException as error:
        failure = f"{type(error).__name__}: {error}"
        raise
    finally:
        timing.close()
        cleanup_error: Exception | None = None
        try:
            environments.teardown_run_environments(run_dir, remove_images=not keep_images)
        except Exception as error:
            cleanup_error = error
            print(f">> warning: could not tear down run environments: {error}", file=sys.stderr)
        finally:
            try:
                credentials.close()
            except Exception as error:
                cleanup_error = cleanup_error or error
                print(f">> warning: could not remove staged credentials: {error}", file=sys.stderr)
        if record_path is not None:
            try:
                finalize_record(
                    record_path,
                    status=final_status,
                    error=failure,
                )
            except Exception as error:
                cleanup_error = cleanup_error or error
                print(f">> warning: could not finalize run record: {error}", file=sys.stderr)
        if rendered_path is not None:
            try:
                retained_path = dispose_render(rendered_path, run_id, run_dir, keep=keep_render)
                if retained_path is not None:
                    print(f">> retained render at {retained_path}", flush=True)
                print(">> removed temporary run task", flush=True)
            except Exception as error:
                cleanup_error = cleanup_error or error
                print(f">> warning: could not dispose run render: {error}", file=sys.stderr)
        events_path = run_dir / "usage" / "events.jsonl"
        timeline_path = run_dir / "usage" / "gateway-timeline.jsonl"
        audit_path = events_path if events_path.is_file() else timeline_path
        if audit_path.is_file():
            try:
                display_path = audit_path.relative_to(repository_root)
            except ValueError:
                display_path = audit_path
            print(
                f">> usage events at {display_path}",
                flush=True,
            )
        if failure is None and cleanup_error is not None:
            raise cleanup_error
    # Harbor can exit zero after recording a failed trial. The finalized record,
    # rather than the orchestration process, determines the run's outcome.
    if record_path is not None:
        data = json.loads(record_path.read_text())["data"]
        if data.get("status") != "completed":
            print(f">> run {data.get('status', 'failed')}; inspect {record_path}", file=sys.stderr)
            return 130 if data.get("status") == "cancelled" else 1
    return 0
