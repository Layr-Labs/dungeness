"""Docker lifecycle for Harbor trials, scoped by their recorded project names.

No configuration lookup or CLI imports. Never prune shared images or unrelated
projects. Administrative cleanup and normal run teardown use the same operations.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def live_harbor_runs() -> list[str]:
    """Harbor processes executing on this machine right now."""

    try:
        result = subprocess.run(
            ["pgrep", "-fl", "harbor run"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def docker_query(arguments: list[str]) -> str | None:
    """Read from the Docker daemon, or None when it cannot be reached."""

    try:
        result = subprocess.run(
            ["docker", *arguments],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def docker_task_networks() -> list[str]:
    """Every per-run Harbor network currently held by the daemon."""

    listing = docker_query(["network", "ls", "--format", "{{.Name}}"])
    if listing is None:
        return []
    return [
        name
        for name in listing.split()
        if name.startswith("task__") and "__env" in name
    ]


def docker_network_capacity() -> int | None:
    """How many networks the daemon's address pools can hold.

    Returns None when the pools have been configured locally: the operator has
    already taken this into their own hands, so there is nothing to warn about.
    Docker's built-in defaults are 15 x /16 plus 16 x /20, hence 31.
    """

    pools = docker_query(
        ["info", "--format", "{{json .DefaultAddressPools}}"]
    )
    if pools is None or pools.strip() not in {"null", ""}:
        return None
    return 31


def check_docker_network_capacity() -> None:
    """Fail before rendering when compose could not allocate this run's networks.

    Each run needs two networks. Exhausting the pools produces a hundred-line
    docker traceback whose one useful line is buried at the end, so say plainly
    what is wrong and how to clear it.
    """

    capacity = docker_network_capacity()
    if capacity is None:
        return
    listing = docker_query(["network", "ls", "--format", "{{.Name}}"])
    if listing is None:
        return
    in_use = len(listing.split())
    if capacity - in_use >= 2:
        return
    leaked = len(docker_task_networks())
    raise SystemExit(
        f"Docker has {in_use} of {capacity} networks in use and this run "
        "needs 2.\n"
        f"{leaked} belong to previous Dungeness runs; remove them with "
        "./dungeness clean\n"
        "Raise the ceiling permanently by setting default-address-pools in "
        "~/.docker/daemon.json."
    )


def harbor_trials_for_run(run_dir: Path) -> list[str]:
    """The lowercase Harbor trial IDs recorded under one run."""

    harbor_root = run_dir / "harbor"
    if not harbor_root.is_dir():
        return []
    return sorted(
        {
            trial.name.lower()
            for trial in harbor_root.glob("*/task__*")
            if trial.is_dir()
        }
    )


def compose_projects_for_run(run_dir: Path) -> list[str]:
    """The environment projects Harbor created for a run."""

    return [f"{trial}__env" for trial in harbor_trials_for_run(run_dir)]


def docker_compose_images() -> list[tuple[str, str]]:
    """Return (image reference, compose project) for Compose-built images."""

    listing = docker_query(
        [
            "image",
            "ls",
            "--format",
            '{{.Repository}}:{{.Tag}}\t{{.Label "com.docker.compose.project"}}',
        ]
    )
    if listing is None:
        return []
    images: set[tuple[str, str]] = set()
    for line in listing.splitlines():
        fields = line.split("\t", 1)
        if len(fields) != 2:
            continue
        image, project = fields
        if not project or image.startswith("<none>:"):
            continue
        images.add((image, project))
    return sorted(images)


def docker_images_for_run(run_dir: Path) -> list[str]:
    """Every Compose-built image whose project belongs to this run's trials."""

    trials = harbor_trials_for_run(run_dir)
    if not trials:
        return []
    return sorted(
        {
            image
            for image, project in docker_compose_images()
            if any(
                project == trial or project.startswith(f"{trial}__")
                for trial in trials
            )
        }
    )


def docker_task_images() -> list[str]:
    """Every image built by a Harbor task Compose project."""

    return sorted(
        {
            image
            for image, project in docker_compose_images()
            if project.startswith("task__")
        }
    )


def remove_docker_images(images: list[str]) -> int:
    """Remove exact image tags without pruning shared or unrelated images."""

    removed = 0
    for image in sorted(set(images)):
        try:
            result = subprocess.run(
                ["docker", "image", "rm", image],
                capture_output=True,
                text=True,
                check=False,
                timeout=300,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            print(
                f">> warning: could not remove docker image {image}: {error}",
                file=sys.stderr,
                flush=True,
            )
            continue
        if result.returncode == 0:
            removed += 1
            continue
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        print(
            f">> warning: could not remove docker image {image}: "
            f"{detail[-1] if detail else 'unknown docker error'}",
            file=sys.stderr,
            flush=True,
        )
    return removed


def compose_down(project: str) -> bool:
    """Remove a compose project's containers and networks. True when removed."""

    try:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "--project-name",
                project,
                "down",
                "--volumes",
                "--remove-orphans",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        print(
            f">> warning: could not tear down {project}: {error}",
            file=sys.stderr,
            flush=True,
        )
        return False
    if result.returncode == 0:
        return True
    detail = (result.stderr or result.stdout or "").strip().splitlines()
    print(
        f">> warning: could not tear down {project}: "
        f"{detail[-1] if detail else 'unknown docker error'}",
        file=sys.stderr,
        flush=True,
    )
    return False


def teardown_run_environments(
    run_dir: Path,
    *,
    remove_images: bool = True,
) -> None:
    """Release a finished run's Docker containers, networks, and images.

    Harbor removes its own environment when a trial ends normally, but an
    interrupt aborts that cleanup mid-flight and leaks two networks per run.
    Docker's built-in address pools hold only 31 networks, so a handful of
    interrupted runs is enough to make every later run fail at compose time.
    Compose-built images are run-scoped and can consume several gigabytes each,
    so they are removed by default as well. Teardown is best-effort: it must
    never mask the run's own outcome.
    """

    for project in compose_projects_for_run(run_dir):
        if compose_down(project):
            print(f">> released docker environment {project}", flush=True)
    if remove_images:
        removed = remove_docker_images(docker_images_for_run(run_dir))
        if removed:
            print(f">> removed {removed} run docker image(s)", flush=True)
