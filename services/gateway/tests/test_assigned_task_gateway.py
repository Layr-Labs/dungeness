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
    async def file_request(self, data, *, name="paper.pdf", query=b"", status=200, expected_data=None):
        original = b"%PDF-fixture" if expected_data is None else expected_data
        entry = {"name": "paper.pdf", "sha256": hashlib.sha256(original).hexdigest(),
                 "bytes": len(original), "media_type": "application/pdf"}
        payload = json.dumps({"schema_version": 1, "attachments": [entry]},
                             sort_keys=True, separators=(",", ":")).encode()
        requests = []
        def upstream(request):
            requests.append(request)
            if request.url.path == "/task":
                return httpx.Response(200, content=payload)
            return httpx.Response(status, content=data, headers={"location": "http://attacker.invalid/"})
        client_type = httpx.AsyncClient
        def client(**kwargs):
            self.assertFalse(kwargs["trust_env"])
            self.assertFalse(kwargs["follow_redirects"])
            return client_type(transport=httpx.MockTransport(upstream), **kwargs)
        incoming = Request({
            "type": "http", "method": "GET", "scheme": "http", "path": "/task/files/" + name,
            "path_params": {"name": name}, "query_string": query,
            "headers": [(b"authorization", b"Bearer never-forward")], "server": ("gateway", 8080),
        })
        with patch.dict(os.environ, {"DUNGENESS_TASK_SHA256": hashlib.sha256(payload).hexdigest()}), \
                patch.object(gateway_module.httpx, "AsyncClient", side_effect=client):
            response = await gateway_module.assigned_file(incoming)
            body = (b"".join([chunk async for chunk in response.body_iterator])
                    if response.status_code == 200 else response.body)
        return response, body, requests

    async def test_task_files_are_digest_verified_without_forwarding_credentials(self):
        response, body, requests = await self.file_request(b"%PDF-fixture")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, b"%PDF-fixture")
        self.assertEqual([str(r.url) for r in requests],
                         ["http://problem:8091/task", "http://problem:8091/task/files/paper.pdf"])
        self.assertTrue(all("authorization" not in r.headers for r in requests))
        self.assertEqual(response.headers["x-content-sha256"], hashlib.sha256(body).hexdigest())

    async def test_file_unknown_paths_query_redirects_and_changed_bytes_fail_closed(self):
        for kwargs, status in (
            ({"name": "unknown.pdf"}, 404), ({"name": "../secret"}, 404),
            ({"query": b"url=http://attacker"}, 400), ({"status": 302}, 502),
        ):
            response, body, requests = await self.file_request(b"%PDF-fixture", **kwargs)
            self.assertEqual(response.status_code, status)
            self.assertNotIn(b"%PDF-fixture", body)
            if status in (400, 404):
                self.assertTrue(all(r.url.path == "/task" for r in requests))
        for data in (b"%PDF-forged!", b"", b"%PDF-fixture-overflow"):
            response, body, _ = await self.file_request(data)
            self.assertEqual(response.status_code, 502)
            self.assertNotEqual(body, data)

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
