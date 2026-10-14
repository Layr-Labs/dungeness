from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


def controller_config(
    *,
    web_mode: str = "enforce_minimum",
    evaluation_mode: str = "enforce_minimum",
    feedback_mode: str | None = None,
    metric_direction: str = "minimize",
    baseline_score: float | None = None,
) -> dict:
    controls = {
        "web_search": {
            "mode": web_mode,
            "level": "medium",
            "minimum": 2,
            "soft_min": 2,
            "soft_max": 3,
            "global_limit": 10,
        },
        "evaluation": {
            "mode": evaluation_mode,
            "level": "medium",
            "minimum": 4,
            "soft_min": 4,
            "soft_max": 6,
            "global_limit": 10,
        },
    }
    config = {
        "run_id": "research-state-test",
        "profile": "research-state-profile:system/dungeness/bounded-smoke-v1",
        "profile_sha256": "0" * 64,
        "controls": controls,
        "safeguards": {
            "max_stop_interventions": 4,
            "max_stalled_interventions": 2,
            "finalization_reserve_sec": 0,
        },
        "metric_direction": metric_direction,
        "agent_timeout_sec": 3600,
        "model_budget": {
            "total_tokens": 1000,
            "normalized_usd": 10.0,
        },
    }
    if feedback_mode is not None:
        config["kb_behavior_feedback"] = {
            "enabled": True,
            "mode": feedback_mode,
            "minimum_improvement": 0,
            "kb_attribution_window_evaluations": 1,
            "no_progress_evaluations": 3,
            "expose_pre_stick_counter": True,
            "baseline_score": baseline_score,
        }
    return config


class ResearchStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module_directory = tempfile.TemporaryDirectory()
        environment = {
            "TESTBED_USAGE_DIR": cls.module_directory.name,
            "RESEARCH_STATE_CONFIG_JSON": json.dumps(controller_config()),
        }
        with patch.dict(os.environ, environment):
            cls.controller_module = load_module(
                "dungeness_research_state_server_test",
                REPOSITORY_ROOT / "services/research-state/server.py",
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.module_directory.cleanup()

    def new_state(self, config: dict | None = None):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return self.controller_module.ResearchState(
            config or controller_config(),
            Path(directory.name),
        )

    def test_search_normalization_and_duplicate_counting(self) -> None:
        state = self.new_state()
        first = state.apply_web_event(
            {
                "event_id": "search-1",
                "query": "  Kaliski   inversion? ",
                "status": "success",
            }
        )
        self.assertTrue(first["accepted"])
        state.apply_web_event(
            {
                "event_id": "search-2",
                "query": "kaliski inversion",
                "status": "success",
            }
        )
        replay = state.apply_web_event(
            {
                "event_id": "search-2",
                "query": "different",
                "status": "success",
            }
        )
        self.assertEqual(
            state.summary()["web_search"]["qualifying_distinct"], 1
        )
        self.assertEqual(state.summary()["web_search"]["duplicates"], 1)
        self.assertTrue(replay["duplicate_event"])

    def test_evaluation_deduplicates_candidates_and_tracks_best(self) -> None:
        state = self.new_state()
        state.apply_evaluation_event(
            {
                "event_id": "eval-1",
                "candidate_sha256": "a" * 64,
                "status": "valid",
                "score": 100,
            }
        )
        state.apply_evaluation_event(
            {
                "event_id": "eval-2",
                "candidate_sha256": "a" * 64,
                "status": "valid",
                "score": 90,
            }
        )
        state.apply_evaluation_event(
            {
                "event_id": "eval-3",
                "candidate_sha256": "b" * 64,
                "status": "invalid",
                "score": 0,
            }
        )
        summary = state.summary()["evaluation"]
        self.assertEqual(summary["qualifying_distinct"], 2)
        self.assertEqual(summary["duplicates"], 1)
        self.assertEqual(summary["valid"], 1)
        self.assertEqual(summary["invalid"], 1)
        self.assertEqual(summary["best_score"], 100)
        self.assertEqual(summary["best_candidate_sha256"], "a" * 64)

    def test_model_usage_creates_linear_evaluation_debt(self) -> None:
        state = self.new_state()
        state.apply_model_usage_event(
            {
                "event_id": "usage-1",
                "model_requests": 5,
                "model_tokens": 500,
                "normalized_usd": 4.0,
            }
        )
        cadence = state.model_view()["evaluation"]["cadence"]
        self.assertEqual(cadence["required_now"], 2)
        self.assertEqual(cadence["debt"], 2)
        self.assertEqual(cadence["remaining_final_minimum"], 4)
        web_cadence = state.model_view()["web_search"]["cadence"]
        self.assertEqual(web_cadence["required_now"], 1)
        self.assertEqual(web_cadence["debt"], 1)
        self.assertEqual(web_cadence["remaining_final_minimum"], 2)

        state.apply_evaluation_event(
            {
                "event_id": "eval-1",
                "candidate_sha256": "a" * 64,
                "status": "valid",
                "score": 100,
            }
        )
        cadence = state.model_view()["evaluation"]["cadence"]
        self.assertEqual(cadence["debt"], 1)
        self.assertEqual(cadence["remaining_final_minimum"], 3)

    def test_model_usage_snapshots_are_monotonic(self) -> None:
        state = self.new_state()
        state.apply_model_usage_event(
            {
                "event_id": "usage-newer",
                "model_requests": 8,
                "model_tokens": 750,
                "normalized_usd": 7.5,
            }
        )
        state.apply_model_usage_event(
            {
                "event_id": "usage-older",
                "model_requests": 7,
                "model_tokens": 700,
                "normalized_usd": 7.0,
            }
        )
        usage = state.model_view()["model_usage"]
        self.assertEqual(usage["requests"], 8)
        self.assertEqual(usage["tokens"], 750)
        self.assertEqual(usage["normalized_usd"], 7.5)

    def test_completion_blocks_then_accepts_at_both_minimums(self) -> None:
        state = self.new_state()
        first = state.completion_attempt({"attempt_id": "stop-1"})
        self.assertEqual(first["decision"], "block")
        self.assertIn("web search: 2 more", first["reason"])
        self.assertIn("evaluation: 4 more", first["reason"])

        for index in range(2):
            state.apply_web_event(
                {
                    "event_id": f"search-{index}",
                    "query": f"query {index}",
                    "status": "success",
                }
            )
        for index in range(4):
            state.apply_evaluation_event(
                {
                    "event_id": f"eval-{index}",
                    "candidate_sha256": f"{index:064x}",
                    "status": "valid",
                    "score": 100 - index,
                }
            )
        accepted = state.completion_attempt({"attempt_id": "stop-2"})
        self.assertEqual(accepted["decision"], "accept")
        self.assertTrue(accepted["compliance"])
        self.assertTrue(state.model_view()["completion_eligible"])

    def test_prompt_only_never_blocks(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
            )
        )
        result = state.completion_attempt({"attempt_id": "stop-1"})
        self.assertEqual(result["decision"], "accept")
        self.assertTrue(result["compliance"])

    def test_shadow_feedback_is_recorded_but_never_shown_to_the_model(
        self,
    ) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="shadow",
            )
        )
        for index, score in enumerate((100, 101, 102, 103)):
            state.apply_evaluation_event({
                "event_id": f"shadow-{index}",
                "candidate_sha256": f"{index + 1:064x}",
                "status": "valid",
                "score": score,
            })
        self.assertNotIn("kb_behavior_feedback", state.model_view())
        summary = state.summary()["kb_behavior_feedback"]
        self.assertEqual(summary["last_feedback_type"], "stick")
        self.assertFalse(summary["latest_feedback"]["visible_to_agent"])

    def test_maximize_direction_treats_a_higher_score_as_progress(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
                metric_direction="maximize",
            )
        )
        state.apply_evaluation_event({
            "event_id": "baseline",
            "candidate_sha256": "1" * 64,
            "status": "valid",
            "score": 100,
        })
        state.apply_knowledge_base_inspiration_event({
            "event_id": "maximize-lookup",
            "kb_lookup_id": "kb_100",
            "query": "raise the reported accuracy",
            "query_sha256": "b" * 64,
            "result_count": 2,
            "new_passage_count": 1,
            "qualifying": True,
            "takeaway": "Widen the search over ancilla schedules.",
            "planned_change": "Apply the wider schedule search.",
        })
        state.apply_evaluation_event({
            "event_id": "higher",
            "candidate_sha256": "2" * 64,
            "status": "valid",
            "score": 110,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["last_feedback_type"], "carrot")
        self.assertEqual(feedback["best_score"], 110.0)
        self.assertIn("Improvement: 10.0", feedback["latest_feedback"]["message"])

    def test_baseline_score_lets_the_first_evaluation_earn_a_carrot(
        self,
    ) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
                baseline_score=100,
            )
        )
        state.apply_knowledge_base_inspiration_event({
            "event_id": "seeded-lookup",
            "kb_lookup_id": "kb_101",
            "query": "shrink the inversion live width",
            "query_sha256": "c" * 64,
            "result_count": 2,
            "new_passage_count": 1,
            "qualifying": True,
            "takeaway": "Free the coefficient register early.",
            "planned_change": "Release it before the callback.",
        })
        state.apply_evaluation_event({
            "event_id": "first",
            "candidate_sha256": "1" * 64,
            "status": "valid",
            "score": 90,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["carrot_count"], 1)
        self.assertEqual(feedback["best_score"], 90.0)

    def test_duplicate_candidate_does_not_advance_the_feedback_clock(
        self,
    ) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        for index, score in enumerate((100, 101)):
            state.apply_evaluation_event({
                "event_id": f"distinct-{index}",
                "candidate_sha256": f"{index + 1:064x}",
                "status": "valid",
                "score": score,
            })
        before = state.model_view()["kb_behavior_feedback"]
        state.apply_evaluation_event({
            "event_id": "resubmission",
            "candidate_sha256": f"{1:064x}",
            "status": "valid",
            "score": 100,
        })
        after = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(
            after["evaluation_index"], before["evaluation_index"]
        )
        self.assertEqual(
            after["uninspired_stall_count"],
            before["uninspired_stall_count"],
        )

    def test_qualifying_lookup_clears_an_answered_stick(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        for index, score in enumerate((100, 101, 102, 103)):
            state.apply_evaluation_event({
                "event_id": f"stall-{index}",
                "candidate_sha256": f"{index + 1:064x}",
                "status": "valid",
                "score": score,
            })
        self.assertEqual(
            state.model_view()["kb_behavior_feedback"]["last_feedback_type"],
            "stick",
        )
        state.apply_knowledge_base_inspiration_event({
            "event_id": "answering-lookup",
            "kb_lookup_id": "kb_102",
            "query": "alternative point addition schedule",
            "query_sha256": "f" * 64,
            "result_count": 3,
            "new_passage_count": 2,
            "qualifying": True,
            "takeaway": "Reorder the additions around the inversion.",
            "planned_change": "Rewrite the schedule accordingly.",
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertIsNone(feedback["latest_feedback"])
        self.assertEqual(feedback["last_feedback_type"], "none")
        self.assertEqual(feedback["stick_count"], 1)

    def test_kb_attributed_improvement_emits_carrot(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        state.apply_evaluation_event({
            "event_id": "baseline",
            "candidate_sha256": "1" * 64,
            "status": "valid",
            "score": 100,
        })
        state.apply_knowledge_base_inspiration_event({
            "event_id": "lookup-event",
            "kb_lookup_id": "kb_004",
            "query": "replay Euclid history without coefficient registers",
            "query_sha256": "a" * 64,
            "result_count": 4,
            "new_passage_count": 2,
            "qualifying": True,
            "takeaway": "Replay branch history against modular registers.",
            "planned_change": "Prototype history replay in the inversion wrapper.",
        })
        state.apply_evaluation_event({
            "event_id": "improved",
            "candidate_sha256": "2" * 64,
            "status": "valid",
            "score": 90,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["last_feedback_type"], "carrot")
        self.assertEqual(feedback["carrot_count"], 1)
        self.assertIn("Previous best: 100.0", feedback["latest_feedback"]["message"])

    def test_three_uninspired_stalls_emit_stick(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        for index, score in enumerate((100, 101, 100, 103)):
            state.apply_evaluation_event({
                "event_id": f"eval-{index}",
                "candidate_sha256": f"{index + 1:064x}",
                "status": "valid",
                "score": score,
            })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["last_feedback_type"], "stick")
        self.assertEqual(feedback["stick_count"], 1)
        self.assertEqual(feedback["uninspired_stall_count"], 0)

    def test_qualifying_lookup_interrupts_stick_window(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        for index, score in enumerate((100, 101, 102)):
            state.apply_evaluation_event({
                "event_id": f"pre-{index}",
                "candidate_sha256": f"{index + 1:064x}",
                "status": "valid",
                "score": score,
            })
        self.assertEqual(
            state.model_view()["kb_behavior_feedback"][
                "uninspired_stall_count"
            ],
            2,
        )
        state.apply_knowledge_base_inspiration_event({
            "event_id": "lookup-event",
            "kb_lookup_id": "kb_005",
            "query": "specific companion code register sharing",
            "query_sha256": "b" * 64,
            "result_count": 2,
            "new_passage_count": 1,
            "qualifying": True,
            "takeaway": "Borrow the denominator register.",
            "planned_change": "Use the companion-code aliasing schedule.",
        })
        state.apply_evaluation_event({
            "event_id": "post-lookup",
            "candidate_sha256": "4" * 64,
            "status": "valid",
            "score": 103,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["last_feedback_type"], "neutral")
        self.assertEqual(feedback["stick_count"], 0)
        self.assertEqual(feedback["uninspired_stall_count"], 1)

    def test_progress_without_kb_emits_no_carrot(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        for index, score in enumerate((100, 90)):
            state.apply_evaluation_event({
                "event_id": f"eval-{index}",
                "candidate_sha256": f"{index + 1:064x}",
                "status": "valid",
                "score": score,
            })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["carrot_count"], 0)
        self.assertEqual(feedback["last_feedback_type"], "none")

    def test_failed_evaluation_does_not_advance_feedback_state(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        state.apply_evaluation_event({
            "event_id": "failed",
            "candidate_sha256": "1" * 64,
            "status": "failed",
            "score": None,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["evaluation_index"], 0)
        self.assertIsNone(feedback["best_score"])

    def test_baseline_consumes_kb_attribution_without_carrot(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        state.apply_knowledge_base_inspiration_event({
            "event_id": "lookup-before-baseline",
            "kb_lookup_id": "kb_006",
            "query": "specific inversion companion implementation",
            "query_sha256": "c" * 64,
            "result_count": 1,
            "new_passage_count": 1,
            "qualifying": True,
            "takeaway": "Use the callback's released state register.",
            "planned_change": "Alias that register during multiplication.",
        })
        state.apply_evaluation_event({
            "event_id": "baseline",
            "candidate_sha256": "1" * 64,
            "status": "valid",
            "score": 100,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["carrot_count"], 0)
        self.assertEqual(feedback["last_feedback_type"], "none")
        self.assertEqual(
            feedback["kb_attribution_evaluations_remaining"],
            0,
        )

    def test_nonqualifying_lookup_does_not_interrupt_stick_window(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        for index, score in enumerate((100, 101, 102)):
            state.apply_evaluation_event({
                "event_id": f"pre-empty-{index}",
                "candidate_sha256": f"{index + 1:064x}",
                "status": "valid",
                "score": score,
            })
        state.apply_knowledge_base_inspiration_event({
            "event_id": "nonqualifying-lookup",
            "kb_lookup_id": "kb_007",
            "query": "generic overview",
            "query_sha256": "d" * 64,
            "result_count": 1,
            "new_passage_count": 0,
            "qualifying": False,
            "takeaway": "No new implementation detail.",
            "planned_change": "No concrete candidate change.",
            "reason": "duplicate_passages_only",
        })
        state.apply_evaluation_event({
            "event_id": "third-stall",
            "candidate_sha256": "4" * 64,
            "status": "valid",
            "score": 103,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["last_feedback_type"], "stick")
        self.assertEqual(feedback["stick_count"], 1)

    def test_kb_without_progress_emits_neutral_not_carrot(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
                feedback_mode="visible",
            )
        )
        state.apply_evaluation_event({
            "event_id": "baseline",
            "candidate_sha256": "1" * 64,
            "status": "valid",
            "score": 100,
        })
        state.apply_knowledge_base_inspiration_event({
            "event_id": "lookup-no-progress",
            "kb_lookup_id": "kb_008",
            "query": "companion code register allocation",
            "query_sha256": "e" * 64,
            "result_count": 2,
            "new_passage_count": 1,
            "qualifying": True,
            "takeaway": "Try the companion register allocation.",
            "planned_change": "Apply the allocation to the inversion wrapper.",
        })
        state.apply_evaluation_event({
            "event_id": "worse",
            "candidate_sha256": "2" * 64,
            "status": "valid",
            "score": 105,
        })
        feedback = state.model_view()["kb_behavior_feedback"]
        self.assertEqual(feedback["last_feedback_type"], "neutral")
        self.assertEqual(feedback["carrot_count"], 0)
        self.assertEqual(feedback["uninspired_stall_count"], 1)

    def test_interrupt_marks_only_active_state(self) -> None:
        active = self.new_state()
        self.assertEqual(active.interrupt()["status"], "interrupted")

        completed = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
            )
        )
        completed.completion_attempt({"attempt_id": "stop-1"})
        self.assertEqual(
            completed.interrupt()["status"], "completed_compliant"
        )

    def test_concurrent_distinct_events_are_not_lost(self) -> None:
        state = self.new_state()
        threads = [
            threading.Thread(
                target=state.apply_web_event,
                args=(
                    {
                        "event_id": f"search-{index}",
                        "query": f"query {index}",
                        "status": "success",
                    },
                ),
            )
            for index in range(8)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(
            state.summary()["web_search"]["qualifying_distinct"], 8
        )

    def test_hook_subprocess_injects_context_and_blocks_completion(self) -> None:
        state = self.new_state()
        previous_state = self.controller_module.STATE
        self.controller_module.STATE = state
        server = self.controller_module.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            self.controller_module.Handler,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.addCleanup(setattr, self.controller_module, "STATE", previous_state)
        environment = {
            **os.environ,
            "DUNGENESS_RESEARCH_STATE_URL": (
                f"http://127.0.0.1:{server.server_port}"
            ),
        }
        hook = REPOSITORY_ROOT / "agents/common/research_state_hook.py"
        session = subprocess.run(
            [sys.executable, str(hook), "session-start"],
            input=json.dumps({"session_id": "session-1"}),
            text=True,
            capture_output=True,
            env=environment,
            check=True,
        )
        session_output = json.loads(session.stdout)
        context = session_output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Current Dungeness research-effort state", context)
        self.assertIn('"qualifying_completed": 0', context)

        stop = subprocess.run(
            [sys.executable, str(hook), "stop"],
            input=json.dumps(
                {
                    "session_id": "session-1",
                    "turn_id": "turn-1",
                    "last_assistant_message": "done",
                }
            ),
            text=True,
            capture_output=True,
            env=environment,
            check=True,
        )
        stop_output = json.loads(stop.stdout)
        self.assertEqual(stop_output["decision"], "block")

    def test_profile_rendering_and_compose_are_isolated(self) -> None:
        build = load_module(
            "dungeness_harbor_build_research_state_test",
            REPOSITORY_ROOT / "adapters/harbor/build.py",
        )
        _, _, resolved = build.resolve_research_state(
            {
                "profile": (
                    "research-state-profile:system/dungeness/"
                    "bounded-smoke-v1"
                ),
                "controls": {
                    "web_search": {
                        "mode": "prompt_only",
                        "level": "medium",
                    },
                    "evaluation": {
                        "mode": "enforce_minimum",
                        "level": "medium",
                    },
                },
            }
        )
        notice = build.build_research_state_notice(resolved)
        self.assertIn("Web-search effort: **MEDIUM**", notice)
        self.assertIn("Authoritative-evaluation effort: **MEDIUM**", notice)
        compose = build.yaml.safe_load(
            build.build_compose(
                "research-state-compose-test",
                {
                    "historical_cutoff": {
                        "end_published_date": "2026-05-28T23:59:59.999Z",
                    },
                    "search": {"max_results": 25},
                },
                {
                    "web": {"searches": 10, "fetches": 10},
                    "model": {"requests": 10, "total_tokens": 1000},
                    "evaluation": {"submissions": 10},
                },
                dev_scorer={
                    "context": "eval-sidecar",
                    "submissions": 10,
                    "port": 8090,
                },
                agent_timeout_sec=600,
                research_state=resolved,
                max_usd=12,
            )
        )
        controller = compose["services"]["research-state"]
        self.assertEqual(controller["networks"], ["agent_internal"])
        self.assertNotIn("external_egress", controller["networks"])
        self.assertEqual(
            compose["services"]["main"]["environment"][
                "DUNGENESS_RESEARCH_STATE_URL"
            ],
            "http://research-state:8079",
        )
        self.assertEqual(
            compose["services"]["gateway"]["environment"][
                "DUNGENESS_RESEARCH_STATE_URL"
            ],
            "http://research-state:8079",
        )
        config = json.loads(
            controller["environment"]["RESEARCH_STATE_CONFIG_JSON"]
        )
        self.assertEqual(
            config["controls"]["web_search"]["global_limit"], 10
        )
        self.assertEqual(
            config["controls"]["evaluation"]["global_limit"], 10
        )
        self.assertEqual(config["model_budget"]["total_tokens"], 1000)
        self.assertEqual(config["model_budget"]["normalized_usd"], 12)

    def test_codex_hook_configuration_covers_state_lifecycle(self) -> None:
        module = load_module(
            "dungeness_codex_gateway_research_state_test",
            REPOSITORY_ROOT / "adapters/harbor/codex_gateway.py",
        )
        hooks = json.loads(module.research_state_hooks_document())
        self.assertEqual(
            set(hooks["hooks"]),
            {"SessionStart", "PreToolUse", "Stop"},
        )
        command = module.install_research_state_hooks_command(
            "/tmp/codex-home"
        )
        self.assertIn("DUNGENESS_RESEARCH_STATE_URL", command)
        self.assertIn("/tmp/codex-home/hooks.json", command)
        runner = module.build_instrumented_codex_command(
            model="k3",
            instruction="test",
            cli_flags="",
            codex_home="/tmp/codex-home",
            agent_dir="/tmp/agent",
            output_filename="codex.txt",
            turn_timeout_sec=60,
        )
        self.assertIn('raw_runner_status=$?', runner)
        self.assertIn('"/finalize"', runner)
        self.assertIn(
            '[ "$raw_runner_status" -eq 0 ]',
            runner,
        )

    def test_normal_codex_exit_finalizes_research_state(self) -> None:
        state = self.new_state(
            controller_config(
                web_mode="prompt_only",
                evaluation_mode="prompt_only",
            )
        )
        previous_state = self.controller_module.STATE
        self.controller_module.STATE = state
        server = self.controller_module.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            self.controller_module.Handler,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.addCleanup(setattr, self.controller_module, "STATE", previous_state)

        module = load_module(
            "dungeness_codex_gateway_finalize_test",
            REPOSITORY_ROOT / "adapters/harbor/codex_gateway.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent_dir = root / "agent"
            agent_dir.mkdir()
            executable = root / "codex"
            executable.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' '{\"type\":\"turn.completed\"}'\n",
                encoding="utf-8",
            )
            executable.chmod(0o755)
            runner = module.build_instrumented_codex_command(
                model="k3",
                instruction="test",
                cli_flags="",
                codex_home=str(agent_dir),
                agent_dir=str(agent_dir),
                output_filename="codex.txt",
            )
            environment = {
                **os.environ,
                "PATH": f"{root}:{os.environ['PATH']}",
                "DUNGENESS_RESEARCH_STATE_URL": (
                    f"http://127.0.0.1:{server.server_port}"
                ),
            }
            subprocess.run(
                ["/bin/bash", "-c", runner],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
        self.assertEqual(state.summary()["status"], "completed_compliant")
        self.assertEqual(state.interrupt()["status"], "completed_compliant")

    def test_bounded_smoke_run_spec_selects_two_enforced_knobs(self) -> None:
        build = load_module(
            "dungeness_harbor_build_research_state_spec_test",
            REPOSITORY_ROOT / "adapters/harbor/build.py",
        )
        path = (
            REPOSITORY_ROOT
            / "run-specs/users/bx/"
            "ecdsa-kimi-subscription-research-state-bounded-smoke/"
            "ecdsa-kimi-subscription-research-state-bounded-smoke.yaml"
        )
        document = build.load_yaml(path)
        _, _, resolved = build.resolve_research_state(
            document["research_state"]
        )
        self.assertEqual(
            resolved["controls"]["web_search"]["minimum"], 2
        )
        self.assertEqual(
            resolved["controls"]["evaluation"]["minimum"], 4
        )
        self.assertEqual(
            resolved["controls"]["web_search"]["mode"],
            "enforce_minimum",
        )
        self.assertEqual(
            resolved["controls"]["evaluation"]["mode"],
            "enforce_minimum",
        )

    def test_knowledge_base_run_spec_selects_behavior_feedback(self) -> None:
        build = load_module(
            "dungeness_harbor_build_three_knob_spec_test",
            REPOSITORY_ROOT / "adapters/harbor/build.py",
        )
        path = (
            REPOSITORY_ROOT
            / "run-specs/users/bx/contaminated/"
            "ecdsa-kimi-subscription-llm-wiki-max-12usd/"
            "ecdsa-kimi-subscription-llm-wiki-max-12usd-knowledge-base.yaml"
        )
        document = build.load_yaml(path)
        _, _, resolved = build.resolve_research_state(
            document["research_state"]
        )
        self.assertNotIn("knowledge_base", resolved["controls"])
        self.assertEqual(
            resolved["controls"]["web_search"]["minimum"],
            0,
        )
        self.assertEqual(
            resolved["controls"]["evaluation"]["minimum"],
            12,
        )
        compose = build.yaml.safe_load(
            build.build_compose(
                "knowledge-base-three-knob-compose-test",
                {
                    "historical_cutoff": {
                        "end_published_date": "2026-05-28T23:59:59.999Z",
                    },
                    "search": {"max_results": 25},
                },
                {
                    "web": {"searches": 10, "fetches": 10},
                    "model": {"requests": 500, "total_tokens": 1000},
                    "evaluation": {"submissions": 10},
                },
                dev_scorer={
                    "context": "eval-sidecar",
                    "submissions": 10,
                    "port": 8090,
                },
                agent_timeout_sec=600,
                research_state=resolved,
                knowledge_base={
                    "access_mode": "sidecar",
                    "behavior_feedback": {
                        "enabled": True,
                        "mode": "visible",
                        "minimum_improvement": 0,
                        "kb_attribution_window_evaluations": 1,
                        "no_progress_evaluations": 3,
                    },
                },
                provider="kimi-code",
                model_name="k3",
                max_usd=12,
            )
        )
        config = json.loads(
            compose["services"]["research-state"]["environment"][
                "RESEARCH_STATE_CONFIG_JSON"
            ]
        )
        self.assertNotIn("knowledge_base", config["controls"])
        self.assertEqual(
            config["kb_behavior_feedback"]["mode"],
            "visible",
        )
        self.assertNotIn(
            "GROUNDING_VERIFIER_MODEL",
            compose["services"]["gateway"]["environment"],
        )


if __name__ == "__main__":
    unittest.main()
