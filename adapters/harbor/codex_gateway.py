"""Harbor Codex adapter pinned to the Dungeness Responses gateway."""

from __future__ import annotations

import json
import shlex
import time
from typing import Any, override

from harbor.agents.installed.codex import Codex
from harbor.agents.installed.base import with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trial.paths import EnvironmentPaths


async def prebaked_codex_is_ready(
    agent: Codex,
    environment: BaseEnvironment,
) -> bool:
    """Return whether the image already contains the requested Codex CLI."""

    version = getattr(agent, "_version", None)
    expected = f"codex-cli {version}" if version else None
    command = "command -v codex >/dev/null 2>&1"
    if expected is not None:
        command += (
            " && "
            f'test "$(codex --version 2>/dev/null)" = {shlex.quote(expected)}'
        )
    try:
        await agent.exec_as_agent(environment, command=command)
    except Exception:
        return False
    return True






def build_instrumented_codex_command(
    *,
    model: str,
    instruction: str,
    cli_flags: str,
    codex_home: str,
    agent_dir: str,
    output_filename: str,
    resume_prompt: str | None = None,
    append: bool = False,
    phase: str = "initial",
    turn_timeout_sec: int | None = None,
) -> str:
    """Run Codex while preserving raw output and recording local stall evidence."""

    output_path = f"{agent_dir}/{output_filename}"
    event_path = f"{agent_dir}/codex-runtime-events.tsv"
    heartbeat_path = f"{agent_dir}/codex-runtime-heartbeats.tsv"
    reasoning_flag = f"{cli_flags} " if cli_flags else ""
    common_options = (
        "--dangerously-bypass-approvals-and-sandbox "
        "--skip-git-repo-check "
        f"--model {shlex.quote(model)} "
        "--json "
        "--enable unified_exec "
        f"{reasoning_flag}"
    )
    if resume_prompt is None:
        codex_command = (
            "codex exec "
            f"{common_options}"
            "-- "
            f"{shlex.quote(instruction)}"
        )
    else:
        codex_command = (
            "codex exec resume "
            "--last "
            f"{common_options}"
            "-- "
            f"{shlex.quote(resume_prompt)}"
        )
    executed_codex_command = (
        f"timeout --signal=TERM {turn_timeout_sec}s {codex_command}"
        if turn_timeout_sec is not None
        else codex_command
    )
    deadline_setup = (
        "export DUNGENESS_AGENT_DEADLINE_EPOCH="
        '"$(( $(date +%s) + '
        f"{turn_timeout_sec}"
        ' ))"'
        if turn_timeout_sec is not None
        else ""
    )
    initialize_logs = (
        ': >> "$output_path"\n: >> "$event_path"\n: >> "$heartbeat_path"'
        if append
        else ': > "$output_path"\n: > "$event_path"\n: > "$heartbeat_path"'
    )
    return f"""
set -o pipefail
output_path={shlex.quote(output_path)}
event_path={shlex.quote(event_path)}
heartbeat_path={shlex.quote(heartbeat_path)}
{initialize_logs}
{deadline_setup}
printf '%s\tphase_start\t%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" {shlex.quote(phase)} >> "$event_path"
(
  {executed_codex_command} 2>&1 </dev/null |
  while IFS= read -r line; do
    timestamp="$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"
    printf '%s\t%s\n' "$timestamp" "$line" >> "$event_path"
    printf '%s\n' "$line" | tee -a "$output_path"
  done
) &
runner_pid=$!
while kill -0 "$runner_pid" 2>/dev/null; do
  timestamp="$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"
  output_bytes="$(wc -c < "$output_path" | tr -d ' ')"
  session_bytes="$(
    if [ -d {shlex.quote(codex_home)}/sessions ]; then
      du -sb {shlex.quote(codex_home)}/sessions 2>/dev/null | awk '{{print $1}}'
    else
      printf '0'
    fi
  )"
  processes="$(
    ps -eo pid=,ppid=,stat=,etime=,time=,rss=,comm= 2>/dev/null |
      awk '$7 ~ /(codex|node)/ {{printf "%s,%s,%s,%s,%s,%s,%s;", $1,$2,$3,$4,$5,$6,$7}}'
  )"
  printf '%s\t%s\t%s\t%s\n' \
    "$timestamp" "$output_bytes" "${{session_bytes:-0}}" "$processes" \
    >> "$heartbeat_path"
  sleep 5
done
wait "$runner_pid"
raw_runner_status=$?
runner_status=$raw_runner_status
if [ "$raw_runner_status" -eq 124 ]; then
  runner_status=0
fi
printf '%s\tphase_exit\t%s\t%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" \
  {shlex.quote(phase)} "$runner_status" >> "$event_path"
exit "$runner_status"
""".strip()


def build_codex_config(
    gateway_base_url: str,
    model_context_window: int | None = None,
) -> str:
    """Build the isolated Codex config used inside one Harbor trial."""

    if not gateway_base_url.startswith("http://gateway:8080/model/"):
        raise ValueError("Codex gateway_base_url must target the trusted gateway")
    if model_context_window is not None and (
        not isinstance(model_context_window, int)
        or isinstance(model_context_window, bool)
        or model_context_window < 1
    ):
        raise ValueError("model_context_window must be a positive integer")
    lines = ['model_provider = "dungeness"']
    if model_context_window is not None:
        lines.append(f"model_context_window = {model_context_window}")
    lines.extend(
        [
            "[model_providers.dungeness]",
            'name = "Dungeness Gateway"',
            f'base_url = "{gateway_base_url.rstrip("/")}"',
            'wire_api = "responses"',
            'env_key = "OPENAI_API_KEY"',
            "supports_websockets = false",
        ]
    )
    return "\n".join(lines) + "\n"


class CodexGateway(Codex):
    def __init__(
        self,
        *args: Any,
        gateway_base_url: str,
        model_context_window: int | None = None,
        continuation_max_resumes: int = 0,
        continuation_min_remaining_sec: int = 600,
        continuation_timeout_sec: int | None = None,
        **kwargs: Any,
    ) -> None:
        self.codex_config = build_codex_config(
            gateway_base_url,
            model_context_window,
        )
        if continuation_max_resumes < 0:
            raise ValueError("continuation_max_resumes must be non-negative")
        if continuation_min_remaining_sec < 1:
            raise ValueError("continuation_min_remaining_sec must be positive")
        if continuation_max_resumes and (
            continuation_timeout_sec is None or continuation_timeout_sec < 1
        ):
            raise ValueError(
                "continuation_timeout_sec is required when continuation is enabled"
            )
        self.gateway_base_url = gateway_base_url.rstrip("/")
        self.continuation_max_resumes = continuation_max_resumes
        self.continuation_min_remaining_sec = continuation_min_remaining_sec
        self.continuation_timeout_sec = continuation_timeout_sec
        super().__init__(*args, **kwargs)

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        if await prebaked_codex_is_ready(self, environment):
            return
        await super().install(environment)

    @with_prompt_template
    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        if not self.model_name:
            raise ValueError("Model name is required")

        started = time.monotonic()
        codex_home = EnvironmentPaths.agent_dir.as_posix()
        env = {"CODEX_HOME": codex_home}
        setup_command = (
            f"mkdir -p {shlex.quote(codex_home)}\n"
            f"printf %s {shlex.quote(self.codex_config)} "
            f"> {shlex.quote(codex_home)}/config.toml"
        )
        skills_command = self._build_register_skills_command()
        if skills_command:
            setup_command += f"\n{skills_command}"
        mcp_command = self._build_register_mcp_servers_command()
        if mcp_command:
            setup_command += "\n" + mcp_command.replace(
                '> "$CODEX_HOME/config.toml"',
                '>> "$CODEX_HOME/config.toml"',
            )
        await self.exec_as_agent(environment, command=setup_command, env=env)

        # The agent profile stores the exact identifier expected by the fixed
        # gateway route. OpenRouter models include a vendor prefix; stripping it
        # would select a different model and fail trusted pricing validation.
        model = self.model_name
        cli_flags = self.build_cli_flags()
        initial_turn_timeout = (
            max(1, self.continuation_timeout_sec - 60)
            if self.continuation_timeout_sec is not None
            else None
        )
        await self.exec_as_agent(
            environment,
            command=build_instrumented_codex_command(
                model=model,
                instruction=instruction,
                cli_flags=cli_flags,
                codex_home=codex_home,
                agent_dir=EnvironmentPaths.agent_dir.as_posix(),
                output_filename=self._OUTPUT_FILENAME,
                turn_timeout_sec=initial_turn_timeout,
            ),
            env=env,
        )
        if self.continuation_timeout_sec is None:
            return
        for resume_index in range(1, self.continuation_max_resumes + 1):
            remaining_sec = int(
                self.continuation_timeout_sec - (time.monotonic() - started)
            )
            if remaining_sec < self.continuation_min_remaining_sec:
                break
            continuation_prompt = (
                "The research window is still open with approximately "
                f"{max(1, remaining_sec // 60)} minutes remaining. Continue "
                "working on the task from the current workspace and transcript. "
                "Do not merely repeat the previous summary. Make another concrete "
                "optimization attempt, rebuild it, measure it, and preserve the "
                "best valid candidate. If the previous direction was too large, "
                "choose the smallest actionable subproblem that could improve the "
                "score."
            )
            await self.exec_as_agent(
                environment,
                command=build_instrumented_codex_command(
                    model=model,
                    instruction=instruction,
                    cli_flags=cli_flags,
                    codex_home=codex_home,
                    agent_dir=EnvironmentPaths.agent_dir.as_posix(),
                    output_filename=self._OUTPUT_FILENAME,
                    resume_prompt=continuation_prompt,
                    append=True,
                    phase=f"resume-{resume_index}",
                    turn_timeout_sec=max(1, remaining_sec - 60),
                ),
                env=env,
            )
