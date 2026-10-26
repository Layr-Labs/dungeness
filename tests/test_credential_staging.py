"""Real file staging with synthetic access; never contact a model provider."""
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

import yaml

from dungeness.execution.credentials import gateway_credentials


class CredentialStagingTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.dict(os.environ, {"PATH": os.defpath}, clear=True))
        (self.root / "environment").mkdir()
        self.env_file = self.root / "access.env"
        self.env_file.write_text("TESTBED_EXAMPLE_TOKEN='synthetic-key'\n"
                                 "EXA_API_KEY=synthetic-search-key\n"
                                 "EXAMPLE_BASE_URL=http://mock:8081\n"
                                 "UNRELATED_SECRET=must-not-propagate\n")
        self.sources = {"EXAMPLE_TOKEN": "TESTBED_EXAMPLE_TOKEN", "EXA_API_KEY": "EXA_API_KEY"}
        (self.root / "environment/docker-compose.yaml").write_text(yaml.safe_dump({
            "services": {"gateway": {"x-dungeness-credential-env": self.sources,
                "environment": {"EXAMPLE_BASE_URL": "${EXAMPLE_BASE_URL:-http://mock}"},
                "volumes": ["${DUNGENESS_CREDENTIALS_FILE}:/credentials:ro"]}}}))

    def test_private_staging_no_secrets_in_launch_and_cleanup(self):
        with gateway_credentials(self.root, self.env_file, {
                "PATH": os.defpath, "TESTBED_EXAMPLE_TOKEN": "ambient-secret",
                "EXA_API_KEY": "ambient-search", "EXAMPLE_TOKEN": "raw-ambient-secret"}) as (env, empty):
            path = Path(env["DUNGENESS_CREDENTIALS_FILE"])
            self.assertEqual(json.loads(path.read_text()), {
                "EXAMPLE_TOKEN": "synthetic-key", "EXA_API_KEY": "synthetic-search-key"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(empty.stat().st_mode & 0o777, 0o600)
            self.assertEqual(env["EXAMPLE_BASE_URL"], "http://mock:8081")
            self.assertEqual(env["PATH"], os.defpath)
            for value in ("synthetic-key", "ambient-secret", "synthetic-search-key", "must-not-propagate"):
                self.assertNotIn(value, json.dumps(env) + empty.read_text())
            self.assertNotIn("UNRELATED_SECRET", env)
        self.assertFalse(path.parent.exists())
        self.assertTrue(self.env_file.exists())

    def test_cleanup_on_failure_and_cancellation(self):
        for error in (RuntimeError("synthetic failure"), KeyboardInterrupt()):
            with self.subTest(error=type(error)), self.assertRaises(type(error)):
                with gateway_credentials(self.root, self.env_file, {}) as (env, _):
                    path = Path(env["DUNGENESS_CREDENTIALS_FILE"])
                    raise error
            self.assertFalse(path.parent.exists())

    def test_missing_required_key_fails_without_exposing_values(self):
        self.env_file.write_text("UNRELATED_SECRET=synthetic-private\n")
        with self.assertRaisesRegex(ValueError, "TESTBED_EXAMPLE_TOKEN is missing"):
            with gateway_credentials(self.root, self.env_file, {}):
                self.fail("Missing credentials must prevent launch")

    def test_env_file_takes_precedence_over_host(self):
        with patch.dict(os.environ, {"TESTBED_EXAMPLE_TOKEN": "ambient"}):
            with gateway_credentials(self.root, self.env_file, {}) as (env, _):
                self.assertEqual(json.loads(Path(env["DUNGENESS_CREDENTIALS_FILE"]).read_text())[
                    "EXAMPLE_TOKEN"], "synthetic-key")

    def test_sigterm_removes_private_files_in_real_child(self):
        code = '''from pathlib import Path
import sys, time
from dungeness.execution.credentials import gateway_credentials
from dungeness.execution.process import termination_as_interrupt
try:
 with termination_as_interrupt():
  with gateway_credentials(Path(sys.argv[1]), Path(sys.argv[2]), {}) as (env, _):
   print(env['DUNGENESS_CREDENTIALS_FILE'], flush=True)
   time.sleep(30)
except KeyboardInterrupt:
 pass
'''
        child_env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
        child = subprocess.Popen([sys.executable, "-c", code, str(self.root), str(self.env_file)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=child_env)
        try:
            path = Path(child.stdout.readline().strip())
            self.assertTrue(path.is_file())
            child.terminate()
            stdout, stderr = child.communicate(timeout=10)
            self.assertEqual(child.returncode, 0, stderr)
            self.assertFalse(path.parent.exists())
        finally:
            if child.poll() is None:
                child.kill(); child.wait()
            child.stdout.close(); child.stderr.close()
