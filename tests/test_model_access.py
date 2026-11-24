"""The compiler's launch inputs satisfy the gateway's authentication contract."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from test_command_harness import compiler, MODEL
from dungeness.execution.credentials import gateway_credentials
from gateway_auth import authentication_headers
from model_access import MODEL_ACCESS, configured_provider

BUDGET = {"model": {"requests": 10, "total_tokens": 10000}}


class ModelAccessContractTests(unittest.TestCase):
    def test_existing_connections_keep_their_private_inputs_and_harness_urls(self):
        expected = {
            "openai": {"OPENAI_API_KEY"},
            "anthropic": {"ANTHROPIC_API_KEY"},
            "claude-subscription": {"CLAUDE_ACCESS_TOKEN", "CLAUDE_ACCESS_TOKEN_EXPIRES_AT"},
            "openrouter": {"OPENROUTER_API_KEY"},
            "openai-chatgpt": set(),
            "grok-subscription": {"GROK_SUBSCRIPTION_TOKEN", "GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT"},
            "minimax-subscription": {"MINIMAX_CODING_PLAN_KEY"},
        }
        for provider, keys in expected.items():
            with self.subTest(provider=provider):
                compose = yaml.safe_load(compiler.build_compose(
                    "connection-contract", {}, BUDGET, provider=provider,
                    command_policy={"models": [{**MODEL, "provider": provider,
                        "base_url": "http://gateway:8080/model/example/v1"}]}))
                gateway = compose["services"]["gateway"]
                self.assertEqual(gateway["x-dungeness-credential-env"],
                                 {key: "TESTBED_" + key for key in keys})
                self.assertFalse(keys & gateway["environment"].keys())
                main = compose["services"]["main"]
                for key in keys:
                    self.assertIn(main["environment"].get(key), (None, "testbed"))
                    self.assertNotIn("TESTBED_" + key, json.dumps(main))
                if provider == "openai-chatgpt":
                    self.assertEqual(gateway["environment"]["DUNGENESS_CHATGPT_AUTH_FILE"],
                                     "/run/dungeness/auth.json")
                    self.assertIn("${DUNGENESS_CODEX_AUTH_FILE:?provider access required}:"
                                  "/run/dungeness/auth.json:ro", gateway["volumes"])
                else:
                    self.assertNotIn("DUNGENESS_CHATGPT_AUTH_FILE", gateway["environment"])
        # Preserve the public URLs, including the historical ChatGPT alias.
        from model_access import gateway_base_url
        self.assertEqual(gateway_base_url("openai-chatgpt", "openai-responses"),
                         "http://gateway:8080/model/chatgpt/v1")
        self.assertEqual(gateway_base_url("claude-subscription", "anthropic-messages"),
                         "http://gateway:8080/model/claude-subscription")

    def test_new_recipe_compiles_stages_and_authenticates_without_compiler_branch(self):
        config = configured_provider("fixture", {
            "base_url": "https://fixture.invalid/v1", "credential_env": "FIXTURE_TOKEN",
            "credential_kind": "session-token", "credential_header": "x-api-key",
            "credential_prefix": "", "credential_headers": {"account-id": "FIXTURE_TOKEN_ACCOUNT"},
            "billed": False, "routes": ["chat/completions"], "headers": {},
            "models": {}, "model_header": None,
        })
        values = {"FIXTURE_TOKEN": "synthetic-private-token",
                  "FIXTURE_TOKEN_ACCOUNT": "synthetic-private-account",
                  "FIXTURE_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z"}
        with tempfile.TemporaryDirectory() as folder, patch.dict(MODEL_ACCESS, {"fixture": config}):
            root = Path(folder)
            (root / "environment").mkdir()
            compose = compiler.build_compose("recipe-contract", {}, BUDGET,
                command_policy={"models": [{**MODEL, "provider": "fixture",
                    "base_url": "http://gateway:8080/model/fixture/v1"}]})
            (root / "environment/docker-compose.yaml").write_text(compose)
            env_file = root / "access.env"
            env_file.write_text("\n".join("TESTBED_" + key + "=" + value for key, value in values.items()))
            with gateway_credentials(root, env_file, {}) as (environment, _):
                credential_path = Path(environment["DUNGENESS_CREDENTIALS_FILE"])
                self.assertEqual(json.loads(credential_path.read_text()), values)
                for value in values.values():
                    self.assertNotIn(value, compose + json.dumps(environment))
                with patch.dict(os.environ, {"DUNGENESS_CREDENTIALS_FILE": str(credential_path)}):
                    self.assertEqual(authentication_headers(config["authentication"]), {
                        "x-api-key": values["FIXTURE_TOKEN"], "account-id": values["FIXTURE_TOKEN_ACCOUNT"]})
            self.assertFalse(credential_path.exists())

    def test_multi_model_run_stages_only_selected_credentials(self):
        models = [{**MODEL, "provider": provider, "base_url": "http://gateway:8080/model/example/v1"}
                  for provider in ("openai-chatgpt", "openai", "anthropic")]
        compose = yaml.safe_load(compiler.build_compose(
            "multi-connection", {}, BUDGET, command_policy={"models": models}))
        gateway = compose["services"]["gateway"]
        self.assertEqual(gateway["x-dungeness-credential-env"], {
            "OPENAI_API_KEY": "TESTBED_OPENAI_API_KEY", "ANTHROPIC_API_KEY": "TESTBED_ANTHROPIC_API_KEY"})
        self.assertEqual(sum(isinstance(mount, str) and "DUNGENESS_CODEX_AUTH_FILE" in mount
                             for mount in gateway["volumes"]), 1)
        self.assertEqual(json.loads(gateway["environment"]["DUNGENESS_ALLOWED_MODELS"]),
                         [[model["provider"], model["request_model"]] for model in models])
