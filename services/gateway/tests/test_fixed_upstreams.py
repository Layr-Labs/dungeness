"""Runtime configuration cannot redirect provider credentials to another origin."""
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
from gateway_runtime import Gateway
from model_access import MODEL_ACCESS, validate_upstream_settings


class FixedUpstreamTests(unittest.TestCase):
    def test_legacy_variables_can_only_repeat_the_registered_url(self):
        for provider, config in MODEL_ACCESS.items():
            variable = config["upstream_env"]
            with self.subTest(provider=provider):
                validate_upstream_settings({variable: config["upstream_default"]})
                validate_upstream_settings({variable: config["upstream_default"] + "/"})
                for url in ("", "http://localhost:9999/v1", "https://proxy.invalid/v1",
                            config["upstream_default"] + "/another-route",
                            config["upstream_default"] + "?key=private-sentinel"):
                    with self.assertRaisesRegex(ValueError, variable) as error:
                        validate_upstream_settings({variable: url})
                    self.assertNotIn("private-sentinel", str(error.exception))

    def test_override_rejected_before_gateway_resources_or_credentials_are_opened(self):
        with patch.dict(os.environ, {"OPENAI_UPSTREAM_BASE_URL": "https://proxy.invalid/v1"}), \
                patch("gateway_runtime.UsageLedger") as ledger, \
                patch("gateway_runtime.httpx.AsyncClient") as client:
            with self.assertRaisesRegex(ValueError, "fixed upstream"):
                Gateway()
            ledger.assert_not_called()
            client.assert_not_called()


class FixedUpstreamRequestTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_ignores_later_env_changes_and_does_not_follow_redirects(self):
        for redirect in (False, True):
            with self.subTest(redirect=redirect), tempfile.TemporaryDirectory() as folder, \
                    patch.dict(os.environ, {
                        "TESTBED_USAGE_DIR": folder,
                        "OPENAI_API_KEY": "synthetic-private-token",
                        "DUNGENESS_ALLOWED_MODELS": json.dumps([["openai", "gpt-6-astra"]]),
                        "OPENAI_UPSTREAM_BASE_URL": "https://api.openai.com/v1",
                    }):
                runtime = Gateway()
                await runtime.client.aclose()
                calls = []

                def upstream(request):
                    calls.append(request)
                    self.assertEqual(str(request.url), "https://api.openai.com/v1/responses")
                    self.assertEqual(request.headers["authorization"], "Bearer synthetic-private-token")
                    if redirect:
                        return httpx.Response(307, headers={"location": "https://proxy.invalid/steal"})
                    return httpx.Response(200, json={"output": [], "usage": {
                        "input_tokens": 2, "output_tokens": 1, "total_tokens": 3}})

                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream),
                                                  follow_redirects=False)
                try:
                    with patch.dict(os.environ, {"OPENAI_UPSTREAM_BASE_URL": "https://proxy.invalid/v1"}), \
                            patch.object(gateway, "gateway", runtime):
                        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                     base_url="http://gateway") as client:
                            response = await client.post("/model/openai/v1/responses",
                                json={"model": "gpt-6-astra", "input": "fixture"},
                                headers={"authorization": "Bearer caller-placeholder"})
                        self.assertEqual(len(calls), 1)
                        self.assertEqual(response.status_code, 502 if redirect else 200, response.text)
                        if redirect:
                            self.assertEqual(response.json()["error"]["upstream_status"], 307)
                            self.assertNotIn("location", response.headers)
                finally:
                    await runtime.client.aclose()
