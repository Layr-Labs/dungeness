"""Cross-run continuation preserves candidates and separates them from scores."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import unittest
from unittest.mock import patch

from test_record_model import REPOSITORY_ROOT, build, write_run_spec


class ResumeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.prior = self.root / "prior"
        self.workspace = self.prior / "harbor/job/trial/artifacts/workspace/repo"
        self.workspace.mkdir(parents=True)
        self.candidate = self.workspace / "solution"
        self.usage = self.prior / "usage"
        self.usage.mkdir()
        self.lookup = patch.object(build, "find_run_directory", return_value=self.prior)
        self.lookup.start()
        self.addCleanup(self.lookup.stop)

    def resolve(self, direction="maximize"):
        return build.resolve_resume_source("prior", [PurePosixPath("solution")], direction)

    def test_directory_candidate_and_fractional_score_history(self):
        self.candidate.mkdir()
        (self.candidate / "answer.txt").write_text("final candidate")
        (self.usage / "events.jsonl").write_text("".join(
            json.dumps({"kind": "evaluation.completed", "data": {"status": status, "score": score}}) + "\n"
            for status, score in [("ok", 0.125), ("ok", 0.75), ("error", 100), ("ok", 0.5)]
        ))
        (self.usage / "summary.json").write_text(json.dumps({"evaluation": {"best_score": 0.75}}))
        resumed = self.resolve()
        self.assertEqual(resumed["candidate_files"], {"solution": self.candidate})
        self.assertEqual(resumed["score_history"], [0.125, 0.75])
        self.assertEqual(resumed["best_score"], 0.75)
        self.assertEqual(self.resolve("minimize")["score_history"], [0.125])

    def test_resume_rejects_missing_candidate(self):
        with self.assertRaisesRegex(ValueError, "no candidate"):
            self.resolve()

    def test_resume_rejects_symlinks_and_special_files(self):
        outside = self.root / "outside"
        outside.write_text("outside candidate")
        self.candidate.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink|unsupported"):
            self.resolve()
        self.candidate.unlink()
        self.candidate.mkdir()
        nested = self.candidate / "nested"
        nested.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink|unsupported"):
            self.resolve()
        nested.unlink()
        os.mkfifo(nested)
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.resolve()

    def test_resume_rejects_symlinked_workspace_parent(self):
        self.workspace.rmdir()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "solution").write_text("outside workspace")
        self.workspace.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.resolve()

    def test_directory_digest_tracks_candidate_changes(self):
        self.candidate.mkdir()
        first = self.candidate / "a"
        first.write_bytes(b"first\x00payload")
        second = self.candidate / "b"
        second.write_bytes(b"second payload")
        original = build.resume_candidate_digest(self.candidate)
        # Creation order and timestamps do not change content identity.
        first.unlink()
        first.write_bytes(b"first\x00payload")
        self.assertEqual(build.resume_candidate_digest(self.candidate), original)
        second.write_bytes(b"changed payload")
        changed = build.resume_candidate_digest(self.candidate)
        self.assertNotEqual(changed, original)
        renamed = second.rename(self.candidate / "renamed")
        self.assertNotEqual(build.resume_candidate_digest(self.candidate), changed)
        changed = build.resume_candidate_digest(self.candidate)
        renamed.chmod(0o755)
        self.assertNotEqual(build.resume_candidate_digest(self.candidate), changed)

    def test_compiler_replaces_whole_candidate_and_hashes_rendered_copy(self):
        # A candidate may change shape between runs. Stale checkpoint files
        # must not survive a directory overlay or affect its recorded digest.
        for baseline_directory, resumed_directory in ((False, False), (True, True), (False, True), (True, False)):
            with self.subTest(baseline_directory=baseline_directory, resumed_directory=resumed_directory):
                if self.candidate.is_dir():
                    shutil.rmtree(self.candidate)
                elif self.candidate.exists():
                    self.candidate.unlink()
                if resumed_directory:
                    self.candidate.mkdir()
                    (self.candidate / "answer.txt").write_bytes(b"final\x00candidate")
                    (self.candidate / "empty").mkdir()
                else:
                    self.candidate.write_bytes(b"final\x00candidate")
                spec = self.root / "run.yaml"
                write_run_spec(spec)

                def checkout(_url, _commit, destination):
                    destination.mkdir(parents=True)
                    if destination.name == "start":
                        candidate = destination / "solution"
                        if baseline_directory:
                            candidate.mkdir()
                            (candidate / "stale.txt").write_text("old baseline")
                        else:
                            candidate.write_text("old baseline")
                        (destination / "trusted.txt").write_text("trusted baseline")
                    else:
                        (destination / "check.txt").write_text("trusted evaluator")

                rendered = None
                try:
                    with (
                        patch.object(build, "RUNS_ROOT", self.root / "runs"),
                        patch.object(build, "checkout", side_effect=checkout),
                        patch.object(build, "apply_evaluator_patches", return_value=[]),
                        patch.object(build, "commit_timestamp", return_value=datetime(2026, 5, 29, tzinfo=timezone.utc)),
                        redirect_stdout(io.StringIO()),
                    ):
                        rendered = build.build_task(
                            "sample-starter", f"resume-{baseline_directory}-{resumed_directory}",
                            agent_id="command", checkpoint="62ae3d0", namespace="users/bx",
                            run_spec=str(spec), resume_from="prior",
                        )
                    workspace = rendered / "environment/workspace"
                    candidate = workspace / "solution"
                    final_file = candidate / "answer.txt" if resumed_directory else candidate
                    self.assertEqual(final_file.read_bytes(), b"final\x00candidate")
                    self.assertFalse((candidate / "stale.txt").exists())
                    self.assertEqual((workspace / "trusted.txt").read_text(), "trusted baseline")
                    statement = (REPOSITORY_ROOT / "tasks/projects/dungeness/sample-starter/statement.txt").read_text()
                    self.assertTrue((rendered / "instruction.md").read_text().startswith(statement.rstrip()))
                    record = json.loads((rendered / "resolved-run.json").read_text())
                    resume = record["data"]["configuration"]["resolved"]["resume"]
                    digest = resume["candidate_sha256"]["solution"]
                    if resumed_directory:
                        self.assertTrue((candidate / "empty").is_dir())
                        # Repeat compilation must be independent of host paths.
                        self.assertEqual(digest, build.resume_candidate_digest(self.candidate))
                        (candidate / "empty").rmdir()
                        self.assertNotEqual(digest, build.resume_candidate_digest(candidate))
                    else:
                        self.assertEqual(digest, hashlib.sha256(b"final\x00candidate").hexdigest())
                finally:
                    if rendered is not None:
                        shutil.rmtree(rendered.parent)

    def test_continuation_distinguishes_final_candidate_from_historical_best(self):
        for direction, better in (("maximize", "higher"), ("minimize", "lower")):
            with self.subTest(direction=direction):
                notice = build.build_continuation_notice(
                    {"best_score": 0.875, "score_history": [0.125, 0.875]}, "solution", direction,
                )
                self.assertIn("final candidate", notice)
                self.assertIn("0.875", notice)
                self.assertIn("0.125", notice)
                self.assertIn(f"{better} is better", notice)
                self.assertIn("Evaluate", notice)
                self.assertNotIn("best solution", notice)
                self.assertNotIn("Its score", notice)
