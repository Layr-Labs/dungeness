#!/usr/bin/env python3
"""Export a committed runtime without research data, run output or local secrets."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "dungeness", "README.md", "DESIGN.md", ".env.example", ".gitignore",
    ".gitattributes", "LICENSE", "LICENSE.md",
    "docs/command-harness.md", "docs/runtime-distribution.md", "docs/cli-reference.md",
    "script/export_runtime.py", "runtime-contract.json",
    "pyproject.toml", "uv.lock",
    "agents/README.md", "tasks/README.md", "run-specs/README.md",
    "checkpoints/README.md", "problems/README.md", "verifiers/README.md", "scaffolds/README.md",
    "docs/README.md", "script/README.md", "tools/README.md",
    "docs/gateway-authentication.md", "docs/gateway-request-policy.md",
    "docs/problem-service.md", "docs/runtime-contract.md", "docs/development.md", "docs/scaffolds.md",
}
TRANSCRIPT_TOOLS = {
    "tools/transcripts/render_gateway_transcript.py",
    "tools/transcripts/serve_gateway_transcripts.py",
}
PREFIXES = (
    "src/", "adapters/", "agents/common/", "agents/projects/dungeness/",
    "services/", "policies/", "assets/",
)


def runtime_path(path: str, *, include_transcript_tools: bool = False) -> bool:
    parts = PurePosixPath(path).parts
    if any(part in {"tests", "__pycache__", ".git"} for part in parts):
        return False
    if path.endswith(".pyc") or any(part.startswith(".env") for part in parts):
        return path == ".env.example"
    return (path in FILES or path.startswith(PREFIXES)
            or include_transcript_tools and path in TRANSCRIPT_TOOLS)


def export_runtime(repository: Path, revision: str, output: Path, *,
                   include_transcript_tools: bool = False) -> dict:
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repository), *args])

    commit = git("rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}").decode().strip()
    paths = [
        path for path in git("ls-tree", "-r", "--name-only", "-z", commit).decode().split("\0")
        if path and runtime_path(path, include_transcript_tools=include_transcript_tools)
    ]
    required = {
        "dungeness", "src/dungeness/compiler.py",
        "adapters/harbor/command_agent.py", "services/gateway/gateway.py",
    }
    if not required <= set(paths):
        raise ValueError(f"Revision lacks runtime files: {', '.join(sorted(required - set(paths)))}")
    archived = git("archive", "--format=tar", commit, "--", *paths)
    entries = []
    with tarfile.open(fileobj=io.BytesIO(archived)) as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile() or member.name not in paths:
                raise ValueError(f"Unexpected runtime archive entry: {member.name}")
            content = archive.extractfile(member).read()
            if content.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
                raise ValueError(f"Runtime requires materialized content, not an LFS pointer: {member.name}")
            # git archive's mode is affected by tar.umask; distribute predictable
            # executable/data modes without group/world-write permissions.
            entries.append((member.name, 0o755 if member.mode & 0o111 else 0o644, content))
    metadata = {
        "schema_version": 1,
        "source_commit": commit,
        "files": {name: hashlib.sha256(content).hexdigest() for name, _, content in entries},
    }
    # Exclusive creation avoids replacing a previous release. gzip/tar times are
    # fixed so the same source commit produces the same archive bytes.
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination:
        with gzip.GzipFile(fileobj=destination, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as bundle:
                for name, mode, content in entries + [
                    ("RUNTIME_SOURCE.json", 0o644, (json.dumps(metadata, sort_keys=True, indent=2) + "\n").encode())
                ]:
                    member = tarfile.TarInfo(f"dungeness-runtime/{name}")
                    member.size = len(content)
                    member.mode = mode
                    bundle.addfile(member, io.BytesIO(content))
    return {
        "source_commit": commit, "files": len(entries), "archive": str(output),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "bytes": output.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="HEAD", help="Committed source to export; working-tree edits are excluded.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--include-transcript-tools", action="store_true",
                        help="Include the optional local transcript viewer.")
    args = parser.parse_args()
    print(json.dumps(export_runtime(ROOT, args.revision, args.output,
                                   include_transcript_tools=args.include_transcript_tools), indent=2))


if __name__ == "__main__":
    main()
