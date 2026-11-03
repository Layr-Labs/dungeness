"""In-container command lifecycle. This file uses only the standard library."""
import json
import os
from pathlib import Path
import signal
import selectors
import subprocess
import sys
import time


MAX_LOG_BYTES = 64 * 1024**2


def capture(process, path, received):
    """Drain both streams continuously into Harbor's per-trial mounted log.

    Logs are untrusted diagnostics, never scoring evidence. Bound disk use while
    continuing to drain excess output so a noisy harness cannot deadlock itself.
    """
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    coverage = path.with_suffix('.coverage.json')
    observed = retained = 0
    last_report = 0.0
    interrupted_at = None
    complete = False
    def report():
        value = {"schema_version": 1, "observed_bytes": observed, "retained_bytes": retained,
                 "truncated": observed > retained, "complete": complete,
                 "streams": ["stdout", "stderr"], "format": "merged"}
        temporary = coverage.with_suffix('.tmp')
        with open(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600), 'w') as output:
            json.dump(value, output)
        os.replace(temporary, coverage)
    try:
        report()
        with os.fdopen(fd, 'wb', buffering=0) as output, selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                for key, _ in selector.select(.2):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    observed += len(chunk)
                    data = chunk[:max(0, MAX_LOG_BYTES - retained)]
                    output.write(data)
                    retained += len(data)
                if process.poll() is not None:
                    # A background descendant must not keep the output pipe open.
                    try: os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                if received:
                    interrupted_at = interrupted_at or time.monotonic()
                    if time.monotonic() - interrupted_at >= 5:
                        try: os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                if time.monotonic() - last_report >= 1:
                    report(); last_report = time.monotonic()
            code = process.wait()
            complete = not received
            report()
            return code
    finally:
        process.stdout.close()
        report()


def launch(task_path):
    task_path = str(Path(task_path).resolve())
    task = json.loads(Path(task_path).read_text())
    execution = task["execution"]
    argv = execution["resume_entrypoint"] if task.get("resume") else execution["entrypoint"]
    environment = {**os.environ, "DUNGENESS_TASK": task_path,
                   "DUNGENESS_WORKSPACE": task["workspace"]}
    if "remaining_seconds" in task:
        remaining = max(0, float(task["remaining_seconds"]))
        environment["DUNGENESS_AGENT_DEADLINE_EPOCH"] = str(time.time() + remaining)
        environment["DUNGENESS_AGENT_TIMEOUT_SEC"] = str(int(remaining))
    log_path = task.get("output_log")
    process = subprocess.Popen(argv, cwd=task["workspace"], env=environment, start_new_session=True,
                               stdout=subprocess.PIPE if log_path else None,
                               stderr=subprocess.STDOUT if log_path else None)
    received = []

    def terminate(signum, _frame):
        received.append(signum)
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    previous = {s: signal.signal(s, terminate) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        if log_path:
            return capture(process, Path(log_path), received)
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
