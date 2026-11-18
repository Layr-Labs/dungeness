"""Prevent native CLI qualification from mistaking reported success for execution."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "tools" / "antigravity-probe"
spec = importlib.util.spec_from_file_location("antigravity_probe", SOURCE / "probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


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
