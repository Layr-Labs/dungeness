"""Regression check for the gateway image's outbound HTTPS trust anchors."""
import hashlib
import os
import ssl
import tempfile
import unittest
from unittest.mock import patch

import certifi
import httpx

from gateway_runtime import Gateway


# emSign ECC Root CA - G3, removed by certifi 2026.10.19.
# Public certificate SHA-256, not a key or a hostname denylist.
RETIRED_ROOT = "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b"


class GatewayTrustTests(unittest.IsolatedAsyncioTestCase):
    async def test_model_and_task_clients_exclude_retired_root(self):
        expected = ssl.create_default_context(cafile=certifi.where())
        expected_roots = {
            hashlib.sha256(cert).hexdigest()
            for cert in expected.get_ca_certs(binary_form=True)
        }
        self.assertNotIn(RETIRED_ROOT, expected_roots)
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
            "TESTBED_RUN_ID": "tls-trust-test",
            "TESTBED_USAGE_DIR": directory,
            "EXA_END_PUBLISHED_DATE": "2026-10-22T00:00:00Z",
            "MAX_SEARCHES": "0",
            "MAX_FETCHES": "0",
            "MAX_MODEL_REQUESTS": "1",
            "MAX_MODEL_TOKENS": "1",
        }, clear=True):
            gateway = Gateway()
            try:
                async with httpx.AsyncClient(trust_env=False) as task_client:
                    for client in (gateway.client, task_client):
                        # HTTPX 0.28.1 is pinned in the image. Inspect the context
                        # actually handed to its connection pool, not system CAs.
                        context = client._transport._pool._ssl_context
                        roots = {
                            hashlib.sha256(cert).hexdigest()
                            for cert in context.get_ca_certs(binary_form=True)
                        }
                        self.assertEqual(roots, expected_roots)
                        self.assertNotIn(RETIRED_ROOT, roots)
                        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
                        self.assertTrue(context.check_hostname)
            finally:
                await gateway.client.aclose()
