"""Custom Harbor adapter for Prime Intellect's prime-agent.

Harbor has no built-in adapter for prime-agent, so this provides one, selected
via the agent `import_path` in the rendered job (module must be on PYTHONPATH --
run harbor with PYTHONPATH=adapters/harbor).

prime-agent is a pi-mono derivative (same pi-ai provider system as the `pi`
agent): it reads a `models.json` provider override for a custom base URL, runs
headless via `--print --mode json`, and takes `--provider/--model/--thinking`
with a `provider/model` id. It is pre-baked into the agent image (npm global
install of a pinned release tarball), so install() here is a no-op verification
-- no network at trial time.
"""

from typing import override
import json
import os
import shlex

from harbor.agents.installed.base import BaseInstalledAgent, CliFlag, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

# provider prefix -> API-key env vars the agent forwards to the CLI (the gateway
# holds the real key; the agent gets only the placeholder).
_PROVIDER_KEYS = {
    "openrouter": ["OPENROUTER_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY", "ANTHROPIC_OAUTH_TOKEN"],
    "openai": ["OPENAI_API_KEY"],
    "google": ["GEMINI_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY", "GOOGLE_API_KEY"],
}


class PrimeAgent(BaseInstalledAgent):
    _OUTPUT_FILENAME = "prime-agent.txt"

    CLI_FLAGS = [
        CliFlag(
            "thinking",
            cli="--thinking",
            type="enum",
            choices=["off", "minimal", "low", "medium", "high", "xhigh", "max"],
        ),
    ]

    @staticmethod
    @override
    def name() -> str:
        # Not a registered Harbor AgentName; this class is selected by import_path.
        return "prime-agent"

    @override
    def get_version_command(self) -> str | None:
        return "prime-agent --version"

    @override
    def parse_version(self, stdout: str) -> str:
        return stdout.strip().splitlines()[-1].strip()

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        # prime-agent is pre-baked in the image (see agents/projects/dungeness/prime-agent/
        # Dockerfile); verify it and skip any network install. If it were
        # somehow absent, exec_as_agent raises on the non-zero exit.
        await self.exec_as_agent(environment, command="command -v prime-agent >/dev/null 2>&1")

    @with_prompt_template
    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        if not self.model_name or "/" not in self.model_name:
            raise ValueError("Model name must be in the format provider/model_name")
        provider, model = self.model_name.split("/", 1)

        # Pin HOME to the image's baked prime-agent home so it finds the
        # pre-built IPython kernel venv + models.json ($HOME/.prime/agent/...);
        # otherwise it would try to rebuild the kernel via uv, which needs the
        # internet the sandbox lacks.
        env: dict[str, str] = {"HOME": "/opt/prime-home"}
        for key in _PROVIDER_KEYS.get(provider, []):
            value = os.environ.get(key)
            if value:
                env[key] = value

        model_args = f"--provider {provider} --model {model} "
        cli_flags = self.build_cli_flags()
        if cli_flags:
            cli_flags += " "
        escaped_instruction = shlex.quote(instruction)

        await self.exec_as_agent(
            environment,
            command=(
                f"prime-agent --print --mode json --no-session "
                f"{model_args}{cli_flags}{escaped_instruction} "
                f'2>&1 </dev/null | grep -v \'"type":"message_update"\' '
                f"| stdbuf -oL tee /logs/agent/{self._OUTPUT_FILENAME}"
            ),
            env=env,
        )

    @override
    def populate_context_post_run(self, context: AgentContext) -> None:
        # Best-effort token accounting from the JSON event stream (the gateway is
        # the source of truth for metering/budget; this just fills the trajectory).
        output_file = self.logs_dir / self._OUTPUT_FILENAME
        if not output_file.exists():
            return
        n_in = n_out = n_cache = 0
        total_cost = 0.0
        for line in output_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "message_end":
                continue
            message = event.get("message") or {}
            if message.get("role") != "assistant":
                continue
            usage = message.get("usage") or {}
            n_in += usage.get("input", 0)
            n_out += usage.get("output", 0)
            n_cache += usage.get("cacheRead", 0)
            cost = usage.get("cost") or {}
            total_cost += cost.get("total", 0.0)
        context.n_input_tokens = n_in + n_cache
        context.n_output_tokens = n_out
        context.n_cache_tokens = n_cache
        context.cost_usd = total_cost if total_cost > 0 else None
