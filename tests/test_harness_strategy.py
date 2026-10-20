"""The runtime enforces permissions while the harness owns research behavior."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_record_model import build, cli, write_run_spec


class HarnessStrategyTests(unittest.TestCase):
    def test_existing_catalyst_web_alias_still_disables_all_web_spending(self):
        for setting in (
            {"mode": "disabled"},
            {"profile": "web-search-profile:system/dungeness/disabled-v1"},
        ):
            access = build.resolve_web_access(setting)
            budget = {"model": {"max_usd": 1}, "web": {"searches": 5, "fetches": 8}}
            resolved = build.apply_web_search_mode_to_budget(budget, access["mode"])
            self.assertEqual(resolved["web"], {"searches": 0, "fetches": 0})
            self.assertEqual(resolved["model"], {"max_usd": 1})
            self.assertEqual(budget["web"]["searches"], 5)

    def test_retired_strategy_settings_fail_before_compilation_or_model_access(self):
        settings = (
            {"evaluation": {"profile": "evaluation-profile:system/dungeness/iterative-v1"}},
            {"evaluation": None},
            {"web_search": {"profile": "web-search-profile:system/dungeness/m4-dedicated-researcher-v1"}},
            {"web_search": {"mode": "disabled", "profile": "anything"}},
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.yaml"
            for setting in settings:
                with self.subTest(setting=setting):
                    write_run_spec(path)
                    with path.open("a") as stream:
                        stream.write(build.yaml.safe_dump(setting))
                    with self.assertRaises(SystemExit):
                        cli.load_run_spec(str(path))
                    with patch.object(build, "checkout") as checkout:
                        with self.assertRaises(ValueError):
                            build.build_task("ecdsa-starter", "invalid-strategy",
                                             agent_id="command", checkpoint="62ae3d0",
                                             namespace="users/bx", run_spec=str(path))
                        checkout.assert_not_called()

    def test_retired_split_evaluator_is_rejected_before_fetching_sources(self):
        original = build.load_yaml

        def split_task(path):
            document = original(path)
            if document.get("type") == "task":
                document["evaluation"] = {"mode": "split", "dev_cases": [1], "holdout_cases": [2]}
            return document

        with tempfile.TemporaryDirectory() as directory, patch.object(build, "load_yaml", side_effect=split_task), \
                patch.object(build, "checkout") as checkout:
            path = Path(directory) / "run.yaml"
            write_run_spec(path)
            with self.assertRaisesRegex(ValueError, "split evaluator has been retired"):
                build.build_task("ecdsa-starter", "invalid-split",
                                 agent_id="command", checkpoint="62ae3d0", namespace="users/bx", run_spec=str(path))
            checkout.assert_not_called()

    def test_runtime_discloses_tools_and_limits_without_selecting_strategy(self):
        notice = (
            build.build_workspace_notice("src/point_add", evaluation_available=True)
            + build.build_eval_notice("src/point_add", "minimize")
            + build.build_timebox_notice(900)
        )
        for required in ("src/point_add", "evaluate", "900 seconds", "run-status",
                         "final verifier", "lower is better"):
            self.assertIn(required, notice)
        for retired in ("Within the first", "Before changing", "research-worker",
                        "Evaluation loop", "two to four", "Stop starting"):
            self.assertNotIn(retired, notice)
