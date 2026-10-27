"""The public compatibility contract works without runtime initialization."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import shutil


ROOT = Path(__file__).resolve().parents[1]


class RuntimeContractTests(unittest.TestCase):
    def test_providers_match_gateway_and_use_only_the_selected_checkout(self):
        from dungeness.contracts import model_providers
        expected = model_providers(ROOT)
        self.assertEqual(expected["providers"], ["anthropic", "claude-subscription", "openai", "openai-chatgpt", "openrouter"])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # Prove registry extensions come from this runtime, not Catalyst or
            # a previously imported checkout. No server or credential is used.
            gateway = root / "services/gateway"
            shutil.copytree(ROOT / "services/gateway", gateway,
                            ignore=shutil.ignore_patterns("__pycache__", "tests"))
            profile = {"protocol": "openai", "base_url": "https://example.invalid/v1",
                       "credential_env": "EXAMPLE_API_KEY", "credential_kind": "api-key",
                       "billed": True, "routes": ["chat/completions"], "headers": {},
                       "model_header": None, "models": {}, "catalog_author": "example"}
            (gateway / "providers.json").write_text(json.dumps({"schema_version": 1, "providers": {"example": profile}}))
            result = subprocess.run([sys.executable, "-B", "-c",
                "import json; from pathlib import Path; from dungeness.contracts import model_providers; "
                "print(json.dumps(model_providers(Path('.'))))"], cwd=root,
                env={"PATH": os.environ["PATH"], "PYTHONPATH": str(ROOT / "src")},
                capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)["providers"], sorted(expected["providers"] + ["example"]))
            (gateway / "providers.json").write_text('{"schema_version": 1, "providers": {"broken": {}}}')
            bad = subprocess.run([sys.executable, str(gateway / "gateway_models.py")],
                                 capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)

    def test_providers_cli_needs_no_credentials_or_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, "-B", str(ROOT / "dungeness"), "providers"],
                                    cwd=temp, env={"PATH": os.environ["PATH"]},
                                    capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout), {
                "schema_version": 1, "runtime": "dungeness",
                "providers": ["anthropic", "claude-subscription", "openai", "openai-chatgpt", "openrouter"]})
            self.assertEqual(list(Path(temp).iterdir()), [])

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
