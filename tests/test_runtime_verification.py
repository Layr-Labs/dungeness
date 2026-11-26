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

    def test_malformed_route_report_fails_command_evidence(self):
        def command(_argv, _cwd, _env, output, _stderr):
            output.write(b"not JSON")
            return 0

        with patch.dict(self.loop, command=command), self.assertRaises(self.loop["VerificationError"]):
            self.loop["route_check"](self.root, self.evidence, "routes", {})

        entry, = self.evidence["commands"]
        self.assertEqual(entry["exit_code"], 0)
        self.assertEqual(entry["status"], "failed")
        self.assertIn("Cannot parse the route report", (self.logs / "routes.log").read_text())

    def test_missing_scored_record_fails_command_evidence(self):
        self.evidence["docker_bind_owner"] = f"{os.geteuid()}:{os.getegid()}"
        root = self.root / "repo"
        root.mkdir()
        with patch.dict(self.loop, stage_gateway=Mock(), stage_run=Mock(return_value=("spec", "fixture")),
                        command=Mock(return_value=0), check_scored_cleanup=Mock(),
                        fixture_images=Mock(return_value=nullcontext())), self.assertRaises(self.loop["VerificationError"]):
            self.loop["scored_run"](root, None, None, self.evidence, "scored", {})

        entry, = self.evidence["commands"]
        self.assertEqual(entry["exit_code"], 0)
        self.assertEqual(entry["status"], "failed")
        self.assertIn("record.json", (self.logs / "scored.log").read_text())

    def test_shared_credential_cleanup_owns_only_new_canary_directories(self):
        shm = self.root / "shm"
        shm.mkdir()
        root = self.root / "repo"
        root.mkdir()
        self.evidence["docker_bind_owner"] = f"{os.geteuid()}:{os.getegid()}"

        def credential_dir(name, contents):
            path = shm / f"dungeness-credentials-{name}"
            path.mkdir()
            (path / "credentials.json").write_bytes(contents)
            return path

        old = credential_dir("old", self.loop["CANARY_BYTES"])
        other = credential_dir("other", b"unrelated")

        def command(*_):
            credential_dir("foreign", b"unrelated")
            credential_dir("leak", self.loop["CANARY_BYTES"])
            return 0

        with patch.dict(self.loop, SHARED_CREDENTIALS=shm, stage_gateway=Mock(),
                        stage_run=Mock(return_value=("spec", "fixture")), command=command,
                        read_score=Mock(return_value={}), fixture_images=Mock(return_value=nullcontext())):
            code, log = self.loop["scored_run"](root, None, None, self.evidence, "scored", {})

        self.assertEqual(code, 1)
        self.assertIn("dungeness-credentials-leak", log)
        self.assertNotIn(self.loop["CANARY"], log)
        self.assertEqual(set(shm.iterdir()), {old, other, shm / "dungeness-credentials-foreign"})

    def test_trial_result_requires_both_projects(self):
        trial = self.root / "harbor/job/renamed-trial"
        trial.mkdir(parents=True)
        (trial / "result.json").write_text("{}")
        self.loop["check_scored_cleanup"](self.root, self.logs, self.root, {}, self.evidence, failed=False)
        self.assertIn("Cannot identify both Docker projects", str(self.evidence["cleanup_errors"]))

    def test_surviving_labelled_verifier_container_fails_cleanup(self):
        trial = self.root / "harbor/job/task__HarborID"
        trial.mkdir(parents=True)
        (trial / "result.json").write_text("{}")
        verifier = "task__harborid__verifier__trial"
        env = {"DOCKER_CONTEXT": "fixture"}
        container = "labelled-fixture-container"

        def capture(*argv, **kwargs):
            self.assertEqual(kwargs, {"cwd": self.root, "env": env})
            if argv[:3] == ("docker", "container", "ls") and argv[-1].endswith("=" + verifier):
                return container
            if argv[:2] == ("docker", "compose"):
                raise self.loop["VerificationError"]("fixture compose stderr")
            return ""

        with patch.dict(self.loop, capture=capture), patch.object(subprocess, "run", return_value=Mock(returncode=0)), \
             redirect_stderr(io.StringIO()):
            self.loop["check_scored_cleanup"](self.root, self.logs, self.root, env, self.evidence, failed=False)

        self.assertEqual(self.evidence["scored_run"]["docker_projects"],
                         ["task__harborid__env", verifier])
        self.assertIn(container, str(self.evidence["cleanup_errors"]))
        self.assertIn("fixture compose stderr", str(self.evidence["cleanup_errors"]))

    def test_project_images_untag_all_refs_before_attempting_any_id(self):
        project = "task__harborid__env"
        first = "sha256:first"
        parent = "sha256:parent"
        child = "sha256:child"
        tag = f"{project}-main:latest"
        extra_tag = f"{project}-extra:latest"
        dangling = f"{parent} <none>:<none>\n{child} <none>:<none>"
        listing = f"{first} {tag}\n{first} {extra_tag}\n{dangling}"
        removals = []

        def capture(*argv, **_kwargs):
            if argv[:3] == ("docker", "image", "rm"):
                removals.append(argv[4:])
            elif argv[:3] == ("docker", "image", "history"):
                return "step\nparent\nbase" if argv[-1] == child else "parent\nbase"
            elif any(arg.startswith("reference=") for arg in argv):
                return listing.splitlines()[0]
            elif argv[:3] == ("docker", "image", "ls"):
                return (listing, dangling, "")[len(removals)]
            return ""

        with patch.dict(self.loop, capture=capture):
            owned = self.loop["project_images"](project, self.root, {})
            images = self.loop["project_resources"](project, self.root, {})["images"]
            self.loop["remove_images"](owned, self.root, {}, self.evidence, "fixture")
        self.assertEqual(images, [extra_tag, tag, child, parent])
        self.assertEqual(removals, [(extra_tag, tag), (child, parent)])
        self.assertEqual(self.evidence["cleanup_errors"], [])
        self.assertEqual(self.evidence["image_cleanup"][0]["removed"], [child, first, parent])

    def test_fixture_cleanup_reports_new_unlabelled_provider_image(self):
        before = {"sha256:base": set(), "sha256:existing": set()}
        after = {**before, "sha256:leak": set()}
        history = Mock(return_value="CMD /app/verify_provider.py")
        with patch.dict(self.loop, capture=Mock(return_value=""), image_inventory=Mock(side_effect=(before, {}, after)),
                        image_history=history, remove_images=Mock()):
            with self.loop["fixture_images"](self.root, {}, self.evidence, "owner"):
                pass

        history.assert_called_once_with("sha256:leak", self.root, {})
        self.assertIn("Verification left a fixture image: sha256:leak", self.evidence["cleanup_errors"])

    def test_fixture_cleanup_releases_failed_builder_container_before_its_image(self):
        operations = Mock()
        operations.capture.return_value = "fixture-container"
        operations.inventory.side_effect = ({}, {"sha256:fixture": set()}, {})
        env = {"DOCKER_CONTEXT": "fixture"}
        with patch.dict(self.loop, capture=operations.capture, image_inventory=operations.inventory,
                        remove_images=operations.remove_images):
            with self.assertRaisesRegex(AssertionError, "primary error"):
                with self.loop["fixture_images"](self.root, env, self.evidence, "owner"):
                    raise AssertionError("primary error")

        self.assertEqual(operations.capture.call_args_list[0].args[-1], "label=dungeness.verify.owner=owner")
        self.assertEqual(operations.mock_calls[2].args,
                         ("docker", "container", "rm", "--force", "fixture-container"))
        self.assertEqual(operations.mock_calls[4].args[0], {"sha256:fixture": set()})
        self.assertIn("Verification left fixture containers: fixture-container", self.evidence["cleanup_errors"])

    def test_health_poll_bounds_docker_exec(self):
        isolation = runpy.run_path(REPOSITORY / "script/check-gateway-isolation.py")["main"].__globals__

        def docker(argv, **kwargs):
            if argv[1] == "exec":
                self.assertEqual(kwargs.get("timeout"), 10)
                raise subprocess.TimeoutExpired(argv, 10)
            return subprocess.CompletedProcess(argv, 0, '[{"Config": {"Env": []}}]', "")

        with patch.object(subprocess, "run", side_effect=docker), \
             patch.object(sys, "argv", ["isolation", "--image", "fixture"]), \
             self.assertRaises(subprocess.TimeoutExpired):
            isolation["main"]()

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

        def docker(*args, **kwargs):
            nonlocal image_removed
            argv = list(args)
            docker_commands.append(argv)
            if argv[:2] == ["docker", "compose"]:
                self.assertEqual(kwargs["cwd"], root)
                self.assertEqual(kwargs["env"]["TMPDIR"], str(root.parent / "tmp"))
                self.assertNotIn("COMPOSE_FILE", kwargs["env"])
                if "__verifier__" in argv[3]:
                    raise self.loop["VerificationError"]("fixture error")
                return ""
            if argv[:3] == ["docker", "image", "rm"]:
                self.assertEqual(argv[3:], ["--no-prune", verifier_image])
                image_removed = True
                return ""
            if argv[:3] == ["docker", "image", "ls"]:
                return f"sha256:fixture {verifier_image}" if f"reference={verifier_image}" in argv and not image_removed else ""
            self.assertIn(argv[-1], {
                "label=com.docker.compose.project=task__harborid__env",
                "label=com.docker.compose.project=task__harborid__verifier__trial",
            })
            return ""

        with patch.dict(self.loop, stage_gateway=lambda *args, **kwargs: None,
                        stage_run=lambda *args: ("spec", "fixture"), command=run, capture=docker,
                        fixture_images=Mock(return_value=nullcontext())), \
             patch.dict(os.environ, COMPOSE_FILE="unrelated.yaml"), redirect_stderr(io.StringIO()), \
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
            self.loop["stage_gateway"](self.root, "base", {}, "owner")

    def test_baseline_rejects_missing_or_empty_unittest_suite(self):
        self.evidence["counts"] = {}
        for missing in (True, False):
            log = self.check_log()
            if missing:
                log = log.removesuffix("Checking Harbor adapter contract\nRan 1 test in 0s\n")
            else:
                log = log.replace("Ran 1 test", "Ran 0 tests")
            with self.subTest(missing=missing), patch.dict(self.loop, checked=Mock(return_value=log),
                                                           route_check=Mock(return_value=(1, ""))):
                with self.assertRaisesRegex(AssertionError, "unittest suite"):
                    self.loop["baseline"](self.evidence, None, None, {})

    def test_sdk_timeout_preserves_earlier_baseline_failures(self):
        self.evidence["counts"] = {}
        sdk = Mock(side_effect=subprocess.TimeoutExpired(["google-sdk"], 1))
        with patch.dict(self.loop, LINUX_X86=False, checked=Mock(return_value=self.check_log()),
                        scratch=Mock(return_value=nullcontext(self.root)), route_check=Mock(return_value=(0, "")),
                        gateway_check=Mock(return_value=(1, "")), scored_run=Mock(return_value=(0, "")),
                        record_command=sdk):
            with self.assertRaisesRegex(AssertionError, "Gateway isolation failed.*google-sdk.*timed out"):
                self.loop["baseline"](self.evidence, None, None, {})
        argv = sdk.call_args.args[2]
        self.assertEqual(argv[argv.index("--python") + 1], "3.12")

    @staticmethod
    def check_log():
        suites = ("tests", "services/gateway/tests", "tools/transcripts", "Harbor adapter contract")
        return "".join(f"Checking {suite}\nRan 1 test in 0s\n" for suite in suites)

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
