"""Trusted adapter for arbitrary commands inside the Harbor sandbox.

Solver code is executed only in the container, never imported by the host.
The run's model policy and the evaluator remain outside the harness.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from harbor.agents.installed.base import BaseInstalledAgent


class CommandAgent(BaseInstalledAgent):
    def __init__(self, *args, execution, task_input=None, models=None,
                 continuation_max_resumes=0, continuation_min_remaining_sec=60,
                 continuation_timeout_sec=3600, **kwargs):
        self.execution = execution
        self.task_input = task_input or {}
        self.models = models or []
        self.max_resumes = continuation_max_resumes
        self.min_remaining = continuation_min_remaining_sec
        self.timeout = continuation_timeout_sec
        super().__init__(*args, **kwargs)

    @staticmethod
    def name():
        return "dungeness-command"

    def get_version_command(self):
        return None

    def parse_version(self, stdout):
        return None

    def mark_startup(self, phase):
        with (self.logs_dir / "startup.jsonl").open("a") as output:
            output.write(json.dumps({"phase": phase, "at": datetime.now(timezone.utc).isoformat()}) + "\n")

    async def install(self, environment):
        self.mark_startup("environment_ready")
        result = await self.exec_as_agent(environment, command="command -v python3")
        if result.return_code:
            raise RuntimeError("Command harness images must include Python 3.")

    async def run(self, instruction, environment, context):
        task = {**self.task_input, "schema_version": 1, "instruction": instruction,
                "workspace": "/workspace/repo", "models": self.models,
                "model": self.model_name, "execution": self.execution}
        if self.models:
            task["gateway"] = self.models[0]["base_url"]
            task["model_provider"] = self.models[0]["provider"]
        await environment.upload_file(Path(__file__).with_name("command_runner.py"),
                                      "/tmp/dungeness-launch.py")
        started = time.monotonic()
        for attempt in range(self.max_resumes + 1):
            task["resume"] = attempt > 0
            task["remaining_seconds"] = max(0, self.timeout - (time.monotonic() - started))
            path = self.logs_dir / "dungeness-task.json"
            path.write_text(json.dumps(task))
            await environment.upload_file(path, "/tmp/dungeness-task.json")
            self.mark_startup("agent_started" if attempt == 0 else "agent_resumed")
            result = await self.exec_as_agent(
                environment, command="python3 /tmp/dungeness-launch.py /tmp/dungeness-task.json",
                cwd=task["workspace"],
            )
            (self.logs_dir / f"harness-output-{attempt}.txt").write_text(
                (result.stdout or "") + "\n" + (result.stderr or ""))
            (self.logs_dir / "harness-outcome.json").write_text(json.dumps({
                "attempt": attempt, "exit_code": result.return_code,
                "status": "completed" if result.return_code == 0 else "failed",
            }))
            if result.return_code == 0:
                return
            if (result.return_code != 75 or attempt >= self.max_resumes
                    or not self.execution.get("resume_entrypoint")
                    or self.timeout - (time.monotonic() - started) < self.min_remaining):
                raise RuntimeError(f"Harness exited with status {result.return_code}.")

    def populate_context_post_run(self, context):
        # Accounting comes only from the gateway.
        pass
