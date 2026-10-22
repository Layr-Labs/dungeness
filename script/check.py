#!/usr/bin/env python3
"""Run offline component checks in the selected locked Python environment."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harbor-only", action="store_true",
                        help="run the adapter API contract in the separate Harbor environment")
    args = parser.parse_args()
    if args.harbor_only:
        from harbor.environments.base import ExecResult  # noqa: F401
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT / "tests")
        return subprocess.run(
            [sys.executable, "-m", "unittest",
             "test_command_harness.CommandHarnessTests.test_adapter_uses_real_harbor_exec_result_contract"],
            cwd=ROOT, env=environment,
        ).returncode

    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    declared = set(project["project"]["dependencies"] + project["dependency-groups"]["gateway"])
    deployed = {line.strip() for line in (ROOT / "services/gateway/requirements.txt").read_text().splitlines()
                if line.strip() and not line.startswith("#")}
    if declared != deployed:
        parser.error("Gateway requirements and pyproject.toml must declare the same pinned dependencies.")

    for directory in ("tests", "services/gateway/tests", "tools/transcripts"):
        environment = dict(os.environ)
        # Each suite runs in its own interpreter: gateway import-time state must
        # not leak into core tests. Do not inherit unrelated PYTHONPATH entries.
        environment["PYTHONPATH"] = os.pathsep.join(
            str(ROOT / path) for path in ("src", "services/gateway")
        )
        print(f"Checking {directory}", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", directory],
            cwd=ROOT, env=environment,
        )
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
