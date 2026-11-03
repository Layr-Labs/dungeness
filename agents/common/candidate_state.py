#!/usr/bin/env python3
"""Save, restore, and inspect named snapshots of the editable candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil


NAME_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")


def digest_path(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
        return digest.hexdigest()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        digest.update(child.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def replace_path(source: Path, destination: Path) -> None:
    if destination.is_dir():
        shutil.rmtree(destination)
    elif destination.exists():
        destination.unlink()
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser(prog="candidate-state")
    parser.add_argument("operation", choices=("save", "restore", "list"))
    parser.add_argument("name", nargs="?")
    args = parser.parse_args()

    candidate_value = os.environ.get("CANDIDATE_PATH")
    if not candidate_value:
        parser.error("CANDIDATE_PATH is not configured")
    candidate = Path(candidate_value)
    state_root = Path(
        os.environ.get(
            "DUNGENESS_CANDIDATE_STATE_DIR",
            "/tmp/dungeness-candidate-state",
        )
    )
    state_root.mkdir(parents=True, exist_ok=True)

    if args.operation == "list":
        records = []
        for path in sorted(state_root.iterdir()):
            if path.name.endswith(".json"):
                continue
            records.append(
                {
                    "name": path.name,
                    "sha256": digest_path(path),
                }
            )
        print(json.dumps({"snapshots": records}, indent=2))
        return

    if not args.name or not NAME_RE.fullmatch(args.name):
        parser.error("save and restore require a lowercase snapshot name")
    snapshot = state_root / args.name
    metadata = state_root / f"{args.name}.json"

    if args.operation == "save":
        if not candidate.exists():
            parser.error(f"candidate does not exist: {candidate}")
        replace_path(candidate, snapshot)
        record = {
            "name": args.name,
            "candidate": str(candidate),
            "sha256": digest_path(snapshot),
        }
        metadata.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(record, sort_keys=True))
        return

    if not snapshot.exists():
        parser.error(f"snapshot does not exist: {args.name}")
    replace_path(snapshot, candidate)
    print(
        json.dumps(
            {
                "restored": args.name,
                "candidate": str(candidate),
                "sha256": digest_path(candidate),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
