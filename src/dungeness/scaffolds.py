"""Materialize trusted, language-independent scaffold data.

Only the operator's pinned task selects a manifest. Scaffolds contain files and
declarative text edits, never host Python modules or executable preparation hooks.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
import shutil

import yaml


def relative_path(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a relative path")
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or ".." in path.parts or "\\" in value
            or path.as_posix() != value or value == "."):
        raise ValueError(f"{field} must be a normalized relative path: {value!r}")
    return path


def contained_path(root, relative):
    path = root.joinpath(*relative.parts)
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"scaffold path escapes its root or is a symlink: {relative}")
    return path


def resolve_scaffold(repository_root: Path, value) -> dict:
    relative = relative_path(value, "task scaffold")
    if relative.parts[0] != "scaffolds":
        raise ValueError("task scaffold must be under scaffolds/")
    manifest_path = contained_path(repository_root / "scaffolds", PurePosixPath(*relative.parts[1:]))
    if not manifest_path.is_file():
        raise ValueError(f"task scaffold does not exist: {relative}")
    manifest = yaml.safe_load(manifest_path.read_text())
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != 2
            or manifest.get("type") != "scaffold" or not isinstance(manifest.get("id"), str)):
        raise ValueError("Expected a schema_version: 2 scaffold; install the trusted problem package.")
    unknown = set(manifest) - {
        "schema_version", "type", "id", "namespace", "candidate_path", "candidate_files",
        "workspace_paths", "trusted_files", "text_edits",
    }
    if unknown:
        raise ValueError(f"unsupported scaffold fields: {', '.join(sorted(unknown))}")
    candidate = relative_path(manifest.get("candidate_path"), "scaffold candidate_path")
    workspace = manifest.get("workspace_paths")
    if not isinstance(workspace, list) or not workspace:
        raise ValueError("scaffold workspace_paths must be a non-empty list")
    for path in workspace:
        relative_path(path, "scaffold workspace path")

    def outside_candidate(destination):
        if destination.is_relative_to(candidate) or candidate.is_relative_to(destination):
            raise ValueError("trusted scaffold edits must be outside the editable candidate")

    def files(field, *, trusted):
        values = manifest.get(field)
        if not isinstance(values, dict) or (not trusted and not values):
            raise ValueError(f"scaffold {field} must be a mapping" + ("" if trusted else " with files"))
        result = {}
        for source_value, destination_value in values.items():
            source = contained_path(manifest_path.parent, relative_path(source_value, field))
            if not source.is_file():
                raise ValueError(f"scaffold source is not a regular file: {source}")
            destination = relative_path(destination_value, field)
            if trusted:
                outside_candidate(destination)
            if destination in result:
                raise ValueError(f"duplicate scaffold destination: {destination}")
            result[destination] = source
        return result

    edits = manifest.get("text_edits", [])
    if not isinstance(edits, list):
        raise ValueError("scaffold text_edits must be a list")
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {"path", "pattern", "replacement", "matches"}:
            raise ValueError("scaffold text edits require path, pattern, replacement and matches")
        outside_candidate(relative_path(edit["path"], "scaffold edit path"))
        if (not isinstance(edit["pattern"], str) or not edit["pattern"]
                or not isinstance(edit["replacement"], str)
                or type(edit["matches"]) is not int or edit["matches"] < 1):
            raise ValueError("invalid scaffold text edit")
        try:
            re.compile(edit["pattern"], re.DOTALL)
        except re.error as error:
            raise ValueError(f"invalid scaffold edit pattern: {error}") from error
    return {
        "id": manifest["id"], "path": manifest_path, "manifest": manifest,
        "candidate_path": candidate, "candidate_files": files("candidate_files", trusted=False),
        "workspace_paths": workspace, "trusted_files": files("trusted_files", trusted=True),
        "text_edits": edits,
    }


def apply_scaffold_trusted_files(scaffold: dict, root: Path) -> None:
    for destination, source in scaffold["trusted_files"].items():
        target = contained_path(root, destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for edit in scaffold["text_edits"]:
        target = contained_path(root, PurePosixPath(edit["path"]))
        text = target.read_text(encoding="utf-8")
        patched, matches = re.subn(edit["pattern"], edit["replacement"], text, flags=re.DOTALL)
        if matches != edit["matches"]:
            raise ValueError(f"scaffold edit for {edit['path']} expected {edit['matches']} matches, got {matches}")
        target.write_text(patched, encoding="utf-8")


def materialize_scaffold_candidate(scaffold: dict, root: Path) -> None:
    destination = contained_path(root, scaffold["candidate_path"])
    if destination.exists():
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    destination.mkdir(parents=True)
    for relative, source in scaffold["candidate_files"].items():
        target = contained_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
