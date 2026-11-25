"""Installed Google routes work through discovery, compilation and private staging."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

from dungeness.contracts import model_providers
from dungeness.credential_access import credential_requirements, prepare_credentials
from gateway_auth import authentication_headers
from gateway_google import upstream_request
from gateway_pricing import pricing_for_request
from model_access import MODEL_ACCESS
from test_command_harness import compiler

ROOT = Path(__file__).resolve().parents[1]


class GoogleRouteTests(unittest.TestCase):
    def test_offline_request_checker_needs_no_cloud_credentials(self):
        with tempfile.TemporaryDirectory() as temp:
            request = Path(temp) / "request.json"
            request.write_text(json.dumps({"model": "gemini-4-carbon",
                "messages": [{"role": "user", "content": "Return 42"}],
                "max_completion_tokens": 512, "reasoning_effort": "low"}))
            for provider in ("google", "google-vertex"):
                result = subprocess.run([sys.executable, str(ROOT / "tools/validate-model-request.py"),
                    "--provider", provider, "--operation", "chat/completions", "--request", str(request)],
                    env={"PATH": os.defpath, "DUNGENESS_CREDENTIALS_FILE": "/must-not-read"},
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(json.loads(result.stdout)["valid"])

    def test_discovery_compiler_and_pricing_agree_for_every_bundled_google_model(self):
        discovered = model_providers(ROOT, details=True)
        routes = {entry["id"]: entry for entry in discovered["access_routes"]}
        for provider in ("google", "google-vertex"):
            self.assertIn(provider, discovered["providers"])
            requirements = credential_requirements([provider])
            self.assertEqual(routes[provider]["credential_inputs"], requirements)
            for model, mapping in MODEL_ACCESS[provider]["models"].items():
                with self.subTest(provider=provider, model=model):
                    self.assertEqual(pricing_for_request(provider, model)["upstream_id"], mapping["catalog"])
                    selected = {"provider": provider, "request_model": model,
                                "upstream_id": mapping["catalog"], "api": "openai-chat",
                                "name_format": "request"}
                    models = compiler.command_models({"model": selected})
                    compose = yaml.safe_load(compiler.build_compose(
                        "google-contract", {}, {"model": {"requests": 4, "total_tokens": 8192}},
                        command_policy={"models": models}))
                    gateway = compose["services"]["gateway"]
                    self.assertEqual(gateway["x-dungeness-credential-env"], requirements["environment"])
                    self.assertEqual(json.loads(gateway["environment"]["DUNGENESS_ALLOWED_MODELS"]),
                                     [[provider, model]])
                    self.assertEqual(models[0]["base_url"], f"http://gateway:8080/model/{provider}/v1")

    def test_vertex_project_and_token_stay_in_private_gateway_staging(self):
        supplied = {"TESTBED_VERTEX_ACCESS_TOKEN": "synthetic-token",
                    "TESTBED_VERTEX_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
                    "TESTBED_VERTEX_PROJECT_ID": "sample-project",
                    "TESTBED_GEMINI_API_KEY": "unselected-api-key",
                    "GOOGLE_REFRESH_TOKEN": "must-not-stage"}
        with prepare_credentials(credential_requirements(["google-vertex"]), supplied) as (paths, _):
            private = Path(paths["DUNGENESS_CREDENTIALS_FILE"])
            staged = private.read_text()
            self.assertNotIn("unselected-api-key", staged)
            self.assertNotIn("must-not-stage", staged)
            with patch.dict(os.environ, paths, clear=True):
                config = MODEL_ACCESS["google-vertex"]
                headers = authentication_headers(config["authentication"])
                url, _, _ = upstream_request(config, {
                    "model": "gemini-4-carbon", "messages": [{"role": "user", "content": "42"}]},
                    "gemini-4-carbon", "fixture", headers)
            self.assertEqual(url, "https://aiplatform.googleapis.com/v1/projects/"
                             "sample-project/locations/global/publishers/google/models/"
                             "gemini-4-carbon:generateContent")
            self.assertNotIn("synthetic-token", url)
        self.assertFalse(private.exists())
