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
        self.assertEqual(set(problem["environment"]), {"TASK_SHA256", "TASK_DOCUMENT"})

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
