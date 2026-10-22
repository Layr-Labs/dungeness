"""The public compatibility contract works without runtime initialization."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RuntimeContractTests(unittest.TestCase):
    def test_capabilities_from_an_unrelated_directory_need_no_workspace_or_credentials(self):
        with tempfile.TemporaryDirectory() as temp:
            environment = {key: value for key, value in os.environ.items()
                           if key in {"PATH", "SYSTEMROOT"}}
            environment["HOME"] = temp
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(
                [sys.executable, str(ROOT / "dungeness"), "capabilities"],
                cwd=temp, env=environment, capture_output=True, text=True, check=True,
            )
            self.assertEqual(json.loads(result.stdout), json.loads((ROOT / "runtime-contract.json").read_text()))
            self.assertEqual(result.stderr, "")
            self.assertEqual(list(Path(temp).iterdir()), [])
