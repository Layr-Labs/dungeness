"""Run lifecycle regressions using synthetic renders and no container daemon."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dungeness.execution import process, runner

loader = SourceFileLoader("lifecycle_cli", str(ROOT / "dungeness"))
cli = module_from_spec(spec_from_loader(loader.name, loader))
loader.exec_module(cli)


class ExecutionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.run_id = "synthetic"
        self.run_dir = self.root / "runs/projects/test" / self.run_id
        self.render_root = Path(self.enterContext(
            tempfile.TemporaryDirectory(prefix=f"dungeness-{self.run_id}-")))
        self.render = self.render_root / "task"
        self.render.mkdir()
        (self.render / "environment").mkdir()
        (self.render / "environment/docker-compose.yaml").write_text(
            "services:\n  gateway:\n    x-dungeness-credential-env: {}\n")
        (self.root / "synthetic.env").write_text("")
        (self.render / "harbor-job.yaml").write_text(
            "agents:\n  - import_path: command_agent:CommandAgent\n    env: {}\n")
        (self.render / "resolved-run.json").write_text(json.dumps({
            "schema_version": 1, "type": "run", "namespace": "projects/test",
            "id": self.run_id, "data": {"run_id": self.run_id, "configuration": {}},
        }))
        self.enterContext(patch.object(cli, "REPO_ROOT", self.root))
        self.enterContext(patch.object(runner.environments, "check_docker_network_capacity"))
        self.teardown = self.enterContext(patch.object(runner.environments, "teardown_run_environments"))
        self.commands = self.enterContext(patch.object(
            runner, "stream_command", side_effect=[str(self.render), "completed"]))
        self.output = io.StringIO()
        self.enterContext(redirect_stdout(self.output))
        self.enterContext(redirect_stderr(self.output))
        # Avoid inheriting any real credential values in mocked launch calls.
        self.enterContext(patch.dict(os.environ, {"PATH": os.defpath}, clear=True))
        self.start = Mock(wraps=cli.start_run_record)
        self.finish = Mock(wraps=cli.finalize_run_record)

    def execute(self, **overrides):
        options = dict(
            repository_root=self.root, render_command=["synthetic-compiler"],
            run_id=self.run_id, run_dir=self.run_dir, environment_file="synthetic.env",
            keep_render=False, keep_images=False, start_record=self.start,
            finalize_record=self.finish,
        )
        return runner.execute(**{**options, **overrides})

    def record(self):
        return json.loads((self.run_dir / "record.json").read_text())["data"]

    def test_success_records_completion_and_releases_run_resources(self):
        self.assertEqual(self.execute(), 0)
        self.assertEqual(self.record()["status"], "completed")
        self.assertFalse(self.render_root.exists())
        self.teardown.assert_called_once_with(self.run_dir, remove_images=True)
        self.assertEqual(self.commands.call_args.kwargs["cwd"], self.root)
        self.assertEqual(self.commands.call_args.kwargs["env"]["PYTHONPATH"],
                         str(self.root / "adapters/harbor"))
        self.assertFalse(Path(self.commands.call_args.kwargs["env"]["DUNGENESS_CREDENTIALS_FILE"]).exists())

    def test_zero_harbor_exit_with_failed_trial_returns_failure(self):
        from dungeness.records import write_json
        write_json(self.run_dir / 'harbor' / self.run_id / 'result.json', {
            'stats': {'n_errored_trials': 1, 'evals': {'synthetic': {'exception_stats': {'RuntimeError': 1}}}}})
        self.assertEqual(self.execute(), 1)
        self.assertEqual(self.record()['status'], 'failed')
        self.assertIn('RuntimeError', self.record()['error'])

    def test_credentials_remain_until_container_teardown_then_are_removed(self):
        files = []
        def command(argv, **kwargs):
            if argv == ["synthetic-compiler"]:
                return str(self.render)
            files.append(Path(kwargs["env"]["DUNGENESS_CREDENTIALS_FILE"]))
            self.assertTrue(files[0].is_file())
            self.assertNotIn(str(self.root / "synthetic.env"), argv)
            return "completed"
        self.commands.side_effect = command
        self.teardown.side_effect = lambda *args, **kwargs: self.assertTrue(files[0].exists())
        self.execute()
        self.assertFalse(files[0].parent.exists())

    def test_credential_cleanup_error_does_not_skip_record_finalization(self):
        original = runner.gateway_credentials
        @contextmanager
        def failed_cleanup(*args):
            with original(*args) as staged:
                yield staged
            raise OSError("synthetic credential cleanup failure")
        with patch.object(runner, "gateway_credentials", failed_cleanup):
            with self.assertRaisesRegex(OSError, "credential cleanup failure"):
                self.execute()
        self.finish.assert_called_once()
        self.assertFalse(self.render_root.exists())

    def test_failed_launch_records_original_error_and_still_cleans(self):
        error = subprocess.CalledProcessError(7, ["synthetic-harbor"])
        self.commands.side_effect = [str(self.render), error]
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.execute()
        self.assertIs(caught.exception, error)
        self.assertEqual(self.record()["status"], "failed")
        self.assertIn("CalledProcessError", self.record()["error"])
        self.assertFalse(self.render_root.exists())
        self.teardown.assert_called_once()

    def test_cli_delegates_resolved_run_to_lifecycle(self):
        (self.root / "synthetic.env").write_text("")
        args = SimpleNamespace(namespace="projects/test", run_id=self.run_id,
                               env_file="synthetic.env", keep_render=True, keep_images=True)
        with patch.object(cli, "resolve_run_spec_arguments", return_value=args), patch.object(
            cli, "build_command", return_value=["synthetic-compiler"],
        ):
            self.assertEqual(cli.execute_run(args), 0)
        self.assertEqual(self.record()["status"], "completed")
        self.assertTrue((self.run_dir / "debug/harbor-task/harbor-job.yaml").is_file())
        self.teardown.assert_called_once_with(self.run_dir, remove_images=False)

    def test_cancellation_records_cancelled_and_preserves_interrupt(self):
        error = KeyboardInterrupt()
        self.commands.side_effect = [str(self.render), error]
        with self.assertRaises(KeyboardInterrupt) as caught:
            self.execute()
        self.assertIs(caught.exception, error)
        self.assertEqual(self.record()["status"], "cancelled")
        self.assertEqual(self.record()["error"], "interrupted")
        self.assertFalse(self.render_root.exists())
        self.teardown.assert_called_once()

    def test_renderer_failure_does_not_create_or_finalize_a_record(self):
        self.commands.side_effect = subprocess.CalledProcessError(2, ["synthetic-compiler"])
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute()
        self.start.assert_not_called()
        self.finish.assert_not_called()
        self.teardown.assert_called_once()

    def test_untrusted_host_adapter_is_rejected_before_record_or_launch(self):
        (self.render / "harbor-job.yaml").write_text(
            "agents:\n  - import_path: submitted:HostCode\n")
        with self.assertRaisesRegex(RuntimeError, "Only dungeness-command-v1"):
            self.execute()
        self.assertEqual(self.commands.call_count, 1)
        self.start.assert_not_called()
        self.assertFalse(self.render_root.exists())

    def test_retention_settings_keep_render_and_images(self):
        self.execute(keep_render=True, keep_images=True)
        self.assertTrue((self.run_dir / "debug/harbor-task/harbor-job.yaml").is_file())
        self.assertFalse(self.render_root.exists())
        self.teardown.assert_called_once_with(self.run_dir, remove_images=False)
        self.assertTrue(self.record()["configuration"]["launcher"]["keep_images"])

    def test_finalization_failure_still_disposes_render_and_is_reported(self):
        self.finish.side_effect = OSError("synthetic record write failure")
        with self.assertRaisesRegex(OSError, "record write failure"):
            self.execute()
        self.assertFalse(self.render_root.exists())
        self.teardown.assert_called_once()

    def test_teardown_failure_still_finalizes_record_and_disposes_render(self):
        self.teardown.side_effect = OSError("synthetic teardown failure")
        with self.assertRaisesRegex(OSError, "teardown failure"):
            self.execute()
        self.assertEqual(self.record()["status"], "completed")
        self.assertFalse(self.render_root.exists())

    def test_secondary_cleanup_errors_do_not_replace_run_failure(self):
        error = subprocess.CalledProcessError(7, ["synthetic-harbor"])
        self.commands.side_effect = [str(self.render), error]
        self.teardown.side_effect = OSError("synthetic teardown failure")
        self.finish.side_effect = OSError("synthetic record write failure")
        with patch.object(runner, "dispose_render", side_effect=OSError("synthetic removal failure")):
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                self.execute()
        self.assertIs(caught.exception, error)
        self.finish.assert_called_once()
        self.assertIn("could not dispose run render", self.output.getvalue())

    def test_render_disposal_refuses_paths_outside_run_temporary_directory(self):
        unrelated = self.root / "task"
        unrelated.mkdir()
        with self.assertRaisesRegex(RuntimeError, "refusing to remove"):
            runner.dispose_render(unrelated, self.run_id, self.run_dir, keep=False)
        self.assertTrue(unrelated.is_dir())


class ProcessTests(unittest.TestCase):
    def test_real_child_uses_explicit_directory_and_environment(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            result = process.stream_command(
                [sys.executable, "-c",
                 "import os, sys; assert os.getcwd() == sys.argv[1]; print(os.environ['SYNTHETIC_VALUE'])",
                 directory],
                cwd=Path(directory), env={"SYNTHETIC_VALUE": "last nonempty line"},
            )
        self.assertEqual(result, "last nonempty line")

    def test_real_child_failure_preserves_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                process.stream_command([sys.executable, "-c", "raise SystemExit(7)"],
                                       cwd=Path(directory))
        self.assertEqual(caught.exception.returncode, 7)

    def test_interruption_reaps_real_child_before_returning_to_cleanup(self):
        children = []
        original = subprocess.Popen

        def spawn(*args, **kwargs):
            child = original(*args, **kwargs)
            children.append(child)
            return child

        with tempfile.TemporaryDirectory() as directory, patch.object(
            process.subprocess, "Popen", side_effect=spawn,
        ), patch.object(process, "print", side_effect=KeyboardInterrupt(), create=True):
            with self.assertRaises(KeyboardInterrupt):
                process.stream_command(
                    [sys.executable, "-c", "import time; print('ready', flush=True); time.sleep(30)"],
                    cwd=Path(directory),
                )
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)

    def test_unresponsive_child_is_killed_after_termination_deadline(self):
        child = Mock()
        child.stdout = io.StringIO("ready\n")
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired("synthetic", 10), 0]
        with patch.object(process.subprocess, "Popen", return_value=child), patch.object(
            process, "print", side_effect=KeyboardInterrupt(), create=True,
        ):
            with self.assertRaises(KeyboardInterrupt):
                process.stream_command(["synthetic"], cwd=ROOT)
        child.terminate.assert_called_once()
        child.kill.assert_called_once()
        self.assertTrue(child.stdout.closed)


if __name__ == "__main__":
    unittest.main()
