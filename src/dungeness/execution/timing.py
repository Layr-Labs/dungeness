"""Bounded, credential-free startup events from the trusted orchestrator."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import threading


class StartupTiming:
    def __init__(self, path: Path):
        self.path = path
        self.process = None
        self.thread = None
        self.lock = threading.Lock()
        self.count = 0

    def mark(self, phase, *, at=None, service=None):
        with self.lock:
            if self.count >= 128:
                return
            self.count += 1
            event = {"phase": phase, "at": at or datetime.now(timezone.utc).isoformat()}
            if service:
                event["service"] = service
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a") as output:
                output.write(json.dumps(event) + "\n")

    def watch_containers(self, render: Path):
        # Observe only this rendered Compose project. Do not retain container
        # configuration, environment, command lines, names or arbitrary labels.
        try:
            self.process = subprocess.Popen(
                ["docker", "events", "--filter", "type=container", "--format", "{{json .}}"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        except OSError:
            self.mark("container_timing_unavailable")
            return

        def collect():
            for line in self.process.stdout:
                try:
                    event = json.loads(line)
                    labels = event.get("Actor", {}).get("Attributes", {})
                    working = Path(labels.get("com.docker.compose.project.working_dir", "/"))
                    if not working.is_relative_to(render):
                        continue
                    service = labels.get("com.docker.compose.service")
                    action = event.get("Action")
                    if service not in {"main", "gateway", "problem", "dev-scorer", "verifier"}:
                        continue
                    if action not in {"create", "start", "health_status: healthy"}:
                        continue
                    at = datetime.fromtimestamp(event["timeNano"] / 1e9, timezone.utc).isoformat()
                    self.mark("container_" + {"create": "created", "start": "started",
                              "health_status: healthy": "healthy"}[action], at=at, service=service)
                except (ValueError, KeyError, TypeError, OverflowError):
                    continue
        self.thread = threading.Thread(target=collect, daemon=True)
        self.thread.start()

    def close(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
            self.thread.join(timeout=3)
            self.process.stdout.close()
