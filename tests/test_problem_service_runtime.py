"""Generic task service: compilation and internal network contract, no Docker."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("problem_service_compiler", ROOT / "src/dungeness/compiler.py")
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)


class ProblemServiceRuntimeTests(unittest.TestCase):
    def test_attachment_bytes_paths_symlinks_and_undeclared_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = root / "source"
            (context / "files").mkdir(parents=True)
            (context / "Dockerfile").write_text("FROM trusted")
            (context / "server.py").write_text("pass")
            raw = b"%PDF-fixture"
            paper = context / "files/paper.pdf"
            paper.write_bytes(raw)
            entry = {"name": "paper.pdf", "bytes": len(raw), "media_type": "application/pdf",
                     "sha256": hashlib.sha256(raw).hexdigest()}
            def binding(attachments):
                payload = json.dumps({"schema_version": 1, "attachments": attachments},
                                     sort_keys=True, separators=(",", ":")).encode()
                (context / "task.json").write_bytes(payload)
                return {"context": "source", "sha256": hashlib.sha256(payload).hexdigest()}
            pin = binding([entry])
            compiler.resolve_problem_service(root, pin, root / "ok")
            for index, media_type in enumerate(('text/markdown', 'text/csv', 'application/zip')):
                compiler.resolve_problem_service(root, binding([{**entry, 'media_type': media_type}]), root / f'media-{index}')
            with self.assertRaises(ValueError):
                compiler.resolve_problem_service(root, binding([{**entry, 'media_type': 'text/plain\r\nX: injected'}]), root / 'invalid-media')
            for routes in ('/test/v1/resources/paper', ['/test/v1/resources/../paper'],
                           ['/test/v1/resources/paper'] * 2, ['https://attacker.invalid/paper']):
                with self.assertRaises(ValueError):
                    compiler.resolve_problem_service(root, binding([{**entry, 'paths': routes}]), root / 'invalid-routes')
            pin = binding([entry])
            paper.write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                compiler.resolve_problem_service(root, pin, root / "bad")
            paper.unlink()
            paper.symlink_to(root / "ok/files/paper.pdf")
            with self.assertRaises(ValueError):
                compiler.resolve_problem_service(root, pin, root / "symlink")
            paper.unlink()
            paper.write_bytes(raw)
            for entries in ([{**entry, "name": "../paper.pdf"}], [entry, entry], []):
                with self.assertRaises(ValueError):
                    compiler.resolve_problem_service(root, binding(entries), root / "unsafe")
            pin = binding([entry])
            (context / "files/secret.txt").write_text("not declared")
            with self.assertRaises(ValueError):
                compiler.resolve_problem_service(root, pin, root / "extra")

    def test_problem_service_is_read_only_and_reachable_only_through_gateway(self):
        compose = yaml.safe_load(compiler.build_compose(
            "test-run",
            {"historical_cutoff": {"end_published_date": "2026-05-28T23:59:59Z"},
             "search": {"max_results": 25}},
            {"web": {"searches": 0, "fetches": 0}, "model": {"requests": 10, "total_tokens": 10000}},
            problem_service={"context": "problem-service", "sha256": "a" * 64},
        ))
        problem = compose["services"]["problem"]
        gateway = compose["services"]["gateway"]
        self.assertTrue(problem["read_only"])
        self.assertEqual(problem["networks"], ["problem_internal"])
        self.assertNotIn("ports", problem)
        self.assertEqual(problem["cap_drop"], ["ALL"])
        self.assertTrue(compose["networks"]["problem_internal"]["internal"])
        self.assertIn("problem_internal", gateway["networks"])
        self.assertEqual(compose["services"]["main"]["networks"], ["agent_internal"])
        self.assertEqual(gateway["environment"]["DUNGENESS_TASK_SHA256"], "a" * 64)
        self.assertTrue(all(v.endswith(":ro") for v in problem["volumes"]))
        proxy_names = {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"}
        self.assertEqual(set(problem["environment"]), {"TASK_SHA256", "TASK_DOCUMENT", "NO_PROXY", "no_proxy"} | proxy_names)
        for service in compose["services"].values():
            self.assertTrue(all(service["environment"][name] == "" for name in proxy_names))
            self.assertEqual(service["environment"]["NO_PROXY"], "*")

    def test_health_probe_ignores_ambient_proxy(self):
        import os
        import subprocess
        import sys
        import threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        class Healthy(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.end_headers()
            def log_message(self, *args): pass
        compose = yaml.safe_load(compiler.build_compose(
            "health-probe", {}, {"model": {"requests": 1}},
            problem_service={"context": "problem-service", "sha256": "a" * 64}))
        with ThreadingHTTPServer(('127.0.0.1', 0), Healthy) as server:
            thread = threading.Thread(target=server.serve_forever); thread.start()
            try:
                code = compose['services']['problem']['healthcheck']['test'][-1]
                code = code.replace('localhost:8091', '127.0.0.1:' + str(server.server_port))
                env = {**os.environ, 'HTTP_PROXY': 'http://127.0.0.1:1',
                       'http_proxy': 'http://127.0.0.1:1', 'NO_PROXY': '', 'no_proxy': ''}
                result = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            finally:
                server.shutdown(); thread.join()

    def test_public_task_context_permissions_do_not_inherit_private_umask(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);context=root/'source';context.mkdir(mode=0o700)
            payload=b'{"schema_version":1,"statement":"public task"}'
            for name,data in [('task.json',payload),('server.py',b'pass'),('Dockerfile',b'FROM trusted')]:
                (context/name).write_bytes(data);(context/name).chmod(0o600)
            binding={'context':'source','sha256':hashlib.sha256(payload).hexdigest()}
            destination=root/'rendered'
            compiler.resolve_problem_service(root,binding,destination)
            self.assertEqual(destination.stat().st_mode & 0o777,0o755)
            self.assertEqual((destination/'task.json').stat().st_mode & 0o777,0o444)
            self.assertEqual((context/'task.json').stat().st_mode & 0o777,0o600)

    def test_compile_copies_only_a_pinned_regular_context(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = root / "source"
            context.mkdir()
            payload = b'{"schema_version":1,"statement":"immutable"}'
            (context / "task.json").write_bytes(payload)
            (context / "Dockerfile").write_text("FROM trusted")
            (context / "server.py").write_text("pass")
            binding = {"context": "source", "sha256": hashlib.sha256(payload).hexdigest()}
            result = compiler.resolve_problem_service(root, binding, root / "rendered")
            self.assertEqual(result["sha256"], binding["sha256"])
            self.assertEqual((root / "rendered/task.json").read_bytes(), payload)
            (context / "task.json").write_text('{"schema_version":1,"statement":"forged"}')
            with self.assertRaisesRegex(ValueError, "differs"):
                compiler.resolve_problem_service(root, binding, root / "second")
            (context / "task.json").unlink()
            (context / "task.json").symlink_to(root / "rendered/task.json")
            with self.assertRaisesRegex(ValueError, "Invalid"):
                compiler.resolve_problem_service(root, binding, root / "third")
            for value in (
                {"context": "../elsewhere", "sha256": "a" * 64},
                {"context": "source", "sha256": "a" * 64, "url": "http://attacker"},
            ):
                with self.assertRaises(ValueError):
                    compiler.problem_service_binding(value)
