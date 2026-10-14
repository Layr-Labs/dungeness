"""Pre-baked pi adapter for the testbed sandbox.

Harbor's stock `pi` adapter (harbor.agents.installed.pi:Pi) ALWAYS runs
`install()` during agent setup, and that install unconditionally `curl`s the
nvm installer from raw.githubusercontent.com and `npm install`s pi from the
registry. In our trial sandbox the agent container has no egress (mediated,
gateway-only network), so that install dies with `Could not resolve host` and
the trial never starts.

Codex and Claude Code avoid this because THEIR `install()` short-circuits when
the binary is already present at the requested version -- so a pre-baked image
skips all network. pi's stock adapter has no such guard. This subclass adds it:
pi is pre-installed globally in the agent Dockerfile, so we verify it and skip
the network install (falling back to the stock behavior only if, unexpectedly,
pi is not on PATH).

Selected via the agent `import_path` in the rendered Harbor job (see build.py),
which requires this module to be importable -- run `harbor` with
`PYTHONPATH=adapters/harbor`.
"""

from typing import override

from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment


class PiPrebaked(Pi):
    @override
    async def install(self, environment: BaseEnvironment) -> None:
        # pi is baked into the image; `command -v pi` exits 0 when present, so
        # exec_as_agent returns normally and we skip the stock network install.
        # If pi were somehow absent, exec_as_agent raises on the non-zero exit
        # and we fall back to the stock install() (which needs egress).
        try:
            await self.exec_as_agent(
                environment,
                command=". ~/.nvm/nvm.sh 2>/dev/null || true; command -v pi >/dev/null 2>&1",
            )
        except Exception:
            await super().install(environment)
