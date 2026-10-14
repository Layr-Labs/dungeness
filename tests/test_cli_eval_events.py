from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


cli = load_module("dungeness_eval_cli", REPOSITORY_ROOT / "dungeness")


class EvaluationEventsCommandTests(unittest.TestCase):
    def make_run(self, root: Path) -> tuple[Path, list[str]]:
        run_dir = root / "runs/users/bx/example-run"
        usage_dir = run_dir / "usage"
        usage_dir.mkdir(parents=True)
        (run_dir / "record.json").write_text(
            json.dumps(
                {
                    "id": "example-run",
                    "type": "run",
                    "namespace": "users/bx",
                    "data": {"run_id": "example-run"},
                }
            ),
            encoding="utf-8",
        )
        records = [
            {
                "schema_version": 1,
                "run_id": "example-run",
                "sequence": 1,
                "source": "gateway",
                "kind": "model.accounting",
                "observed_at": "2026-09-05T01:00:00Z",
                "data": {"normalized_usd": 0.01},
            },
            {
                "schema_version": 1,
                "run_id": "example-run",
                "sequence": 2,
                "source": "evaluator",
                "kind": "evaluation.completed",
                "observed_at": "2026-09-05T01:01:00Z",
                "event_id": "evaluation:1",
                "data": {
                    "status": "ok",
                    "score": 42,
                    "best_score": 42,
                    "avg_toffoli": 21,
                    "peak_qubits": 2,
                    "candidate_sha256": "a" * 64,
                    "submissions_used": 1,
                    "submissions_limit": 200,
                },
                "usage": {"normalized_usd": 0.125},
            },
            {
                "schema_version": 1,
                "run_id": "example-run",
                "sequence": 3,
                "source": "evaluator",
                "kind": "evaluation.completed",
                "observed_at": "2026-09-05T01:02:00Z",
                "event_id": "evaluation:2",
                "data": {
                    "status": "invalid",
                    "score": 1e18,
                    "best_score": 42,
                    "candidate_sha256": "b" * 64,
                    "submissions_used": 2,
                    "submissions_limit": 200,
                },
                "usage": {"normalized_usd": 0.5},
            },
        ]
        lines = [
            json.dumps(record, separators=(",", ":"))
            for record in records
        ]
        (usage_dir / "events.jsonl").write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )
        return run_dir, lines

    def test_copy_paste_command_targets_exact_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir, _lines = self.make_run(root)
            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                command = cli.evaluation_events_command(run_dir)
            finally:
                cli.REPO_ROOT = previous_root

        self.assertEqual(
            command,
            "./dungeness evals runs/users/bx/example-run",
        )

    def test_human_output_accepts_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_run(root)
            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                output = io.StringIO()
                with redirect_stdout(output):
                    result = cli.show_evaluations(
                        argparse.Namespace(target="example-run", jsonl=False)
                    )
            finally:
                cli.REPO_ROOT = previous_root

        self.assertEqual(result, 0)
        text = output.getvalue()
        self.assertIn("eval 1/200", text)
        self.assertIn("score=42", text)
        self.assertIn("usd=$0.125", text)
        self.assertIn("toffoli=21", text)
        self.assertIn("eval 2/200", text)
        self.assertIn("invalid", text)
        self.assertNotIn("model.accounting", text)

    def test_jsonl_output_preserves_matching_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir, lines = self.make_run(root)
            output = io.StringIO()
            with redirect_stdout(output):
                result = cli.show_evaluations(
                    argparse.Namespace(target=str(run_dir), jsonl=True)
                )

        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().splitlines(), lines[1:])


if __name__ == "__main__":
    unittest.main()
