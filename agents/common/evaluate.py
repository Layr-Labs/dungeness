#!/usr/bin/env python3
"""Submit the current candidate to the eval sidecar and print its score.

The agent never sees test inputs or answers: this ships the candidate to the eval
sidecar, which scores it and returns a score only. The candidate may be a single
file (e.g. ecdsa-fail's src/point_add.rs at the earliest commit) or a whole module
DIRECTORY (src/point_add/ at later commits); this client sends raw bytes for a
file and a tar for a directory, and the matching sidecar handles each. What the
score means comes from the sidecar's `note`. This client holds no test data and
does no scoring itself.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

DEV_SCORER_URL = os.environ.get("DEV_SCORER_URL", "http://dev-scorer:8090")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="evaluate",
        description="Score the current candidate via the eval sidecar.",
    )
    parser.add_argument(
        "solution", nargs="?", default=os.environ.get("CANDIDATE_PATH")
    )
    parser.add_argument("--json", action="store_true", help="Print the trusted evaluator response as JSON.")
    args = parser.parse_args()

    if not args.solution:
        raise SystemExit("evaluate: no candidate path (set CANDIDATE_PATH or pass one)")
    source = Path(args.solution)

    # A file -> raw bytes; a directory (a module candidate) -> a tar of its
    # contents. The sidecar for this problem expects the matching form.
    if source.is_file():
        data = source.read_bytes()
        content_type = "application/octet-stream"
    elif source.is_dir():
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as tar:
            tar.add(source, arcname=".")
        data = buffer.getvalue()
        content_type = "application/x-tar"
    else:
        raise SystemExit(f"evaluate: candidate not found: {source}")

    request = urllib.request.Request(
        DEV_SCORER_URL.rstrip("/") + "/score",
        data=data,
        headers={"content-type": content_type},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=1800) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as error:
        sys.stderr.write(error.read().decode("utf-8", "replace") + "\n")
        raise SystemExit(1) from error
    except urllib.error.URLError as error:
        raise SystemExit(f"evaluate: cannot reach eval sidecar: {error}") from error

    if args.json:
        print(json.dumps(result, sort_keys=True))
        return

    # `status` is present when the sidecar builds/runs the candidate (ecdsa-fail);
    # a non-ok status carries the agent's own build/correctness output in `detail`.
    status = result.get("status")
    if status and status != "ok":
        print(f"status: {status}")
        detail = result.get("detail")
        if detail:
            sys.stderr.write(detail.rstrip() + "\n")

    print(f"score: {result['score']}")
    remaining = result.get("submissions_remaining")
    if remaining is not None:
        print(f"submissions remaining: {remaining}")
    note = result.get("note")
    if note:
        print(f"note: {note}")


if __name__ == "__main__":
    main()
