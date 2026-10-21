"""Trusted credentials cannot be replaced by the submitted harness."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
from gateway_auth import authentication_headers
from gateway_models import MODEL_PROVIDERS, provider_auth_headers, configured_provider_config
from configured_fixture import FIXTURES
from gateway_runtime import Gateway


class AuthenticationTests(unittest.TestCase):
    def test_same_resolver_handles_bearer_api_key_and_account_metadata(self):
        for header, prefix in (("authorization", "Bearer "), ("x-api-key", "")):
            recipe = {"sources": [{"headers": {
                header: {"env": "EXAMPLE_TOKEN", "prefix": prefix},
                "example-account-id": {"env": "EXAMPLE_ACCOUNT"},
            }}]}
            with self.subTest(header=header), patch.dict(os.environ, {
                "EXAMPLE_TOKEN": "private-key", "EXAMPLE_ACCOUNT": "account-7",
            }):
                self.assertEqual(authentication_headers(recipe), {header: prefix + "private-key", "example-account-id": "account-7"})

    def test_unknown_provider_does_not_reuse_default_credentials(self):
        with self.assertRaisesRegex(ValueError, "Unknown authentication provider"):
            provider_auth_headers("unknown-provider")

    def test_missing_or_invalid_environment_never_falls_back_to_request(self):
        recipe = {"sources": [{"headers": {
            "authorization": {"env": "EXAMPLE_TOKEN", "prefix": "Bearer "},
        }}]}
        for value in ("", "secret\r\nInjected: value"):
            with self.subTest(value=repr(value)), patch.dict(os.environ, {"EXAMPLE_TOKEN": value}):
                with self.assertRaisesRegex(ValueError, "authentication"):
                    authentication_headers(recipe)

    def test_expiry_is_independent_of_provider_and_billing(self):
        recipe = {"sources": [{
            "headers": {"authorization": {"env": "EXAMPLE_TOKEN", "prefix": "Bearer "}},
            "expires_at": {"env": "EXAMPLE_EXPIRY"},
        }]}
        with patch.dict(os.environ, {"EXAMPLE_TOKEN": "private-key"}):
            for expiry in ("", "invalid", "2000-01-01T00:00:00Z", "2099-01-01T00:00:00"):
                with self.subTest(expiry=expiry), patch.dict(os.environ, {"EXAMPLE_EXPIRY": expiry}):
                    with self.assertRaisesRegex(ValueError, "expired"):
                        authentication_headers(recipe)
            with patch.dict(os.environ, {"EXAMPLE_EXPIRY":
                    (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}):
                self.assertEqual(authentication_headers(recipe), {"authorization": "Bearer private-key"})

    def test_invalid_configured_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "DUNGENESS_CHATGPT_AUTH_FILE": str(Path(temp) / "auth.json"),
        }):
            path = Path(temp) / "auth.json"
            for content in (None, "{", '{"tokens":{}}',
                            '{"tokens":{"access_token":"secret\\u0000","account_id":"account"}}',
                            '{"tokens":{"access_token":"secret","account_id":"bad\\r\\naccount"}}'):
                with self.subTest(content=content):
                    if content is not None:
                        path.write_text(content)
                    with self.assertRaises(ValueError):
                        provider_auth_headers("openai-chatgpt")

    def test_missing_trusted_file_fails_closed(self):
        with patch.dict(os.environ, {"DUNGENESS_CHATGPT_AUTH_FILE": ""}):
            with self.assertRaisesRegex(ValueError, "source is unavailable"):
                provider_auth_headers("openai-chatgpt")


class AuthenticationBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_configured_authentication_does_not_depend_on_provider_name(self):
        profile = {**FIXTURES["example-session"],
                   "credential_kind": "api-key",
                   "credential_header": "x-api-key", "credential_prefix": "",
                   "credential_headers": {"account-id": "EXAMPLE_SESSION_TOKEN_ACCOUNT"}}
        cfg = configured_provider_config("example-session", profile)
        # The provider's name does not determine its authentication mechanism.
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp, "EXAMPLE_SESSION_TOKEN": "private-key",
            "EXAMPLE_SESSION_TOKEN_ACCOUNT": "account-7",
        }), patch.dict(MODEL_PROVIDERS, {"example-session": cfg}):
            self.assertEqual(provider_auth_headers("example-session"), {"x-api-key": "private-key", "account-id": "account-7"})

    async def test_trusted_file_overrides_agent_account_and_token(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
            "TESTBED_USAGE_DIR": temp, "DUNGENESS_ALLOWED_MODELS": '[["openai-chatgpt","gpt-6-astra"]]',
            "DUNGENESS_CHATGPT_AUTH_FILE": str(Path(temp) / "auth.json"),
            "MAX_MODEL_REQUESTS": "10", "MAX_MODEL_TOKENS": "100000",
        }):
            Path(temp, "auth.json").write_text(json.dumps({"tokens": {
                "access_token": "private-test-token", "account_id": "trusted-account",
            }}))
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []
            def upstream(request):
                calls.append(request)
                self.assertEqual(request.headers["authorization"], "Bearer private-test-token")
                self.assertEqual(request.headers["chatgpt-account-id"], "trusted-account")
                self.assertEqual(request.url.host, "chatgpt.com")
                return httpx.Response(200, json={"output": [], "usage": {
                    "input_tokens": 2, "output_tokens": 1, "total_tokens": 3}})
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        reply = await client.post("/model/chatgpt/v1/responses",
                            json={"model": "gpt-6-astra", "input": "test"},
                            headers={"authorization": "Bearer attacker", "chatgpt-account-id": "other-account"})
                        self.assertEqual(reply.status_code, 200, reply.text)
                        Path(temp, "auth.json").unlink()
                        denied = await client.post("/model/chatgpt/v1/responses",
                            json={"model": "gpt-6-astra", "input": "test"},
                            headers={"authorization": "Bearer attacker"})
                        self.assertEqual(denied.status_code, 400, denied.text)
                        # Unconfigured credentials must not enable the old bearer passthrough.
                        with patch.dict(os.environ, {"DUNGENESS_CHATGPT_AUTH_FILE": ""}):
                            denied = await client.post("/model/chatgpt/v1/responses",
                                json={"model": "gpt-6-astra", "input": "test"},
                                headers={"authorization": "Bearer attacker", "chatgpt-account-id": "other-account"})
                            self.assertEqual(denied.status_code, 400, denied.text)
                self.assertEqual(len(calls), 1)
                self.assertEqual(runtime.ledger.counts["model_requests"], 1)
                events = Path(temp, "events.jsonl").read_text()
                self.assertNotIn("private-test-token", events)
                self.assertNotIn("trusted-account", events)
            finally:
                await runtime.client.aclose()
