from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("render_gateway_transcript.py")
SPEC = importlib.util.spec_from_file_location(
    "watcher_renderer_under_test",
    MODULE_PATH,
)
assert SPEC is not None and SPEC.loader is not None
renderer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = renderer
SPEC.loader.exec_module(renderer)

SERVER_MODULE_PATH = Path(__file__).with_name("serve_gateway_transcripts.py")
SERVER_SPEC = importlib.util.spec_from_file_location(
    "watcher_server_under_test",
    SERVER_MODULE_PATH,
)
assert SERVER_SPEC is not None and SERVER_SPEC.loader is not None
server = importlib.util.module_from_spec(SERVER_SPEC)
sys.modules[SERVER_SPEC.name] = server
SERVER_SPEC.loader.exec_module(server)


def request(
    index: int,
    request_id: str,
    timestamp: datetime,
    command: str | None = None,
) -> object:
    response = renderer.Response(available=True)
    if command is not None:
        response.tool_calls.append(
            renderer.ToolCall(
                call_id=f"call-{index}",
                name="Bash",
                arguments="{}",
                command=command,
            )
        )
    return renderer.RequestView(
        index=index,
        request_id=request_id,
        timestamp=timestamp,
        provider="test",
        model="test",
        operation="messages",
        messages=[],
        tool_names=[],
        prompt_profile=None,
        response=response,
        response_timestamp=timestamp,
    )


class RunDiscoveryTests(unittest.TestCase):
    def test_discovers_runs_nested_below_a_runs_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            immediate = root / "immediate-run"
            nested = root / "contaminiated" / "nested-run"
            immediate.mkdir()
            nested.mkdir(parents=True)
            (immediate / "record.json").write_text("{}", encoding="utf-8")
            (nested / "record.json").write_text("{}", encoding="utf-8")

            discovered = server.discover_runs(root, [])

            self.assertEqual(discovered["immediate-run"], immediate.resolve())
            self.assertEqual(discovered["nested-run"], nested.resolve())


class RunOrderingTests(unittest.TestCase):
    def test_snapshot_sorts_by_recorded_start_instead_of_file_activity(
        self,
    ) -> None:
        registry = server.TranscriptRegistry([], None)
        older = server.RunState(
            run_id="older-run",
            run_dir=Path("/tmp/older-run"),
            summary={"started_at": "2026-09-10T12:00:00Z"},
            last_activity=datetime(2026, 9, 12, tzinfo=timezone.utc),
        )
        newer = server.RunState(
            run_id="newer-run",
            run_dir=Path("/tmp/newer-run"),
            summary={"started_at": "2026-09-11T12:00:00Z"},
            last_activity=datetime(2026, 9, 9, tzinfo=timezone.utc),
        )
        registry.runs = {
            older.run_id: older,
            newer.run_id: newer,
        }

        self.assertEqual(
            [state.run_id for state in registry.snapshot()],
            ["newer-run", "older-run"],
        )

    def test_snapshot_falls_back_to_timestamp_in_run_id(self) -> None:
        registry = server.TranscriptRegistry([], None)
        older = server.RunState(
            run_id="example-20260910T120000Z-older",
            run_dir=Path("/tmp/older-run"),
            last_activity=datetime(2026, 9, 12, tzinfo=timezone.utc),
        )
        newer = server.RunState(
            run_id="example-20260911T120000Z-newer",
            run_dir=Path("/tmp/newer-run"),
            last_activity=datetime(2026, 9, 9, tzinfo=timezone.utc),
        )
        registry.runs = {
            older.run_id: older,
            newer.run_id: newer,
        }

        self.assertEqual(
            [state.run_id for state in registry.snapshot()],
            [newer.run_id, older.run_id],
        )


class ProgressRailTests(unittest.TestCase):
    def run_data(self) -> object:
        first = datetime(2026, 9, 4, 1, 0, tzinfo=timezone.utc)
        second = datetime(2026, 9, 4, 1, 1, tzinfo=timezone.utc)
        return renderer.RunData(
            run_dir=Path("/tmp/example-run"),
            run_id="example-run",
            requests=[
                request(
                    1,
                    "request-1",
                    first,
                    "cd /workspace/repo && evaluate",
                ),
                request(2, "request-2", second),
            ],
            record={"data": {"status": "completed"}},
            evals=[
                {
                    "status": "ok",
                    "score": 123456789,
                    "candidate_sha256": "a" * 64,
                    "cumulative_usage": {"normalized_usd": 1.25},
                }
            ],
            research_state=[],
            gateway_events=[],
            delivery_events=[],
            kb_events=[
                {
                    "event": "knowledge_base_request",
                    "action": "read",
                    "page": "README.md",
                    "bytes": 1200,
                    "observed_at": "2026-09-04T01:00:30Z",
                }
            ],
        )

    def test_evaluate_command_detection(self) -> None:
        self.assertTrue(
            renderer.command_invokes_evaluate(
                "cd /workspace/repo && candidate-state save baseline "
                "&& evaluate 2>&1 | tail -40"
            )
        )
        self.assertTrue(
            renderer.command_invokes_evaluate(
                "timeout 600 evaluate src/point_add"
            )
        )
        self.assertFalse(
            renderer.command_invokes_evaluate("rg -n evaluate README.md")
        )

    def test_evaluation_marker_uses_invoking_request(self) -> None:
        run = self.run_data()
        markers = renderer.build_markers(run)
        evaluation = next(
            marker for marker in markers if marker.kind == "evaluation"
        )
        self.assertEqual(evaluation.request_id, "request-1")
        self.assertTrue(evaluation.after_request)
        self.assertIn("score 123,456,789", evaluation.label)

        slots, unplaced = renderer.place_markers(run, markers)
        self.assertFalse(unplaced)
        self.assertIn(evaluation, slots[2])

    def test_render_includes_right_progress_rail(self) -> None:
        document = renderer.Renderer(self.run_data()).render()
        self.assertIn('class="progress-sidebar"', document)
        self.assertIn(
            ".progress-sidebar{min-width:0;position:sticky",
            document,
        )
        self.assertIn(
            ".progress-sidebar{position:static;max-height:none",
            document,
        )
        self.assertIn('id="progress-current"', document)
        self.assertIn(
            "evaluation #1: ok score 123,456,789",
            document,
        )
        self.assertIn("knowledge-base read: README.md", document)
        self.assertIn("1</b> evaluations", document)
        self.assertIn("1</b> KB calls", document)
        self.assertIn(
            "Evaluation score and KB activity versus cumulative spend",
            document,
        )
        self.assertIn('"cumulative_usd":1.25', document)
        self.assertIn('"knowledge_base":[', document)
        self.assertIn("knowledge-base activity", document)
        self.assertIn("drawEvalTrajectory()", document)

    def test_trajectory_falls_back_to_model_usage_cost(self) -> None:
        run = self.run_data()
        run.evals[0].pop("cumulative_usage")
        run.requests[0].accounting = {
            "input_tokens": 1_000_000,
            "cached_input_tokens": 500_000,
            "output_tokens": 10_000,
        }

        points = renderer.evaluation_trajectory_points(run)

        self.assertEqual(len(points), 1)
        self.assertAlmostEqual(points[0]["cumulative_usd"], 3.05)
        self.assertEqual(
            points[0]["cost_source"],
            "gateway accounting timeline",
        )

    def test_unknown_eval_cost_is_not_rendered_as_zero(self) -> None:
        run = self.run_data()
        run.requests = []
        run.evals[0].pop("cumulative_usage")

        points = renderer.evaluation_trajectory_points(run)

        self.assertIsNone(points[0]["cumulative_usd"])
        self.assertEqual(points[0]["cost_source"], "unavailable")

    def test_legacy_rollout_places_evals_and_kb_on_gateway_cost_timeline(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            rollout = (
                run_dir
                / "harbor/job/task__abc/agent/sessions/2026/09/08"
                / "rollout-test.jsonl"
            )
            rollout.parent.mkdir(parents=True)
            records = [
                {
                    "timestamp": "2026-09-08T01:00:10Z",
                    "type": "event_msg",
                    "payload": {
                        "item": {
                            "type": "CommandExecution",
                            "command": [
                                "/bin/bash",
                                "-lc",
                                "knowledge-base read README.md",
                            ],
                            "stdout": "knowledge base page",
                        }
                    },
                },
                {
                    "timestamp": "2026-09-08T01:00:20Z",
                    "type": "event_msg",
                    "payload": {
                        "item": {
                            "type": "CommandExecution",
                            "command": ["/bin/bash", "-lc", "evaluate"],
                            "stdout": (
                                "status: ok\nscore: 100\n"
                                "submissions remaining: 199\n"
                            ),
                        }
                    },
                },
                {
                    "timestamp": "2026-09-08T01:01:20Z",
                    "type": "event_msg",
                    "payload": {
                        "item": {
                            "type": "CommandExecution",
                            "command": ["/bin/bash", "-lc", "evaluate"],
                            "stdout": (
                                "status: ok\nscore: 80\n"
                                "submissions remaining: 198\n"
                            ),
                        }
                    },
                },
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )
            eval_timestamps, kb_timestamps = (
                renderer.load_legacy_action_timestamps(run_dir)
            )

            first = request(
                1,
                "request-1",
                datetime(2026, 9, 8, 1, 0, tzinfo=timezone.utc),
            )
            first.accounting = {"normalized_usd": 0.4}
            second = request(
                2,
                "request-2",
                datetime(2026, 9, 8, 1, 1, tzinfo=timezone.utc),
            )
            second.accounting = {"normalized_usd": 0.6}
            run = renderer.RunData(
                run_dir=run_dir,
                run_id="legacy-run",
                requests=[first, second],
                record={"data": {"status": "completed"}},
                evals=[
                    {"status": "ok", "score": 100},
                    {"status": "ok", "score": 80},
                ],
                research_state=[],
                gateway_events=[],
                delivery_events=[],
                kb_events=[
                    {
                        "event": "knowledge_base_request",
                        "action": "read",
                        "page": "README.md",
                    }
                ],
                legacy_eval_timestamps=eval_timestamps,
                legacy_kb_timestamps=kb_timestamps,
            )

            markers = renderer.build_markers(run)
            data = renderer.evaluation_trajectory_data(
                run,
                markers,
                {"total_usd": 1.0},
            )

            self.assertEqual(len(eval_timestamps), 2)
            self.assertEqual(len(kb_timestamps), 1)
            self.assertEqual(
                [point["cumulative_usd"] for point in data["points"]],
                [0.4, 1.0],
            )
            self.assertEqual(
                data["knowledge_base"][0]["cumulative_usd"],
                0.4,
            )
            self.assertEqual(
                data["knowledge_base"][0]["detail"],
                "README.md",
            )

    def test_load_run_prefers_canonical_event_stream(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            usage = run_dir / "usage"
            usage.mkdir()
            (run_dir / "record.json").write_text(
                json.dumps(
                    {
                        "id": "canonical-run",
                        "data": {
                            "status": "completed",
                            "metric": {"direction": "minimize"},
                        },
                    }
                ),
                encoding="utf-8",
            )
            events = [
                {
                    "schema_version": 1,
                    "run_id": "canonical-run",
                    "sequence": 1,
                    "source": "gateway",
                    "kind": "model.request",
                    "observed_at": "2026-09-05T01:00:00Z",
                    "recorded_at": "2026-09-05T01:00:00Z",
                    "request_id": "request-1",
                    "data": {
                        "provider": "openai",
                        "operation": "responses",
                        "model": "gpt-5.6-sol",
                        "prompt_profile": {"bytes": 20},
                        "request": {
                            "model": "gpt-5.6-sol",
                            "input": "hello",
                        },
                    },
                },
                {
                    "schema_version": 1,
                    "run_id": "canonical-run",
                    "sequence": 2,
                    "source": "gateway",
                    "kind": "model.response",
                    "observed_at": "2026-09-05T01:00:01Z",
                    "recorded_at": "2026-09-05T01:00:01Z",
                    "request_id": "request-1",
                    "data": {
                        "provider": "openai",
                        "operation": "responses",
                        "model": "gpt-5.6-sol",
                        "status": "success",
                        "response": [],
                        "usage": {"total_tokens": 15},
                    },
                },
                {
                    "schema_version": 1,
                    "run_id": "canonical-run",
                    "sequence": 3,
                    "source": "gateway",
                    "kind": "model.accounting",
                    "observed_at": "2026-09-05T01:00:01Z",
                    "recorded_at": "2026-09-05T01:00:01Z",
                    "request_id": "request-1",
                    "data": {
                        "provider": "openai",
                        "model": "gpt-5.6-sol",
                        "total_tokens": 15,
                        "normalized_usd": 0.01,
                    },
                },
                {
                    "schema_version": 1,
                    "run_id": "canonical-run",
                    "sequence": 4,
                    "source": "evaluator",
                    "kind": "evaluation.completed",
                    "observed_at": "2026-09-05T01:00:02Z",
                    "recorded_at": "2026-09-05T01:00:02Z",
                    "event_id": "evaluation:1",
                    "data": {
                        "operation": "score",
                        "status": "ok",
                        "score": 42,
                    },
                    "usage": {"normalized_usd": 0.01},
                },
                {
                    "schema_version": 1,
                    "run_id": "canonical-run",
                    "sequence": 5,
                    "source": "knowledge-base",
                    "kind": "knowledge_base.request",
                    "observed_at": "2026-09-05T01:00:03Z",
                    "recorded_at": "2026-09-05T01:00:03Z",
                    "event_id": "knowledge-base:1",
                    "data": {"action": "read", "page": "README.md"},
                },
            ]
            (usage / "events.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events),
                encoding="utf-8",
            )

            run = renderer.load_run(run_dir)
            self.assertEqual(len(run.requests), 1)
            self.assertEqual(run.requests[0].accounting["total_tokens"], 15)
            self.assertEqual(run.evals[0]["score"], 42)
            self.assertEqual(
                run.evals[0]["cumulative_usage"]["normalized_usd"],
                0.01,
            )
            self.assertEqual(run.kb_events[0]["action"], "read")
            self.assertFalse(run.warnings)

    def test_final_verifier_score_is_loaded_and_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            usage = run_dir / "usage"
            usage.mkdir()
            (run_dir / "record.json").write_text(
                json.dumps(
                    {
                        "id": "final-run",
                        "data": {
                            "status": "failed",
                            "finished_at": "2026-09-08T21:31:52Z",
                            "metric": {
                                "name": "ecdsafail_score",
                                "direction": "minimize",
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            (usage / "eval-events.jsonl").write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "score": 7_297_268_598,
                        "observed_at": "2026-09-08T21:00:00Z",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            harbor = run_dir / "harbor" / "final-run"
            trial = harbor / "task__abc"
            trial.mkdir(parents=True)
            job_result = harbor / "result.json"
            job_result.write_text(
                json.dumps(
                    {
                        "finished_at": "2026-09-08T14:31:51",
                        "stats": {
                            "evals": {
                                "codex__test": {
                                    "metrics": [{"mean": 4_099_273_784}],
                                    "reward_stats": {
                                        "ecdsafail_score": {
                                            "4099273784.0": ["task__abc"]
                                        }
                                    },
                                }
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            trial_result = trial / "result.json"
            trial_result.write_text(
                json.dumps(
                    {
                        "finished_at": "2026-09-08T21:31:51Z",
                        "verifier_result": {
                            "rewards": {
                                "ecdsafail_score": 4_099_273_784
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            run = renderer.load_run(run_dir)
            summary = renderer.summarize_run(run)
            markers = renderer.build_markers(run)
            document = renderer.Renderer(run).render()

            self.assertEqual(run.verifier_score, 4_099_273_784)
            self.assertEqual(run.verifier_metric, "ecdsafail_score")
            self.assertEqual(
                run.verifier_finished_at,
                datetime(2026, 9, 8, 21, 31, 52, tzinfo=timezone.utc),
            )
            self.assertEqual(
                summary["best_evaluation_score"],
                7_297_268_598,
            )
            self.assertEqual(
                summary["final_verifier_score"],
                4_099_273_784,
            )
            self.assertEqual(summary["result_score"], 4_099_273_784)
            verifier = next(
                marker for marker in markers if marker.kind == "verifier"
            )
            self.assertIn("score 4,099,273,784", verifier.label)
            self.assertIn("best evaluation 7,297,268,598", verifier.detail)
            self.assertIn(
                "final verifier (authoritative)</span> "
                "<b>4,099,273,784</b>",
                document,
            )
            self.assertIn("final verifier: score 4,099,273,784", document)
            self.assertIn(
                '"score":4099273784.0,"cumulative_usd":0.0',
                document,
            )
            self.assertIn(job_result, server.tracked_files(run_dir))
            self.assertIn(trial_result, server.tracked_files(run_dir))


class LiveReloadTests(unittest.TestCase):
    def test_run_page_has_silent_live_reload_without_visible_live_box(self) -> None:
        state = server.RunState(
            run_id="example-run",
            run_dir=Path("/tmp/example-run"),
            version="version-1",
            html="<html><body><main>transcript</main></body></html>",
        )

        document = server.render_run_page(state, poll_ms=5000)

        self.assertNotIn('id="dgt-live"', document)
        self.assertNotIn('id="dgt-dot"', document)
        self.assertNotIn('id="dgt-poll"', document)
        self.assertIn("/api/run/", document)
        self.assertIn("setInterval(poll,pollMs)", document)
        self.assertIn("dgt-scroll:", document)

    def test_index_prefers_final_verifier_and_retains_best_eval(self) -> None:
        registry = server.TranscriptRegistry([], None)
        state = server.RunState(
            run_id="final-run",
            run_dir=Path("/tmp/final-run"),
            version="version-1",
            summary={
                "status": "budget exhausted",
                "requests": 158,
                "evaluations": 7,
                "evaluations_valid": 7,
                "evaluations_invalid": 0,
                "best_score": 7_297_268_598,
                "best_evaluation_score": 7_297_268_598,
                "final_verifier_score": 4_099_273_784,
                "result_score": 4_099_273_784,
                "score_source": "final verifier",
            },
            last_activity=datetime(2026, 9, 8, 21, 31, tzinfo=timezone.utc),
        )
        registry.runs[state.run_id] = state

        document = server.render_index(registry)

        self.assertIn("<th>result score</th>", document)
        self.assertIn("4,099,273,784", document)
        self.assertIn("final verifier", document)
        self.assertIn("best eval 7,297,268,598", document)


if __name__ == "__main__":
    unittest.main()
