"""Prevent native CLI qualification from mistaking reported success for execution."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "tools" / "antigravity-probe"
spec = importlib.util.spec_from_file_location("antigravity_probe", SOURCE / "probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
subscription_spec = importlib.util.spec_from_file_location(
    "antigravity_subscription", SOURCE / "subscription.py",
)
subscription = importlib.util.module_from_spec(subscription_spec)
subscription_spec.loader.exec_module(subscription)


class AntigravityProbeTests(unittest.TestCase):
    def report(self, *, planner_calls=2, helper_calls=0, mcp_calls=0):
        usage = probe.expected_cli_usage(planner_calls)
        events = [
            {"event": "step_update", "step_update": {
                "state": "DONE", "tool_name": "call_mcp_tool",
            }},
            {"event": "result", "result": {"status": "SUCCESS", "usage": usage}},
        ]
        requests = [
            {"model": probe.MODEL, "tools": ["call_mcp_tool"]}
            for _ in range(planner_calls)
        ] + [{"model": "gemini-3.1-flash-lite-preview", "tools": []}
             for _ in range(helper_calls)]
        return probe.summarize("mcp", requests,
            "\n".join(map(json.dumps, events)), 0, False, mcp_calls)

    def test_success_and_done_do_not_prove_tool_execution(self):
        self.assertFalse(self.report()["mcp_tool_completed"])
        self.assertTrue(self.report(mcp_calls=1)["mcp_tool_completed"])

    def test_missing_helper_usage_cannot_pass_qualification(self):
        result = self.report(helper_calls=1, mcp_calls=1)
        self.assertTrue(result["mcp_tool_completed"])
        self.assertEqual(result["model_calls_observed"], 3)
        self.assertFalse(result["all_observed_usage_reported"])
        self.assertTrue(self.report(mcp_calls=1)["all_observed_usage_reported"])

    def test_combined_usage_cannot_price_different_models(self):
        requests = [
            {"model": probe.MODEL, "tools": []},
            {"model": probe.MODEL, "tools": []},
            {"model": "gemini-3.1-flash-lite-preview", "tools": []},
        ]
        final = {"event": "result", "result": {
            "status": "SUCCESS", "usage": probe.expected_cli_usage(3),
        }}
        result = probe.summarize("mcp", requests, json.dumps(final), 0, False, 1)
        self.assertTrue(result["all_observed_usage_reported"])
        self.assertFalse(result["model_usage_attributable"])
        self.assertEqual(result["expected_usage_by_model"], {
            probe.MODEL: probe.expected_cli_usage(2),
            "gemini-3.1-flash-lite-preview": probe.expected_cli_usage(1),
        })
        self.assertTrue(self.report(mcp_calls=1)["model_usage_attributable"])

    def test_mcp_fixture_records_calls_without_executing_the_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            journal = Path(temporary) / "calls.jsonl"
            marker = Path(temporary) / "must-not-exist"
            requests = [
                {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": "research_exec", "arguments": {
                     "command": f"touch {marker}",
                 }}},
            ]
            result = subprocess.run([sys.executable, str(SOURCE / "mock_mcp.py")],
                input="\n".join(map(json.dumps, requests)) + "\n",
                env={**os.environ, "OPENRSI_PROBE_MCP_CALLS": str(journal)},
                capture_output=True, text=True, timeout=5, check=True)
            replies = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual(len(replies), 2)
            self.assertEqual(journal.read_text(), '{"tool":"research_exec"}\n')
            self.assertFalse(marker.exists())

    def test_subscription_models_must_be_available_before_testing(self):
        available = [{"id": "gemini-4-neon-low", "name": "Neon"}]
        with self.assertRaisesRegex(ValueError, "Not available"):
            subscription.select_models(
                ["gemini-4-neon-low", "gemini-4-carbon-low"], available,
            )
        self.assertEqual(subscription.select_models(
            ["gemini-4-neon-low", "gemini-4-neon-low"], available,
        ), ["gemini-4-neon-low"])

    def test_subscription_receipt_excludes_private_cli_fields(self):
        raw = {"event": "result", "result": {
            "status": "ERROR", "conversation_id": "private-conversation",
            "response": "private response", "usage": {
                "input_tokens": 0, "account": "private-account",
            },
        }}
        process = subprocess.CompletedProcess([], 1, json.dumps(raw),
            "Verify your account at https://example.invalid/private-code")
        result = subscription.summarize("gemini-4-neon-low", process)
        self.assertEqual(result["error"], "account_verification_required")
        self.assertEqual(result["reported_usage"], {"input_tokens": 0})
        self.assertNotIn("private", json.dumps(result))
        self.assertFalse(result["passed"])

    def test_subscription_connection_does_not_fall_back_to_api_key_or_adc(self):
        keys = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS",
                "GOOGLE_GEMINI_BASE_URL", "AGY_ADC_AUTH")
        with patch.dict(os.environ, dict.fromkeys(keys, "must-not-propagate")):
            env = subscription.subscription_environment()
        for key in keys:
            self.assertNotIn(key, env)
        self.assertEqual(env["AGY_CLI_DISABLE_AUTO_UPDATE"], "true")
