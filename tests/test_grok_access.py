"""The official Grok API uses shared route selection and private credentials."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from test_command_harness import compiler
from access_selection import export_policy, resolve_endpoint
from dungeness.credential_access import credential_requirements, prepare_credentials
from model_access import DEFAULT_MODEL_ACCESS, validate_upstream_settings


class GrokAccessTests(unittest.TestCase):
    def test_model_compiles_for_native_operations_and_exports_approved_policy(self):
        for api in ("openai-responses", "openai-chat"):
            with self.subTest(api=api):
                model = {"provider": "xai", "upstream_id": "x-ai/grok-4.7",
                         "request_model": "grok-4.7", "api": api, "name_format": "request"}
                resolved, = compiler.command_models({"model_access": {"models": [model]}})
                self.assertEqual(resolved["base_url"], "http://gateway:8080/model/xai/v1")
        pricing = yaml.safe_load((Path(__file__).resolve().parents[1] /
                                  "services/gateway/pricing.yaml").read_text())
        policy = export_policy(DEFAULT_MODEL_ACCESS, pricing)
        self.assertIn("grok-4.7", policy["routes"]["xai"]["models"])
        self.assertNotIn("grok-subscription", policy["routes"])
        self.assertEqual(resolve_endpoint(DEFAULT_MODEL_ACCESS, {
            "endpoint": "https://api.x.ai/v1", "authentication": "bearer"}), "xai")
        with self.assertRaises(ValueError):
            validate_upstream_settings({"XAI_UPSTREAM_BASE_URL": "https://unapproved.invalid/v1"})

    def test_only_the_selected_api_key_is_staged_and_removed(self):
        requirements = credential_requirements(["xai"])
        self.assertEqual(requirements, {"schema_version": 1,
                         "environment": {"XAI_API_KEY": "TESTBED_XAI_API_KEY"}, "files": {}})
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"TMPDIR": tmp}):
            with prepare_credentials(requirements, {
                "TESTBED_XAI_API_KEY": "synthetic-xai-secret",
                "TESTBED_OPENAI_API_KEY": "unselected-secret",
            }) as (paths, _):
                private = Path(paths["DUNGENESS_CREDENTIALS_FILE"])
                self.assertEqual(private.stat().st_mode & 0o777, 0o600)
                self.assertEqual(json.loads(private.read_text()), {"XAI_API_KEY": "synthetic-xai-secret"})
            self.assertFalse(private.exists())
