"""Discover subscription models and optionally run small, direct official CLI tests."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile


RESPONSE = "subscription ready"
USAGE_FIELDS = (
    "input_tokens", "output_tokens", "thinking_tokens",
    "cache_read_tokens", "total_tokens",
)
SETTINGS = {
    "permissions": {
        "deny": [
            "command(*)", "read_file(*)", "write_file(*)",
            "read_url(*)", "execute_url(*)", "mcp(*)",
        ],
    },
}
AGENT = """---
name: openrsi-smoke
description: Text-only subscription connection test
tools: []
inheritCustomizations: false
mainAgent: true
subagent: false
---
Answer the supplied text prompt only. Do not use tools or inspect files.
"""


def subscription_environment():
    env = dict(os.environ)
    for key in (
        "GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_GEMINI_BASE_URL", "AGY_ADC_AUTH",
    ):
        env.pop(key, None)
    env["AGY_CLI_DISABLE_AUTO_UPDATE"] = "true"
    return env


def error_kind(text):
    """Keep sign-in links, account identifiers and arbitrary diagnostics out of receipts."""
    text = text.lower()
    if "verify your account" in text:
        return "account_verification_required"
    if "sign in" in text or "sign-in" in text:
        return "sign_in_required"
    if "rate limit" in text or "resource_exhausted" in text:
        return "rate_limited"
    return "cli_error"


def discover(cli, env):
    result = subprocess.run(
        [str(cli), "models"], env=env, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, timeout=25,
    )
    if result.returncode:
        raise RuntimeError(error_kind(result.stderr))
    models = []
    for line in result.stdout.splitlines():
        identifier, separator, label = line.partition("\t")
        if separator and identifier.startswith("gemini-"):
            models.append({"id": identifier, "name": label.strip()})
    if not models:
        raise RuntimeError("no_google_subscription_models")
    return models


def select_models(requested, available):
    known = {model["id"] for model in available}
    selected = list(dict.fromkeys(requested))
    missing = [model for model in selected if model not in known]
    if missing:
        raise ValueError("Not available in this account: " + ", ".join(missing))
    return selected


def summarize(model, process):
    final = {}
    for line in process.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("event") == "result":
            candidate = event.get("result")
            if isinstance(candidate, dict):
                final = candidate
    usage = final.get("usage")
    usage = usage if isinstance(usage, dict) else {}
    usage = {
        key: value for key in USAGE_FIELDS
        if isinstance(value := usage.get(key), int)
        and not isinstance(value, bool) and value >= 0
    }
    response_matches = str(final.get("response", "")).strip() == RESPONSE
    passed = process.returncode == 0 and final.get("status") == "SUCCESS" and response_matches
    return {
        "model": model,
        "passed": passed,
        "exit_code": process.returncode,
        "response_matches": response_matches,
        "reported_usage": usage,
        "error": None if passed else (
            error_kind(process.stderr) if process.returncode else "unexpected_response"
        ),
    }


def smoke(cli, model, env):
    with tempfile.TemporaryDirectory(prefix="openrsi-agy-subscription-") as temporary:
        workspace = Path(temporary)
        agents = workspace / ".agents" / "agents"
        agents.mkdir(parents=True)
        (agents / "openrsi-smoke.md").write_text(AGENT)
        command = [
            str(cli), "-p", f"Reply with exactly: {RESPONSE}",
            "--model", model, "--agent", "openrsi-smoke",
            "--output-format", "stream-json", "--print-timeout", "45s",
            "--disable-slash-commands", "--settings", json.dumps(SETTINGS),
        ]
        try:
            process = subprocess.run(
                command, cwd=workspace, env=env, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=55,
            )
        except subprocess.TimeoutExpired:
            return {"model": model, "passed": False, "error": "timeout"}
        return summarize(model, process)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True, help="Verified official agy executable")
    parser.add_argument(
        "--model", action="append", default=[],
        help="Exact model ID to test; repeat for multiple. Omit for discovery only.",
    )
    parser.add_argument("--output", type=Path, help="Save the sanitized JSON receipt")
    args = parser.parse_args()
    cli = args.cli.resolve(strict=True)
    env = subscription_environment()
    try:
        available = discover(cli, env)
        selected = select_models(args.model, available)
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        parser.exit(2, f"{error if not isinstance(error, subprocess.TimeoutExpired) else 'discovery_timeout'}\n")
    tests = []
    for model in selected:
        result = smoke(cli, model, env)
        tests.append(result)
        # Do not repeat account-wide failures against every requested model.
        if result.get("error") in ("account_verification_required", "sign_in_required", "rate_limited"):
            break
    report = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "scope": "direct official CLI subscription discovery and text-only smoke tests",
        "authentication": "cached official CLI sign-in; API-key and ADC environment removed",
        "available_google_models": available,
        "requested_models": selected,
        "tests": tests,
        "attested": False,
        "accounting_verified": False,
    }
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")
    return 0 if all(test["passed"] for test in tests) and len(tests) == len(selected) else 2


if __name__ == "__main__":
    raise SystemExit(main())
