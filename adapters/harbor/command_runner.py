"""In-container command lifecycle. This file uses only the standard library."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys


def launch(task_path):
    task_path = str(Path(task_path).resolve())
    task = json.loads(Path(task_path).read_text())
    execution = task["execution"]
    argv = execution["resume_entrypoint"] if task.get("resume") else execution["entrypoint"]
    environment = {**os.environ, "DUNGENESS_TASK": task_path,
                   "DUNGENESS_WORKSPACE": task["workspace"]}
    process = subprocess.Popen(argv, cwd=task["workspace"], env=environment, start_new_session=True)
    received = []

    def terminate(signum, _frame):
        received.append(signum)
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    previous = {s: signal.signal(s, terminate) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        while True:
            try:
                return process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                if received:
                    try:
                        return process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        return 128 + received[0]
    finally:
        # Also remove background workers when the entrypoint exits normally.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        for signum, handler in previous.items():
            signal.signal(signum, handler)


if __name__ == "__main__":
    raise SystemExit(launch(sys.argv[1]))
