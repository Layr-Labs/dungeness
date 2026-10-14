#!/usr/bin/env python3
"""Run a bounded, read-only Codex web-research worker inside a trial."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROLE_PROMPTS = {
    "thin": """\
You are a thin web-research worker. The main agent owns the research agenda,
hypotheses, implementation strategy, and final synthesis. Stay within the
assigned research direction.

You may inspect /workspace/repo read-only and use `web search` and eligible
`web fetch` results. Do not edit files, run `evaluate`, solve the whole coding
task, delegate again, or broaden the agenda without explaining why the assigned
question cannot be answered.

Return a compact evidence report with:
1. Assigned question
2. Findings
3. Evidence table: claim, source title/URL, publication date evidence, relevance
4. Implications for the main agent's hypothesis
5. Contradictions, uncertainty, and suggested follow-up
""",
    "autonomous": """\
You are the dedicated web researcher for a coding-research task. You own the
research policy for the supplied problem: choose queries, follow promising
leads, compare and corroborate evidence, inspect relevant repository context
read-only, and decide when further research has lower value than returning.

Use `web search` and eligible `web fetch` results. Do not edit files, run
`evaluate`, implement the solution, or delegate again.

Return a structured evidence packet with:
1. Research framing and revised hypotheses
2. Search path and why it changed
3. Evidence table: claim, source title/URL, publication date evidence, strength
4. Conflicts and unresolved uncertainty
5. Concrete implementation opportunities, ranked by expected value
6. What should be tested first
""",
}

TOPOLOGY_MODES = {
    "thin-workers": {"thin"},
    "dedicated-researcher": {"autonomous"},
    "single-agent": set(),
}


def worker_prompt(mode: str, brief: str) -> str:
    if mode not in ROLE_PROMPTS:
        raise ValueError(f"unsupported research-worker mode: {mode}")
    normalized = brief.strip()
    if not normalized:
        raise ValueError("research-worker brief must not be empty")
    return ROLE_PROMPTS[mode] + "\n\nMain-agent brief:\n" + normalized + "\n"


def require_topology(mode: str, topology: str) -> None:
    allowed = TOPOLOGY_MODES.get(topology)
    if allowed is None:
        raise ValueError(f"unsupported research topology: {topology}")
    if mode not in allowed:
        raise ValueError(
            f"research-worker {mode!r} is unavailable under topology {topology!r}"
        )


def reserve_dedicated_researcher(state_root: Path) -> None:
    state_root.mkdir(parents=True, exist_ok=True)
    marker = state_root / "dedicated-researcher-invoked"
    try:
        descriptor = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError(
            "dedicated-researcher topology permits exactly one invocation"
        ) from error
    os.close(descriptor)


def build_command(
    *,
    model: str,
    reasoning_effort: str,
    reasoning_summary: str,
    output_path: Path,
    prompt: str,
) -> list[str]:
    return [
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--disable",
        "multi_agent",
        "--enable",
        "unified_exec",
        "--model",
        model,
        "-c",
        f"model_reasoning_effort={reasoning_effort}",
        "-c",
        f"model_reasoning_summary={reasoning_summary}",
        "--output-last-message",
        str(output_path),
        "--color",
        "never",
        "--",
        prompt,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a read-only research worker using the trial's model route."
    )
    parser.add_argument("mode", choices=sorted(ROLE_PROMPTS))
    parser.add_argument(
        "brief",
        nargs="*",
        help="research brief; when omitted, read it from standard input",
    )
    args = parser.parse_args()
    brief = " ".join(args.brief) if args.brief else sys.stdin.read()
    try:
        prompt = worker_prompt(args.mode, brief)
    except ValueError as error:
        parser.error(str(error))

    topology = os.environ.get(
        "DUNGENESS_RESEARCH_TOPOLOGY",
        "single-agent",
    )
    try:
        require_topology(args.mode, topology)
        if topology == "dedicated-researcher":
            reserve_dedicated_researcher(
                Path(
                    os.environ.get(
                        "DUNGENESS_RESEARCH_STATE_DIR",
                        "/tmp/dungeness-research-state",
                    )
                )
            )
    except ValueError as error:
        parser.error(str(error))

    model = os.environ.get("DUNGENESS_RESEARCH_MODEL")
    effort = os.environ.get("DUNGENESS_RESEARCH_REASONING_EFFORT")
    summary = os.environ.get("DUNGENESS_RESEARCH_REASONING_SUMMARY", "none")
    source_home = os.environ.get("CODEX_HOME")
    if not model or not effort or not source_home:
        parser.error(
            "research-worker requires DUNGENESS_RESEARCH_MODEL, "
            "DUNGENESS_RESEARCH_REASONING_EFFORT, and CODEX_HOME"
        )
    source_config = Path(source_home) / "config.toml"
    if not source_config.is_file():
        parser.error(f"Codex config does not exist: {source_config}")

    with tempfile.TemporaryDirectory(prefix="dungeness-research-worker-") as raw:
        worker_home = Path(raw)
        shutil.copy2(source_config, worker_home / "config.toml")
        output_path = worker_home / "evidence.md"
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(worker_home)
        command = build_command(
            model=model,
            reasoning_effort=effort,
            reasoning_summary=summary,
            output_path=output_path,
            prompt=prompt,
        )
        result = subprocess.run(command, env=environment, check=False)
        if result.returncode != 0:
            return result.returncode
        if not output_path.is_file():
            print("research-worker produced no evidence packet", file=sys.stderr)
            return 1
        print(output_path.read_text(encoding="utf-8").rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
