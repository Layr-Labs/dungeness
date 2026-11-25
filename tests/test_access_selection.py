"""Caller choices cannot replace trusted endpoints, mappings or accounting."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import yaml

from test_command_harness import compiler
from access_selection import export_policy, policy_digest, resolve_routes, resolve_endpoint, resolve_model, selection_evidence
from dungeness.credential_access import credential_requirements, prepare_credentials
from model_access import DEFAULT_MODEL_ACCESS

ROOT = Path(__file__).resolve().parents[1]
SELECTION = {"claude-subscription": {"endpoint": "https://api.anthropic.com/v1",
                                   "authentication": "bearer"}}
MODEL = {**SELECTION["claude-subscription"], "request_model": "claude-opus-5",
         "upstream_id": "anthropic/claude-opus-5", "api": "anthropic-messages", "name_format": "request"}


class AccessSelectionTests(unittest.TestCase):
    def test_endpoint_selection_resolves_the_complete_route_without_mutating_it(self):
        original = copy.deepcopy(DEFAULT_MODEL_ACCESS)
        resolved = resolve_routes(original, SELECTION)
        self.assertEqual(original, DEFAULT_MODEL_ACCESS)
        self.assertEqual(resolved, original)
        self.assertEqual(resolve_model(original, MODEL)["provider"], "claude-subscription")
        self.assertEqual(resolve_endpoint(original, {
            "endpoint": "https://api.anthropic.com/v1", "authentication": "api-key"}), "anthropic")
        self.assertEqual(resolve_endpoint(original, {
            "endpoint": "https://aiplatform.googleapis.com/v1", "authentication": "bearer"}), "google-vertex")
        self.assertEqual(resolve_routes(original, {}), original)
        self.assertEqual(selection_evidence(original, SELECTION)["policy_sha256"], policy_digest(original))

    def test_url_and_configuration_escape_hatches_are_rejected_without_echoing_values(self):
        for patch in (
            {"endpoint": "https://api.anthropic.com.evil.invalid/v1"},
            {"endpoint": "https://api.anthropic.com/v1/messages/../files"},
            {"endpoint": "https://api.anthropic.com/v1?api_key=private"},
            {"endpoint": "https://private@api.anthropic.com/v1"},
            {"endpoint": "http://api.anthropic.com/v1"},
            {"authentication": "openai"},
            {"authentication": {"headers": {"authorization": "private"}}},
            {"headers": {"x-upstream-url": "https://private.invalid"}},
            {"usage_parser": "private"}, {"models": {}}, {"prices": {}},
            {"credential": "private"}, {"transport": "passthrough"},
        ):
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError) as caught:
                    resolve_endpoint(DEFAULT_MODEL_ACCESS, {**SELECTION["claude-subscription"], **patch})
                self.assertNotIn("private", str(caught.exception))
        with self.assertRaises(ValueError):
            resolve_model(DEFAULT_MODEL_ACCESS, {**MODEL, "provider": "anthropic"})
        duplicate = copy.deepcopy(DEFAULT_MODEL_ACCESS)
        duplicate["ambiguous"] = duplicate["claude-subscription"]
        with self.assertRaises(ValueError):
            resolve_endpoint(duplicate, SELECTION["claude-subscription"])

    def test_selected_credentials_only_and_compose_evidence(self):
        policy = {"models": [MODEL]}
        models = compiler.command_models({"model_access": policy, "model": MODEL})
        compose = yaml.safe_load(compiler.build_compose(
            "selection", {}, {"model": {"requests": 4, "total_tokens": 10000}},
            command_policy={**policy, "models": models}))
        gateway = compose["services"]["gateway"]
        self.assertEqual(json.loads(gateway["environment"]["DUNGENESS_ACCESS_SELECTION"]), SELECTION)
        self.assertEqual(compose["x-dungeness-model-access"], selection_evidence(DEFAULT_MODEL_ACCESS, SELECTION))
        requirements = credential_requirements(["claude-subscription"], SELECTION)
        self.assertNotIn("ANTHROPIC_API_KEY", requirements["environment"])
        supplied = {"TESTBED_CLAUDE_ACCESS_TOKEN": "private-token",
                    "TESTBED_CLAUDE_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
                    "TESTBED_ANTHROPIC_API_KEY": "unselected-secret"}
        with prepare_credentials(requirements, supplied) as (paths, _):
            private = Path(paths["DUNGENESS_CREDENTIALS_FILE"])
            self.assertNotIn("unselected-secret", private.read_text())
            code = ("from model_access import MODEL_ACCESS; from gateway_auth import authentication_headers;"
                    "h=authentication_headers(MODEL_ACCESS['claude-subscription']['authentication']);"
                    "assert h['authorization']=='Bearer private-token'; assert 'x-api-key' not in h")
            result = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True,
                env={"PATH": os.defpath, "PYTHONPATH": str(ROOT / "services/gateway"), **paths,
                     "DUNGENESS_ACCESS_SELECTION": json.dumps(SELECTION)})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("private-token", json.dumps(compose))
            self.assertNotIn("CLAUDE_ACCESS_TOKEN", json.dumps(compose["services"]["main"]))
        self.assertFalse(private.exists())

    def test_wrong_model_price_or_protocol_cannot_compile(self):
        for patch in ({"request_model": "unapproved-model"},
                      {"upstream_id": "anthropic/claude-sonnet-5-5"},
                      {"api": "openai-chat"}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                model = {**MODEL, **patch}
                compiler.command_models({"model": model, "model_access": {"models": [model]}})

    def test_existing_production_chat_completions_label_is_preserved(self):
        model = {"provider": "openai", "request_model": "gpt-5.6-sol",
                 "upstream_id": "openai/gpt-5.6-sol", "api": "openai-completions",
                 "name_format": "request"}
        resolved, = compiler.command_models({"model": model})
        self.assertEqual(resolved["api"], "openai-completions")
        self.assertEqual(resolved["base_url"], "http://gateway:8080/model/openai/v1")

    def test_ambiguous_public_selection_and_invalid_startup_fail_closed(self):
        with self.assertRaises(ValueError):
            compiler.command_models({"model": MODEL, "model_access": {
                "models": [MODEL], "routes": {"google": {"endpoint": "https://generativelanguage.googleapis.com/v1beta",
                                                       "authentication": "api-key"}}}})
        for selection in ("null", "[]", "bad", '{"anthropic":{"endpoint":"https://evil.invalid","authentication":"anthropic"}}'):
            result = subprocess.run([sys.executable, "-B", "-c", "import model_access"], capture_output=True,
                env={"PATH": os.defpath, "PYTHONPATH": str(ROOT / "services/gateway"),
                     "DUNGENESS_ACCESS_SELECTION": selection})
            self.assertNotEqual(result.returncode, 0)

    def test_public_policy_comes_from_registry_and_prices(self):
        prices = yaml.safe_load((ROOT / "services/gateway/pricing.yaml").read_text())
        policy = export_policy(DEFAULT_MODEL_ACCESS, prices)
        self.assertEqual(policy["routes"]["anthropic"]["authentication"], ["api-key"])
        self.assertEqual(policy["routes"]["claude-subscription"]["authentication"], ["bearer"])
        self.assertEqual(policy["routes"]["google"]["authentication"], ["api-key"])
        self.assertEqual(policy["routes"]["google-vertex"]["authentication"], ["bearer"])
        self.assertIn("gemini-4-carbon", policy["routes"]["google"]["models"])
        self.assertNotIn("authentication", policy["routes"]["google"]["models"])
        self.assertNotIn("sources", json.dumps(policy))
