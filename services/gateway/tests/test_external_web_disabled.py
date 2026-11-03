"""Retired web operations must not use credentials, network or budget."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
from gateway_runtime import Gateway


class ExternalWebDisabledTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_and_fetch_cannot_be_enabled_by_keys_or_budgets(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                "TESTBED_USAGE_DIR": directory, "EXA_API_KEY": "synthetic-retired-key",
                "EXA_END_PUBLISHED_DATE": "not-a-date", "EXA_MAX_RESULTS": "invalid",
                "MAX_SEARCHES": "100", "MAX_FETCHES": "100"}):
            runtime = Gateway()
            await runtime.client.aclose()
            calls = []
            def upstream(request):
                calls.append(request)
                raise AssertionError("External web request reached a provider")
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            before = dict(runtime.ledger.counts)
            try:
                with patch.object(gateway, "gateway", runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),
                                                 base_url="http://gateway") as client:
                        for route in ("/web/search", "/web/fetch"):
                            for body in (b"{}", b"not-json", json.dumps({
                                    "query": "test", "url": "http://attacker.invalid",
                                    "api_key": "synthetic-retired-key"}).encode()):
                                reply = await client.post(route, content=body)
                                self.assertEqual(reply.status_code, 410)
                                self.assertEqual(reply.json()["error"]["code"], "external_web_disabled")
                                self.assertFalse(reply.json()["error"]["retryable"])
                                self.assertNotIn("synthetic-retired-key", reply.text)
                        self.assertEqual((await client.get("/healthz")).status_code, 200)
                for operation in (runtime.search, runtime.fetch):
                    with self.assertRaisesRegex(ValueError, "disabled"):
                        await operation("test")
                self.assertEqual(calls, [])
                self.assertEqual(runtime.ledger.counts, before)
                for path in Path(directory).rglob("*"):
                    if path.is_file():
                        self.assertNotIn(b"synthetic-retired-key", path.read_bytes())
            finally:
                await runtime.client.aclose()
