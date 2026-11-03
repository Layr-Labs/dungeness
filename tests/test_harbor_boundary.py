"""Execution adapter boundaries; no Docker, credentials or model calls."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dungeness.execution import harbor


class HarborBoundaryTests(unittest.TestCase):
    def test_adapter_import_needs_no_compiler_gateway_or_harbor_sdk(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-c", """
import sys
from dungeness.execution import harbor, runner
assert not any(name == 'harbor' or name.startswith('harbor.')
               or name.startswith('gateway') or name == 'dungeness.compiler'
               for name in sys.modules)
"""], cwd=directory, capture_output=True, text=True,
                env={"PATH": os.defpath, "PYTHONPATH": str(ROOT / "src"),
                     "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_launch_uses_tested_dependency_pins_and_literal_paths(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())
        dependencies = project["dependency-groups"]["harbor"]
        command = harbor.launch_command(Path("job with spaces;literal.yaml"), "env with spaces")
        self.assertIn(command[command.index("--from") + 1], dependencies)
        self.assertIn(command[command.index("--with") + 1], dependencies)
        self.assertEqual(command[-4:], ["--env-file", "env with spaces",
                                       "--config", "job with spaces;literal.yaml"])

    def test_trusted_adapter_precedes_existing_import_path_without_mutating_host(self):
        base = {"PYTHONPATH": "/existing", "AWS_ACCESS_KEY_ID": "synthetic",
                "TESTBED_OPENAI_API_KEY": "synthetic-gateway"}
        original = dict(base)
        environment, scrubbed = harbor.harbor_launch_environment(
            base, {}, adapter_path=Path("/trusted/adapter"),
        )
        self.assertEqual(base, original)
        self.assertEqual(environment["PYTHONPATH"], "/trusted/adapter" + os.pathsep + "/existing")
        self.assertEqual(scrubbed, ["AWS_ACCESS_KEY_ID"])
        self.assertNotIn("AWS_ACCESS_KEY_ID", environment)
        self.assertEqual(environment["TESTBED_OPENAI_API_KEY"], "synthetic-gateway")


if __name__ == "__main__":
    unittest.main()
