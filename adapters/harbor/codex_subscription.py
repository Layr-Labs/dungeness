"""Harbor Codex adapter using a ChatGPT subscription credential."""

from __future__ import annotations

import shlex
import time
from typing import Any, override

from harbor.agents.installed.codex import Codex
from harbor.agents.installed.base import with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trial.paths import EnvironmentPaths

from codex_gateway import (
    build_instrumented_codex_command,
    prebaked_codex_is_ready,
)


def build_codex_subscription_config(
    model_context_window: int | None = None,
) -> str:
    """Build the isolated Codex config used for ChatGPT subscription runs."""

    if model_context_window is not None and (
        not isinstance(model_context_window, int)
        or isinstance(model_context_window, bool)
        or model_context_window < 1
    ):
        raise ValueError("model_context_window must be a positive integer")
    lines = [
        'cli_auth_credentials_store = "file"',
        'model_provider = "dungeness"',
    ]
    if model_context_window is not None:
        lines.append(f"model_context_window = {model_context_window}")
    lines.extend(
        [
            "[model_providers.dungeness]",
            'name = "Dungeness ChatGPT"',
            'base_url = "http://gateway:8080/model/chatgpt/v1"',
            'wire_api = "responses"',
            "requires_openai_auth = true",
            "supports_websockets = false",
        ]
    )
    return "\n".join(lines) + "\n"


class CodexSubscription(Codex):
    def __init__(
        self,
        *args: Any,
        model_context_window: int | None = None,
        continuation_max_resumes: int = 0,
        continuation_min_remaining_sec: int = 600,
        continuation_timeout_sec: int | None = None,
        **kwargs: Any,
    ) -> None:
        self.codex_config = build_codex_subscription_config(
            model_context_window
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
            'test -s /run/dungeness/codex-auth/auth.json || '
            '{ echo "missing Codex subscription credential" >&2; exit 1; }\n'
            f"mkdir -p {shlex.quote(codex_home)}\n"
            f"cp /run/dungeness/codex-auth/auth.json "
            f"{shlex.quote(codex_home)}/auth.json\n"
            f"chmod 600 {shlex.quote(codex_home)}/auth.json\n"
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

        model = self.model_name.split("/")[-1]
        cli_flags = self.build_cli_flags()
        initial_turn_timeout = (
            max(1, self.continuation_timeout_sec - 60)
            if self.continuation_timeout_sec is not None
            else None
        )
        try:
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
            if self.continuation_timeout_sec is not None:
                for resume_index in range(
                    1, self.continuation_max_resumes + 1
                ):
                    remaining_sec = int(
                        self.continuation_timeout_sec
                        - (time.monotonic() - started)
                    )
                    if remaining_sec < self.continuation_min_remaining_sec:
                        break
                    continuation_prompt = (
                        "The research window is still open with approximately "
                        f"{max(1, remaining_sec // 60)} minutes remaining. "
                        "Continue working on the task from the current workspace "
                        "and transcript. Do not merely repeat the previous "
                        "summary. Make another concrete optimization attempt, "
                        "rebuild it, measure it, and preserve the best valid "
                        "candidate. If the previous direction was too large, "
                        "choose the smallest actionable subproblem that could "
                        "improve the score."
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
        finally:
            try:
                await self.exec_as_agent(
                    environment,
                    command=f"rm -f {shlex.quote(codex_home)}/auth.json",
                    env=env,
                )
            except Exception:
                pass
