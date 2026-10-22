"""Run-scoped Docker cleanup contracts, exercised without a daemon."""
import argparse
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dungeness.execution import environments

loader = SourceFileLoader("environment_cli", str(ROOT / "dungeness"))
cli = module_from_spec(spec_from_loader(loader.name, loader))
loader.exec_module(cli)


def stub_docker(networks: list[str], pools: str = "null"):
    """Answer environments.docker_query without a daemon."""

    def query(arguments: list[str]) -> str | None:
        if arguments[:2] == ["info", "--format"]:
            return pools + "\n"
        if arguments[:2] == ["network", "ls"]:
            return "\n".join(networks) + "\n"
        return ""

    return query



class DockerEnvironmentTests(unittest.TestCase):
    def test_compose_projects_derive_from_harbor_trial_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "harbor/job/task__9ZB7PhJ").mkdir(parents=True)
            (run_dir / "harbor/job/task__ABC1234").mkdir(parents=True)
            # Docker lowercases project names, so the derived name has to match
            # what compose actually created for the trial.
            self.assertEqual(
                environments.compose_projects_for_run(run_dir),
                ["task__9zb7phj__env", "task__abc1234__env"],
            )

    def test_teardown_is_a_noop_before_harbor_writes_a_trial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(environments.compose_projects_for_run(Path(directory)), [])

    def test_run_images_are_scoped_by_harbor_trial_project_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "harbor/job/task__9ZB7PhJ").mkdir(parents=True)
            listing = "\n".join(
                (
                    "task__9zb7phj__env-main:latest\t"
                    "task__9zb7phj__env",
                    "task__9zb7phj__verifier__trial-main:latest\t"
                    "task__9zb7phj__verifier__trial",
                    "task__other__env-main:latest\ttask__other__env",
                    "python:3.12-slim\t",
                )
            )
            with patch.object(environments, "docker_query", return_value=listing):
                self.assertEqual(
                    environments.docker_images_for_run(run_dir),
                    [
                        "task__9zb7phj__env-main:latest",
                        "task__9zb7phj__verifier__trial-main:latest",
                    ],
                )

    def test_teardown_removes_run_images_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "harbor/job/task__ABC1234").mkdir(parents=True)
            with (
                patch.object(environments, "compose_down", return_value=True),
                patch.object(
                    environments,
                    "docker_images_for_run",
                    return_value=["task__abc1234__env-main:latest"],
                ),
                patch.object(
                    environments,
                    "remove_docker_images",
                    return_value=1,
                ) as remove,
            ):
                environments.teardown_run_environments(run_dir)
            remove.assert_called_once_with(
                ["task__abc1234__env-main:latest"]
            )

    def test_teardown_can_retain_run_images(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "harbor/job/task__ABC1234").mkdir(parents=True)
            with (
                patch.object(environments, "compose_down", return_value=True),
                patch.object(environments, "remove_docker_images") as remove,
            ):
                environments.teardown_run_environments(
                    run_dir,
                    remove_images=False,
                )
            remove.assert_not_called()

    def test_run_refuses_to_start_without_room_for_two_networks(self) -> None:
        with patch.object(environments, "docker_query", stub_docker(["n"] * 30)):
            with self.assertRaisesRegex(SystemExit, "30 of 31 networks"):
                environments.check_docker_network_capacity()
        with patch.object(environments, "docker_query", stub_docker(["n"] * 29)):
            environments.check_docker_network_capacity()

    def test_capacity_message_counts_leaked_run_networks(self) -> None:
        networks = [
            f"task__x{index}__env_agent_internal" for index in range(28)
        ] + ["bridge", "host", "none"]
        with patch.object(environments, "docker_query", stub_docker(networks)):
            with self.assertRaisesRegex(SystemExit, "28 belong to previous"):
                environments.check_docker_network_capacity()

    def test_configured_address_pools_disable_the_capacity_check(self) -> None:
        with patch.object(
            environments,
            "docker_query",
            stub_docker(
                ["n"] * 500, pools='[{"base":"10.0.0.0/12","size":24}]'
            ),
        ):
            environments.check_docker_network_capacity()

    def test_unreachable_daemon_never_blocks_a_run(self) -> None:
        with patch.object(environments, "docker_query", lambda arguments: None):
            environments.check_docker_network_capacity()

    def test_clean_refuses_while_a_run_is_executing(self) -> None:
        with patch.object(
            environments, "live_harbor_runs", lambda: ["37009 harbor run --config x"]
        ):
            arguments = argparse.Namespace(yes=True, force=False)
            with self.assertRaisesRegex(SystemExit, "still executing"):
                cli.clean_environments(arguments)

    def test_clean_removes_leftover_run_images(self) -> None:
        arguments = argparse.Namespace(yes=True, force=False)
        images = ["task__old__env-main:latest"]
        with (
            patch.object(environments, "live_harbor_runs", return_value=[]),
            patch.object(environments, "docker_query", return_value=""),
            patch.object(environments, "docker_task_networks", return_value=[]),
            patch.object(environments, "docker_task_images", return_value=images),
            patch.object(
                environments,
                "remove_docker_images",
                return_value=1,
            ) as remove,
        ):
            self.assertEqual(cli.clean_environments(arguments), 0)
        remove.assert_called_once_with(images)
