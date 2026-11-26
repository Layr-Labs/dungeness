"""Exercise loop failures without a Docker daemon or a provider."""
from contextlib import nullcontext, redirect_stderr
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


REPOSITORY = Path(__file__).resolve().parents[1]


class RuntimeVerificationTests(unittest.TestCase):
    def setUp(self):
        with patch.object(sys, "path", sys.path.copy()):
            self.loop = runpy.run_path(REPOSITORY / "script/verify-runtime.py")["main"].__globals__
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.logs = self.root / ".verify/test"
        self.logs.mkdir(parents=True)
        self.loop.update(ROOT=self.root, OUTPUT=self.logs.parent)
        self.evidence = {"mode": "test", "commands": [], "cleanup_errors": [], "faults": []}

    def test_timeout_preserves_redacted_output_and_primary_error(self):
        canary = self.loop["CANARY_BYTES"]
        timeout = subprocess.TimeoutExpired(["fixture"], 1)

        def run(_argv, _cwd, _env, output, _stderr):
            output.write(b"before timeout: " + canary)
            raise timeout

        with patch.dict(self.loop, command=run), self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.loop["record_command"](self.evidence, "timeout", ["fixture"], self.root, {}, check_canary=True)

        self.assertIs(caught.exception, timeout)
        log = (self.logs / "timeout.log").read_bytes()
        self.assertIn(b"before timeout: [synthetic credential redacted]", log)
        self.assertNotIn(canary, log)
        self.assertEqual(self.evidence["commands"][0]["assertion"], self.loop["OUTPUT_LEAK"])

    def test_route_check_reads_stdout_and_rejects_unexpected_routes(self):
        document = {
            "providers": sorted(self.loop["ROUTES"]),
            "access_policy": {"schema_version": 1, "sha256": self.loop["EXPECTED_POLICY_SHA256"]},
        }
        record_command = self.loop["record_command"]

        def report(evidence, name, argv, cwd, env, **kwargs):
            self.assertEqual(argv[:4], ["uv", "run", "--isolated", "--locked"])
            return record_command(evidence, name, [
                sys.executable, "-c",
                "import sys; print(sys.argv[1]); print('uv warning', file=sys.stderr)",
                json.dumps(document),
            ], cwd, env, **kwargs)

        with patch.dict(self.loop, record_command=report):
            self.assertEqual(self.loop["route_check"](REPOSITORY, self.evidence, "routes", None)[0], 0)
            document["providers"].append("unexpected")
            code, reason = self.loop["route_check"](REPOSITORY, self.evidence, "extra-route", None)
            self.assertEqual(code, 1)
            self.assertIn("unexpected registered route", reason)
            document["providers"].remove("unexpected")
            document["access_policy"]["sha256"] = "0" * 64
            code, reason = self.loop["route_check"](REPOSITORY, self.evidence, "digest", None)
            self.assertEqual(code, 1)
            self.assertIn("public policy digest does not match", reason)

        self.assertIn("uv warning", (self.logs / "routes.log").read_text())
        self.assertIn("unexpected registered route", (self.logs / "extra-route.log").read_text())

    def test_failed_fault_preserves_baseline_and_runs_the_next_fault(self):
        baseline = {"score": 42}
        self.evidence.update(scored_run=baseline)
        verification_error = self.loop["VerificationError"]

        def fail_route(*_arguments):
            raise verification_error("Cannot parse route report: route assertion")

        def scored(_root, _base, _stock, evidence, _name, _env):
            evidence["scored_run"] = {"score": 0}
            return 1, "retry assertion"

        with patch.dict(self.loop, FAULTS={"missing-route": "route assertion", "lost-retry-flag": "retry assertion"},
                        scratch=lambda *args: nullcontext(self.root), seed=lambda *args: None,
                        route_check=fail_route, scored_run=scored):
            with self.assertRaisesRegex(AssertionError, "A fault survived or failed"):
                self.loop["proof"](self.evidence, "", "", {})

        self.assertIs(self.evidence["scored_run"], baseline)
        self.assertEqual([fault["status"] for fault in self.evidence["faults"]], ["failed", "detected"])
        self.assertEqual(self.evidence["faults"][0]["error"], "Cannot parse route report: route assertion")
        self.assertNotIn("error", self.evidence["faults"][1])

    def test_scored_timeout_checks_staging_and_tears_down_both_recorded_projects(self):
        root = self.root / "repo"
        root.mkdir()
        self.evidence["docker_bind_owner"] = f"{os.geteuid()}:{os.getegid()}"
        timeout = subprocess.TimeoutExpired(["fixture"], 1)
        docker_commands = []
        verifier_image = "task__harborid__verifier__trial-main:latest"
        image_removed = False

        def run(argv, _cwd, env, _output, _stderr):
            self.assertEqual(argv[:4], ["uv", "run", "--isolated", "--locked"])
            run_id = argv[-1]
            (root / "runs/users/verify" / run_id / "harbor/job/task__HarborID").mkdir(parents=True)
            temp = Path(env["TMPDIR"])
            (temp / "dungeness-credentials-fixture").mkdir()
            (temp / f"dungeness-{run_id}-fixture").mkdir()
            (temp / "unrelated").mkdir()
            raise timeout

        def docker(argv, **_kwargs):
            nonlocal image_removed
            argv = list(argv)
            docker_commands.append(argv)
            if argv[:2] == ["docker", "compose"]:
                return subprocess.CompletedProcess(argv, int("__verifier__" in argv[3]), "", "fixture error")
            if argv[:3] == ["docker", "image", "rm"]:
                self.assertEqual(argv[3:], ["--no-prune", verifier_image])
                image_removed = True
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "--format" in argv:
                self.assertIn(argv[5], {
                    "reference=task__harborid__env-main:latest",
                    f"reference={verifier_image}",
                })
                stdout = f"sha256:fixture {verifier_image}" if argv[5] == f"reference={verifier_image}" and not image_removed else ""
                return subprocess.CompletedProcess(argv, 0, stdout, "")
            self.assertIn(argv[-1], {
                "label=com.docker.compose.project=task__harborid__env",
                "label=com.docker.compose.project=task__harborid__verifier__trial",
            })
            return subprocess.CompletedProcess(argv, 0, "", "")

        with patch.dict(self.loop, stage_gateway=lambda *args, **kwargs: None,
                        stage_run=lambda *args: ("spec", "fixture"), command=run), \
             patch.object(subprocess, "run", side_effect=docker), redirect_stderr(io.StringIO()), \
             self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.loop["scored_run"](root, None, None, self.evidence, "timeout", {})

        self.assertIs(caught.exception, timeout)
        self.assertEqual([argv[3] for argv in docker_commands if argv[:2] == ["docker", "compose"]],
                         ["task__harborid__env", "task__harborid__verifier__trial"])
        self.assertTrue(image_removed)
        staging, leaked_image, teardown = self.evidence["cleanup_errors"]
        self.assertIn("dungeness-credentials-fixture", staging)
        self.assertRegex(staging, r"dungeness-runtime-verify-[a-f0-9]+-fixture")
        self.assertNotIn("unrelated", staging)
        self.assertIn(verifier_image, leaked_image)
        self.assertIn("Could not tear down scored run project task__harborid__verifier__trial", teardown)

    def test_docker_host_takes_precedence_over_context(self):
        stock = self.root / "stock_adapter.py"
        stock.touch()
        with patch.dict(os.environ, DUNGENESS_VERIFY_UV_CACHE=str(self.root),
                        DUNGENESS_VERIFY_STOCK_ADAPTER=str(stock),
                        DUNGENESS_VERIFY_IMAGE="sha256:" + "0" * 64), \
             patch.dict(self.loop, sha256=lambda _: self.loop["STOCK_SHA256"], capture=Mock()) as loop:
            with self.assertRaisesRegex(self.loop["VerificationError"], "local Docker Unix socket"):
                self.loop["inputs"]({"DOCKER_HOST": "tcp://127.0.0.1:1", "DOCKER_CONTEXT": "local"})
            loop["capture"].assert_not_called()

    def test_artifact_scan_ignores_symlinks_and_fifos(self):
        artifacts = self.root / "artifacts"
        artifacts.mkdir()
        outside = self.root / "outside"
        outside.write_bytes(self.loop["CANARY_BYTES"])
        (artifacts / "outside").symlink_to(outside)
        (artifacts / "broken").symlink_to(self.root / "missing")
        os.mkfifo(artifacts / "pipe")
        self.assertIsNone(self.loop["find_artifact_leak"](artifacts))
        (artifacts / "regular").write_bytes(self.loop["CANARY_BYTES"])
        self.assertIn("regular", self.loop["find_artifact_leak"](artifacts))

    def test_capture_preserves_redacted_stderr(self):
        with self.assertRaisesRegex(self.loop["VerificationError"], r"fixture \[synthetic credential redacted\]"):
            self.loop["capture"](sys.executable, "-c",
                                 "import sys; sys.exit('fixture ' + sys.argv[1])", self.loop["CANARY"])

    def test_gateway_staging_rejects_changed_workdir(self):
        gateway = self.root / "services/gateway"
        gateway.mkdir(parents=True)
        original = (REPOSITORY / "services/gateway/Dockerfile").read_text()
        (gateway / "Dockerfile").write_text(original.replace("WORKDIR /app", "WORKDIR /changed"))
        with self.assertRaisesRegex(self.loop["VerificationError"], "substitution no longer matches Dockerfile"):
            self.loop["stage_gateway"](self.root, "base", {})

    def test_baseline_rejects_an_empty_unittest_suite(self):
        with patch.dict(self.loop, checked=lambda *_: "Ran 3 tests in 1s\nRan 0 tests in 0s\n"):
            with self.assertRaisesRegex(AssertionError, "suite ran no tests"):
                self.loop["baseline"](self.evidence, None, None, {})

    def test_scored_record_matches_harbor_and_gateway(self):
        self.evidence.update(commit="runtime", pins={"harbor": "harbor", "litellm": "litellm"})
        run_id = "run"
        harbor = self.root / "harbor" / run_id
        trial = harbor / "task__trial"
        trial.mkdir(parents=True)
        trial_result = trial / "result.json"
        trial_result.write_text(json.dumps({"verifier_result": {"rewards": {"sample_score": 42}}}))
        stats = dict(n_completed_trials=1, n_errored_trials=0, n_cancelled_trials=0, n_running_trials=0,
                     n_pending_trials=0, evals={"fixture": {"reward_stats": {"sample_score": {"42": [trial.name]}}}})
        outcome = {"n_total_trials": 1, "stats": stats}
        (harbor / "result.json").write_text(json.dumps(outcome))
        usage = {"model_requests": 2, "model_tokens": 2056, "normalized_usd": 0.01044,
                 "model_accounting_state": "settled"}
        usage_dir = self.root / "usage"
        usage_dir.mkdir()
        (usage_dir / "summary.json").write_text(json.dumps({"run_id": run_id, "usage": usage}))
        (usage_dir / "fixture-provider.jsonl").write_text("{}\n{}\n")
        events = [
            {"kind": "gateway.http_request_completed", "data": {"route": "/model/fixture"}},
            {"kind": "gateway.http_request_completed", "data": {
                "route": "/model/fixture", "code": "model_budget_exhausted"}},
        ]
        (usage_dir / "events.jsonl").write_text("\n".join(json.dumps(event) for event in [events[0], *events]))
        record = {
            "status": "completed", "usage": usage, "execution": outcome,
            "configuration": {"repository": {"commit": "runtime"},
                              "launcher": {"harbor_version": "harbor", "litellm_version": "litellm"}},
            "checkpoint": {"repository": {"commit": "fixture"}},
            "task": {"evaluator": {"commit": "fixture"}},
        }

        def read(data):
            (self.root / "record.json").write_text(json.dumps({"data": data}))
            return self.loop["read_score"](self.root, run_id, "fixture", self.evidence, [trial_result],
                                           "VERIFY: scaffold sent two attempts and one budget probe")

        self.assertEqual(read(record)["score"], 42)
        with self.assertRaisesRegex(AssertionError, "usage does not match"):
            read(dict(record, usage=dict(usage, normalized_usd=0)))
        with self.assertRaisesRegex(AssertionError, "not terminal and completed"):
            read(dict(record, status="failed"))
        wrong_score = dict(stats, evals={"fixture": {"reward_stats": {"sample_score": {"0": [trial.name]}}}})
        with self.assertRaisesRegex(AssertionError, "outcome and score"):
            read(dict(record, execution=dict(outcome, stats=wrong_score)))

    def test_isolation_join_is_bounded_and_preserves_primary_error(self):
        isolation = runpy.run_path(REPOSITORY / "script/check-run-isolation.py")["main"].__globals__
        server = Mock()
        server.shutdown.side_effect = RuntimeError("listener shutdown failed")
        thread = Mock()
        thread.is_alive.return_value = True
        primary = subprocess.CalledProcessError(2, ["docker"], stderr="fixture")

        class Server:
            def __new__(cls, *_):
                return server

        with patch.dict(isolation, ThreadingHTTPServer=Server), \
             patch("threading.Thread", return_value=thread), patch.object(subprocess, "run", side_effect=primary), \
             patch.object(sys, "argv", ["isolation", "--image", "fixture"]), redirect_stderr(io.StringIO()) as stderr, \
             self.assertRaises(subprocess.CalledProcessError) as caught:
            isolation["main"]()

        self.assertIs(caught.exception, primary)
        thread.join.assert_called_once_with(2)
        self.assertIn("Host listener thread did not stop.", stderr.getvalue())
