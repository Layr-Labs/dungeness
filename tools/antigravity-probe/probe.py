"""Offline, real-CLI qualification probes. Run only through run.py."""
import collections
import http.server
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from urllib.parse import urlsplit


FIXTURE_USAGE = {
    "promptTokenCount": 100,
    "candidatesTokenCount": 5,
    "thoughtsTokenCount": 3,
    "totalTokenCount": 108,
    "cachedContentTokenCount": 20,
}
USAGE_FIELDS = (
    "input_tokens", "output_tokens", "thinking_tokens",
    "cache_read_tokens", "total_tokens",
)
MODEL = "gemini-4-carbon"


def expected_cli_usage(calls):
    # Observed CLI semantics: input and total exclude cache; output includes thought.
    return dict(zip(USAGE_FIELDS, (80 * calls, 8 * calls, 3 * calls, 20 * calls, 88 * calls)))


def summarize(case, requests, stdout, returncode, marker_exists):
    events = [json.loads(line) for line in stdout.splitlines() if line.startswith("{")]
    finals = [event["result"] for event in events if event.get("event") == "result"]
    final = finals[-1] if finals else {}
    usage = final.get("usage")
    steps = [
        event["step_update"] for event in events
        if event.get("event") == "step_update"
    ]
    errors = [
        step.get("tool_info", {}).get("error", {}).get("message", "")
        for step in steps if step.get("state") == "ERROR"
    ]
    declared = sorted({name for request in requests for name in request["tools"]})
    return {
        "case": case,
        "exit_code": returncode,
        "status": final.get("status"),
        "models_requested": dict(collections.Counter(r["model"] for r in requests)),
        "model_calls_observed": len(requests),
        "model_facing_tools": declared,
        "reported_usage": usage,
        "expected_usage_for_all_observed_calls": expected_cli_usage(len(requests)),
        "all_observed_usage_reported": bool(requests) and usage == expected_cli_usage(len(requests)),
        "mcp_tool_completed": any(
            step.get("tool_name") == "call_mcp_tool" and step.get("state") == "DONE"
            for step in steps
        ),
        "undeclared_shell_rejected": (
            case == "undeclared-shell"
            and "run_command" not in declared
            and not marker_exists
            and any('unknown tool: "run_command"' in error for error in errors)
        ),
    }


def run_case(case, always_proceed):
    # Each case receives a fresh HOME, workspace, CLI state, and synthetic key.
    with tempfile.TemporaryDirectory(prefix="agy-probe-") as temporary:
        root = Path(temporary)
        home = root / "home"
        workspace = root / "workspace"
        workspace.mkdir()
        config = home / ".gemini"
        (config / "antigravity-cli").mkdir(parents=True)
        (config / "config").mkdir()
        settings = {"modelProvider": "gemini", "agentMode": "", "toolPermission": "request-review"}
        (config / "antigravity-cli/settings.json").write_text(json.dumps(settings))
        (config / "config/mcp_config.json").write_text(json.dumps({
            "mcpServers": {"openrsi": {"command": "python", "args": ["/probe/mock_mcp.py"]}},
        }))
        agents = workspace / ".agents/agents"
        agents.mkdir(parents=True)
        (agents / "openrsi.md").write_text(
            "---\nname: openrsi\ndescription: Isolated probe agent\ntools: []\n"
            "mainAgent: true\nsubagent: false\n---\nUse only the supplied research tools.\n"
        )
        marker = root / "undeclared-tool-executed"
        requests = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                path = urlsplit(self.path).path
                if not path.startswith("/v1beta/models/") or not path.endswith(":streamGenerateContent"):
                    self.send_error(404)
                    return
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4 * 1024 * 1024:
                    self.send_error(413)
                    return
                body = json.loads(self.rfile.read(length))
                model = path.split("/models/", 1)[1].split(":", 1)[0]
                requests.append({
                    "model": model,
                    "tools": [
                        tool["name"] for group in body.get("tools", [])
                        for tool in group.get("functionDeclarations", [])
                    ],
                })
                parts = [{"text": "probe ready"}]
                if model != MODEL:
                    # Correctly shaped review response: no retry needed for invalid JSON.
                    parts = [{"text": json.dumps({
                        "severity": 0, "confidence": 10,
                        "reason": "The fixture returns a fixed string without executing a command.",
                    })}]
                elif len(requests) == 1 and case == "mcp":
                    parts = [{"functionCall": {"name": "call_mcp_tool", "args": {
                        "ServerName": "openrsi", "ToolName": "research_exec",
                        "Arguments": {"command": "echo 42"},
                    }}}]
                elif len(requests) == 1 and case == "undeclared-shell":
                    parts = [{"functionCall": {"name": "run_command", "args": {
                        "CommandLine": f"printf controlled > {marker}",
                        "Cwd": str(workspace), "Blocking": True, "SafeToAutoRun": True,
                    }}}]
                response = {
                    "candidates": [{"content": {"role": "model", "parts": parts},
                                    "finishReason": "STOP", "index": 0}],
                    "usageMetadata": FIXTURE_USAGE,
                    "modelVersion": model,
                }
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                self.wfile.write(b"data: " + json.dumps(response).encode() + b"\n\n")

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        # Explicit environment, with no host credentials, settings, or proxies.
        env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(home),
            "GEMINI_API_KEY": "synthetic-test-key",
            "GOOGLE_GEMINI_BASE_URL": f"http://127.0.0.1:{server.server_port}",
            "AGY_CLI_DISABLE_AUTO_UPDATE": "true",
        }
        command = [
            "/usr/local/bin/agy", "-p", "Reply probe ready.",
            "--model", MODEL + "-high", "--output-format", "stream-json",
            "--print-timeout", "15s", "--agent", "openrsi", "--disable-slash-commands",
            "--settings", json.dumps(settings),
        ]
        if always_proceed:
            command.append("--dangerously-skip-permissions")
        try:
            process = subprocess.run(
                command, env=env, cwd=workspace, capture_output=True, text=True, timeout=25,
            )
            result = summarize(case, requests, process.stdout, process.returncode, marker.exists())
            result["permission_mode"] = "always-proceed" if always_proceed else "request-review"
            if not result["status"]:
                # Only the synthetic container is inspected; no real credentials are mounted.
                result["diagnostic"] = process.stderr[-1500:]
            return result
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


def main():
    if os.environ.get("OPENRSI_OFFLINE_AGY_PROBE") != "1":
        raise SystemExit("Use run.py, which supplies an offline container.")
    cases = [
        run_case("text", True), run_case("mcp", False),
        run_case("mcp", True), run_case("undeclared-shell", True),
    ]
    report = {
        "schema_version": 1,
        "scope": "synthetic native CLI checks; not subscription entitlement or attestation qualification",
        "cases": cases,
        "probe_completed": (
            all(case["exit_code"] == 0 and case["status"] == "SUCCESS" for case in cases)
            and cases[2]["mcp_tool_completed"]
        ),
        "complete_usage_observed": all(case["all_observed_usage_reported"] for case in cases),
        "undeclared_shell_rejected": cases[-1]["undeclared_shell_rejected"],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
