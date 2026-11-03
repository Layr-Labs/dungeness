"""Subprocess streaming with an explicit working directory."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import signal
import subprocess
import threading


@contextmanager
def termination_as_interrupt():
    """Let the CLI's SIGTERM cancellation unwind container/credential cleanup."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def stream_command(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    """Run a command visibly and return its last non-empty output line."""
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    last_line = ""
    assert process.stdout is not None
    try:
        for line in process.stdout:
            print(line, end="", flush=True)
            if line.strip():
                last_line = line.strip()
        return_code = process.wait()
    except BaseException:
        # Stay in the caller's process group: OpenRSI cancels that whole group.
        # Reap our child before container teardown even if interruption happens
        # while streaming output, rather than leaving a launcher running.
        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        except ProcessLookupError:
            # The child may exit between poll and signalling; still reap it.
            process.wait()
        raise
    finally:
        process.stdout.close()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command)
    return last_line
