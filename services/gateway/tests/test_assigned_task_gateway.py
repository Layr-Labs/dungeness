"""A task request cannot choose an upstream or change the pinned document."""
import hashlib
import json
import os
import unittest
from unittest.mock import patch

import httpx
from starlette.requests import Request
from test_gateway import gateway_module


class AssignedTaskGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def fetch(self, payload, *, status=200, digest=None, query=b""):
        requests = []

        def upstream(request):
            requests.append(request)
            return httpx.Response(status, content=payload,
                                  headers={"location": "http://attacker.invalid/"})

        expected = digest or hashlib.sha256(payload).hexdigest()
        client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        incoming = Request({
            "type": "http", "method": "GET", "scheme": "http", "path": "/task",
            "query_string": query, "headers": [(b"authorization", b"Bearer private-model-token")],
            "server": ("gateway", 8080),
        })
        with patch.dict(os.environ, {"DUNGENESS_TASK_SHA256": expected}), \
                patch.object(gateway_module.httpx, "AsyncClient", return_value=client):
            response = await gateway_module.assigned_task(incoming)
        await client.aclose()
        return response, requests

    async def test_serves_pinned_document_without_forwarding_credentials(self):
        payload = b'{"schema_version":1,"statement":"trusted"}'
        response, requests = await self.fetch(payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, payload)
        self.assertEqual(str(requests[0].url), "http://problem:8091/task")
        self.assertNotIn("authorization", requests[0].headers)

    async def test_rejects_changed_oversized_redirected_or_selected_tasks(self):
        for payload, status, digest in (
            (b'{"schema_version":1,"statement":"forged"}', 200, "a" * 64),
            (b" " * (256 * 1024 + 1), 200, "a" * 64),
            (b"", 302, "a" * 64),
        ):
            response, requests = await self.fetch(payload, status=status, digest=digest)
            self.assertEqual(response.status_code, 502)
            self.assertEqual(len(requests), 1)
        response, requests = await self.fetch(b"{}", query=b"problem=other")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(requests)
