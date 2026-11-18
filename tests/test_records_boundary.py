"""Record storage works without importing execution or assuming a checkout root."""
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dungeness import records


class RecordsBoundaryTests(unittest.TestCase):
    def test_damaged_event_line_does_not_hide_completed_evaluations_or_cancellation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "record.json"
            records.write_json(path, {
                "data": {"run_id": "trial", "status": "running",
                         "metric": {"name": "accuracy", "direction": "maximize"}},
            })
            usage = root / "usage"
            usage.mkdir()
            event = {
                "source": "evaluator", "kind": "evaluation.completed",
                "data": {"status": "ok", "score": 42, "best_score": 42,
                         "submissions_used": 1, "candidate_sha256": "a" * 64},
            }
            valid = json.dumps(event).encode() + b"\n"
            damaged = b'{"kind":"evaluation.completed","data":{"message":"\xe2\x82'
            # UTF-8 writes can end mid-character. A malformed earlier line
            # must not prevent reading later complete events either.
            for contents in (valid + damaged, damaged + b"\n" + valid):
                with self.subTest(contents=contents):
                    events = usage / "events.jsonl"
                    events.write_bytes(contents)
                    records.finalize_run_record(
                        path, status="cancelled", error="interrupted",
                        execution_outcome=Mock(),
                    )
                    result = records.read_json(path)["data"]
                    self.assertEqual(result["status"], "cancelled")
                    self.assertEqual(result["error"], "interrupted")
                    self.assertEqual(result["evaluation"]["best_score"], 42)
                    self.assertEqual(result["metrics"], {"accuracy": 42})
                    self.assertNotIn("usage", result)
                    self.assertEqual(events.read_bytes(), contents)

    def test_import_has_no_execution_dependencies_or_filesystem_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-c", """
import sys
from dungeness import records
assert not any(name.startswith(('dungeness.execution', 'dungeness.compiler',
                                'gateway', 'harbor', 'yaml'))
               for name in sys.modules)
"""], cwd=directory, capture_output=True, text=True,
                env={"PATH": os.defpath, "PYTHONPATH": str(ROOT / "src"),
                     "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_explicit_storage_root_and_result_interpreter_preserve_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rendered = root / "rendered"
            records.write_json(rendered / "resolved-run.json", {
                "namespace": "users/example", "type": "run", "id": "trial",
                "data": {"run_id": "trial", "configuration": {}},
            })
            launcher = {"harbor_version": "synthetic", "keep_images": False}
            provenance = {"available": True, "dirty": False, "commit": "a" * 40}
            path = records.start_run_record(
                rendered, "trial", runs_root=root / "evidence",
                repository=provenance, launcher=launcher,
            )
            self.assertEqual(path, root / "evidence/users/example/trial/record.json")
            started = records.read_json(path)
            self.assertEqual(started["data"]["status"], "running")
            self.assertEqual(started["data"]["configuration"], {
                "repository": provenance, "launcher": launcher,
            })
            result = {"id": "synthetic-execution", "stats": {}}
            records.write_json(path.parent / "harbor/trial/result.json", result)
            outcome = Mock(return_value=("failed", "verification failed"))
            records.finalize_run_record(path, status="completed", execution_outcome=outcome)
            outcome.assert_called_once_with(result)
            finished = records.read_json(path)
            self.assertEqual(finished["data"]["status"], "failed")
            self.assertEqual(finished["data"]["error"], "verification failed")
            self.assertEqual(finished["data"]["execution"], result)
            self.assertEqual(finished["created_at"], started["created_at"])
            self.assertEqual(finished["published_at"], finished["data"]["finished_at"])
            self.assertEqual(list(path.parent.glob(".*.tmp")), [])

            outcome.reset_mock()
            records.finalize_run_record(
                path, status="cancelled", error="interrupted", execution_outcome=outcome,
            )
            outcome.assert_not_called()
            self.assertEqual(records.read_json(path)["data"]["status"], "cancelled")
            self.assertEqual(records.read_json(path)["data"]["error"], "interrupted")


if __name__ == "__main__":
    unittest.main()
