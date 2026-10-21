"""Versioned discovery uses the existing verified attachment transport."""
import hashlib
import json
import os
import unittest
from unittest.mock import patch

import httpx
from starlette.testclient import TestClient
from test_gateway import gateway_module


class AssignedResourceTests(unittest.TestCase):
    def request(self, path, *, raw=b'# Notes\n', query='', digest=None, upstream_status=200):
        expected = b'# Notes\n'
        paths = ['/ecdsa-fail/v1/resources/notes', '/ecdsa-fail/resources/notes']
        entries = [{'name': 'notes.md', 'media_type': 'text/markdown', 'bytes': len(expected),
                    'sha256': hashlib.sha256(expected).hexdigest(), 'paths': paths}]
        for name, endpoint in [('description.json', 'description'), ('resources.json', 'knowledge-base')]:
            entries.append({'name': name, 'media_type': 'application/json', 'bytes': 2,
                            'sha256': hashlib.sha256(b'{}').hexdigest(),
                            'paths': [f'/ecdsa-fail/v1/{endpoint}', f'/ecdsa-fail/{endpoint}']})
        payload = json.dumps({'schema_version': 1, 'attachments': entries}, sort_keys=True, separators=(',', ':')).encode()
        requests = []
        def upstream(request):
            requests.append(request)
            if request.url.path == '/task':
                return httpx.Response(200, content=payload)
            content = raw if request.url.path.endswith('notes.md') else b'{}'
            return httpx.Response(upstream_status, content=content, headers={'Location': 'https://attacker.invalid'})
        client_type = httpx.AsyncClient
        def client(**kwargs):
            self.assertFalse(kwargs['trust_env'])
            self.assertFalse(kwargs['follow_redirects'])
            return client_type(transport=httpx.MockTransport(upstream), **kwargs)
        with patch.dict(os.environ, {'DUNGENESS_TASK_SHA256': digest or hashlib.sha256(payload).hexdigest()}), \
                patch.object(gateway_module.httpx, 'AsyncClient', side_effect=client), \
                TestClient(gateway_module.app) as agent:
            response = agent.get(path + query, headers={'Authorization': 'Bearer never-forward'})
        self.assertTrue(all('authorization' not in request.headers for request in requests))
        self.assertTrue(all(request.url.host == 'problem' for request in requests))
        return response, requests

    def test_versioned_alias_and_legacy_urls_serve_identical_verified_bytes(self):
        for path in ['/ecdsa-fail/v1/resources/notes', '/ecdsa-fail/resources/notes', '/task/files/notes.md']:
            with self.subTest(path=path):
                response, requests = self.request(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b'# Notes\n')
                self.assertTrue(response.headers['content-type'].startswith('text/markdown'))
                self.assertEqual(response.headers['x-content-sha256'], hashlib.sha256(response.content).hexdigest())
                self.assertEqual(response.headers['content-disposition'], 'attachment; filename="notes.md"')
                self.assertEqual([r.url.path for r in requests], ['/task', '/task/files/notes.md'])
        for endpoint in ['description', 'knowledge-base']:
            for prefix in ['/ecdsa-fail/v1', '/ecdsa-fail']:
                response, _ = self.request(prefix + '/' + endpoint)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {})

    def test_unknown_releases_resources_and_queries_cannot_select_other_content(self):
        for path in ['/ecdsa-fail/v2/resources/notes', '/other/v1/resources/notes',
                     '/ecdsa-fail/v1/resources/missing', '/ecdsa-fail/v2/description']:
            response, requests = self.request(path)
            self.assertEqual(response.status_code, 404)
            self.assertTrue(all(r.url.path == '/task' for r in requests))
        response, requests = self.request('/ecdsa-fail/v1/resources/notes', query='?url=https://attacker.invalid')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(requests)

    def test_changed_bytes_changed_task_and_redirects_fail_closed(self):
        for options in [{'raw': b'forged!'}, {'raw': b''}, {'raw': b'# Notes\nextra'},
                        {'digest': 'a' * 64}, {'upstream_status': 302}]:
            response, _ = self.request('/ecdsa-fail/v1/resources/notes', **options)
            self.assertEqual(response.status_code, 502)
