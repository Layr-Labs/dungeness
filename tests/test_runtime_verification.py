"""Exercise loop failures without a Docker daemon or a provider."""
from contextlib import nullcontext
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


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
        registry = json.loads((REPOSITORY / "services/gateway/model-access.json").read_text())["access_routes"]
        document = {
            "providers": sorted(self.loop["ROUTES"]),
            "access_policy": {"schema_version": 1, "sha256": self.loop["policy_digest"](registry)},
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
            with self.assertRaisesRegex(self.loop["VerificationError"], "unexpected registered route"):
                self.loop["route_check"](REPOSITORY, self.evidence, "extra-route", None)

        self.assertIn("uv warning", (self.logs / "routes.log").read_text())
        self.assertIn("unexpected registered route", (self.logs / "extra-route.log").read_text())

    def test_failed_fault_preserves_baseline_and_runs_the_next_fault(self):
        baseline = {"score": 42}
        self.evidence.update(scored_run=baseline)
        verification_error = self.loop["VerificationError"]

        def fail_route(*_arguments):
            raise verification_error("malformed route report")

        def scored(_root, _base, _stock, evidence, _name, _env):
            evidence["scored_run"] = {"score": 0}
            return 1, "retry assertion"

        with patch.dict(self.loop, FAULTS={"missing-route": "route assertion", "lost-retry-flag": "retry assertion"},
                        scratch=lambda *args: nullcontext(self.root), seed=lambda *args: None,
                        route_check=fail_route, scored_run=scored):
            with self.assertRaisesRegex(verification_error, "A fault survived or failed"):
                self.loop["proof"](self.evidence, "", "", {})

        self.assertIs(self.evidence["scored_run"], baseline)
        self.assertEqual([fault["status"] for fault in self.evidence["faults"]], ["failed", "detected"])
        self.assertEqual(self.evidence["faults"][0]["error"], "malformed route report")
