"""Credential preparation contracts using synthetic inputs and real private files."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

from dungeness.credential_access import credential_requirements, prepare_credentials
from dungeness.contracts import model_providers
from dungeness.execution.credentials import gateway_credentials

ROOT = Path(__file__).resolve().parents[1]


class CredentialAccessTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.dict(os.environ, {"PATH": os.defpath}, clear=True))
        self.login = self.root / "login.json"
        self.login.write_text(json.dumps({"tokens": {
            "access_token": "synthetic-access",
            "account_id": "synthetic-account",
            "refresh_token": "must-stay-local",
            "id_token": "also-stays-local",
        }, "email": "private@example.invalid"}))
        self.login.chmod(0o600)

    def test_mixed_routes_stage_only_selected_inputs_and_authentication_fields(self):
        requirements = credential_requirements(["openai", "claude-subscription", "openai-chatgpt"])
        supplied = {
            "TESTBED_OPENAI_API_KEY": "synthetic-api",
            "TESTBED_CLAUDE_ACCESS_TOKEN": "synthetic-claude",
            "TESTBED_CLAUDE_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
            "DUNGENESS_CODEX_AUTH_FILE": str(self.login),
            "UNSELECTED_KEY": "must-not-stage",
        }
        with prepare_credentials(requirements, supplied) as (paths, empty):
            flat = Path(paths["DUNGENESS_CREDENTIALS_FILE"])
            account = Path(paths["DUNGENESS_CODEX_AUTH_FILE"])
            self.assertEqual(json.loads(flat.read_text()), {
                "OPENAI_API_KEY": "synthetic-api",
                "CLAUDE_ACCESS_TOKEN": "synthetic-claude",
                "CLAUDE_ACCESS_TOKEN_EXPIRES_AT": "2099-01-01T00:00:00Z",
            })
            self.assertEqual(json.loads(account.read_text()), {"tokens": {
                "access_token": "synthetic-access", "account_id": "synthetic-account"}})
            for path in (flat, account, empty):
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            self.assertNotEqual(account, self.login)
            self.login.unlink()
            self.assertTrue(account.exists(), "a run owns its staged credential snapshot")
            self.assertNotIn("synthetic-access", repr(paths) + empty.read_text())
        self.assertFalse(flat.parent.exists())

    def test_api_key_resolver_does_not_read_ambient_credentials(self):
        with patch.dict(os.environ, {"TESTBED_OPENAI_API_KEY": "ambient-secret"}):
            with self.assertRaisesRegex(ValueError, "TESTBED_OPENAI_API_KEY is missing"):
                with prepare_credentials(credential_requirements(["openai"]), {}):
                    self.fail("An explicit missing input must not choose an ambient account")

    def test_bad_file_does_not_fall_back_and_error_never_contains_path_or_values(self):
        requirements = credential_requirements(["openai-chatgpt"])
        link = self.root / "sensitive-path"
        link.symlink_to(self.login)
        for filename in (str(link), str(self.root / "missing-private-path")):
            with self.subTest(filename=filename), self.assertRaises(ValueError) as caught:
                with prepare_credentials(requirements, {"DUNGENESS_CODEX_AUTH_FILE": filename}):
                    self.fail("Invalid source must prevent preparation")
            self.assertIn("DUNGENESS_CODEX_AUTH_FILE", str(caught.exception))
            self.assertNotIn(filename, str(caught.exception))
        self.login.chmod(0o644)
        with self.assertRaises(ValueError):
            with prepare_credentials(requirements, {"DUNGENESS_CODEX_AUTH_FILE": str(self.login)}):
                self.fail("Publicly readable source must be rejected")

    def test_missing_fields_fail_without_leaking_credential_document(self):
        self.login.write_text('{"tokens":{"access_token":"private-sentinel"}}')
        with self.assertRaises(ValueError) as caught:
            with prepare_credentials(credential_requirements(["openai-chatgpt"]),
                                     {"DUNGENESS_CODEX_AUTH_FILE": str(self.login)}):
                self.fail("Missing account metadata must prevent preparation")
        self.assertNotIn("private-sentinel", str(caught.exception))

    def test_file_cleanup_on_cancellation_preserves_original_login(self):
        with self.assertRaises(KeyboardInterrupt):
            with prepare_credentials(credential_requirements(["openai-chatgpt"]),
                                     {"DUNGENESS_CODEX_AUTH_FILE": str(self.login)}) as (paths, _):
                staged = Path(paths["DUNGENESS_CODEX_AUTH_FILE"])
                raise KeyboardInterrupt
        self.assertFalse(staged.parent.exists())
        self.assertTrue(self.login.exists())

    def test_real_compiler_and_launcher_share_the_file_input_contract(self):
        from test_command_harness import compiler, MODEL
        (self.root / "environment").mkdir()
        (self.root / "environment/docker-compose.yaml").write_text(compiler.build_compose(
            "credential-access", {}, {"model": {"requests": 10, "total_tokens": 10000}},
            provider="openai-chatgpt", command_policy={"models": [
                {**MODEL, "base_url": "http://gateway:8080/model/chatgpt/v1"}]}))
        env_file = self.root / "access.env"
        env_file.write_text("DUNGENESS_CODEX_AUTH_FILE=" + str(self.login) + "\n")
        with gateway_credentials(self.root, env_file, {}) as (paths, _):
            staged = Path(paths["DUNGENESS_CODEX_AUTH_FILE"])
            self.assertNotEqual(staged, self.login)
            from gateway_auth import authentication_headers
            from model_access import MODEL_ACCESS
            with patch.dict(os.environ, {"DUNGENESS_CHATGPT_AUTH_FILE": str(staged)}):
                self.assertEqual(authentication_headers(MODEL_ACCESS["openai-chatgpt"]["authentication"]), {
                    "authorization": "Bearer synthetic-access",
                    "chatgpt-account-id": "synthetic-account",
                })
        self.assertFalse(staged.exists())
        self.assertTrue(self.login.exists())

    def test_older_render_keeps_existing_chatgpt_file_mount(self):
        (self.root / "environment").mkdir()
        (self.root / "environment/docker-compose.yaml").write_text(yaml.safe_dump({
            "services": {"gateway": {
                "x-dungeness-credential-env": {},
                "environment": {"DUNGENESS_CHATGPT_AUTH_FILE": "/run/dungeness/auth.json"},
                "volumes": ["${DUNGENESS_CODEX_AUTH_FILE:?required}:/run/dungeness/auth.json:ro"],
            }}}))
        env_file = self.root / "access.env"
        env_file.write_text("DUNGENESS_CODEX_AUTH_FILE=" + str(self.login) + "\n")
        with gateway_credentials(self.root, env_file, {}) as (paths, _):
            self.assertEqual(paths["DUNGENESS_CODEX_AUTH_FILE"], str(self.login))
        self.assertTrue(self.login.exists())

    def test_discovery_preserves_old_output_and_never_reads_private_sources(self):
        old = model_providers(ROOT)
        self.assertEqual(set(old), {"schema_version", "runtime", "providers"})
        # Describe through the same fresh-interpreter CLI integrators use, with
        # execution dependencies unavailable and an unusable ambient login.
        code = ("import runpy,sys; sys.modules['dotenv']=None; "
                "sys.argv=[sys.argv[1],'providers','--details']; "
                "runpy.run_path(sys.argv[0],run_name='__main__')")
        result = subprocess.run(
            [sys.executable, "-c", code, str(ROOT / "dungeness")],
            env={**os.environ, "DUNGENESS_CODEX_AUTH_FILE": "/must/not/read/private-login"},
            text=True, capture_output=True, check=True)
        details = json.loads(result.stdout)
        self.assertEqual(details["providers"], old["providers"])
        routes = {route["id"]: route for route in details["access_routes"]}
        self.assertEqual(routes["openai"]["upstream"], "https://api.openai.com/v1")
        self.assertEqual(routes["openai"]["credential_inputs"],
                         credential_requirements(["openai"]))
        self.assertIn("DUNGENESS_CODEX_AUTH_FILE", routes["openai-chatgpt"]["credential_inputs"]["files"])
        self.assertNotIn("/must/not/read/private-login", result.stdout)

    def test_alternative_authentication_sources_are_not_silently_combined(self):
        from model_access import MODEL_ACCESS
        config = {**MODEL_ACCESS["openai"], "authentication": {"sources": [
            {"headers": {"authorization": {"env": "FIRST_KEY"}}},
            {"headers": {"authorization": {"env": "SECOND_KEY"}}},
        ]}}
        with patch.dict(MODEL_ACCESS, {"synthetic": config}):
            with self.assertRaisesRegex(ValueError, "explicit authentication source selection"):
                credential_requirements(["synthetic"])
