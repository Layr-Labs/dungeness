"""Describe and prepare credentials for a trusted launcher, never a harness.

Caller-selected inputs are explicit; this module performs no login, discovery,
refresh, network access or account fallback. The context must outlive the run's
containers. Only paths leave it; original credential sources remain untouched.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sys
import tempfile

def credential_requirements(access_routes):
    """Read the trusted registry lazily, without loading it into adapter imports."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services/gateway"))
    from model_access import credential_requirements as describe
    return describe(access_routes)


def _name(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Z][A-Z0-9_]*", value)


def _write_private(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)


def _validate(requirements):
    if (not isinstance(requirements, dict)
            or set(requirements) != {"schema_version", "environment", "files"}
            or type(requirements["schema_version"]) is not int
            or requirements["schema_version"] != 1):
        raise ValueError("Invalid credential requirements; use the trusted runtime's description.")
    sources, files = requirements["environment"], requirements["files"]
    if (not isinstance(sources, dict)
            or any(not _name(key) or not _name(source) for key, source in sources.items())
            or not isinstance(files, dict)):
        raise ValueError("Invalid gateway credential selectors; re-render the run")
    for name, spec in files.items():
        if (not _name(name) or name == "DUNGENESS_CREDENTIALS_FILE"
                or name in sources or name in sources.values()
                or not isinstance(spec, dict)
                or set(spec) != {"gateway_env", "mount_path", "paths"}
                or not _name(spec["gateway_env"])
                or not isinstance(spec["mount_path"], str)
                or not spec["mount_path"].startswith("/run/dungeness/")
                or not isinstance(spec["paths"], list) or not spec["paths"]
                or any(not isinstance(path, list) or not path
                       or any(not isinstance(part, str) or not part for part in path)
                       for path in spec["paths"])):
            raise ValueError("Invalid gateway credential file selectors; re-render the run")
    return sources, files


def _selected_document(filename, paths):
    """Copy only authentication fields, excluding refresh tokens and login metadata."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services/gateway"))
    from gateway_auth import private_json_file
    document = private_json_file(filename)
    selected = {}
    for path in paths:
        value = document
        for part in path:
            value = value.get(part) if isinstance(value, dict) else None
        if (not isinstance(value, str) or not value
                or any(ord(c) < 32 or ord(c) > 126 for c in value)):
            raise ValueError("Required credential field is missing or invalid.")
        target = selected
        for part in path[:-1]:
            target = target.setdefault(part, {})
        target[path[-1]] = value
    return selected


@contextmanager
def prepare_credentials(requirements, supplied):
    """Yield (host path variables, empty env file) for these explicit inputs.

    ``requirements`` comes from credential_requirements() or a trusted compiled
    render. ``supplied`` maps input names to values/private source-file paths.
    No ambient environment is read. Errors identify input names, never values.
    Gateway authentication checks recipe-declared expiry on each model request.
    """
    sources, files = _validate(requirements)
    values = {}
    for key, source in sources.items():
        value = supplied.get(source)
        if (not isinstance(value, str) or not value
                or any(ord(c) < 32 or ord(c) > 126 for c in value)):
            raise ValueError(f"Required gateway credential {source} is missing or invalid")
        values[key] = value
    parent = "/dev/shm" if Path("/dev/shm").is_dir() and os.access("/dev/shm", os.W_OK) else None
    with tempfile.TemporaryDirectory(prefix="dungeness-credentials-", dir=parent) as directory:
        root = Path(directory)
        root.chmod(0o700)
        credential_file = root / "credentials.json"
        _write_private(credential_file, json.dumps(values))
        paths = {"DUNGENESS_CREDENTIALS_FILE": str(credential_file)}
        for index, (name, spec) in enumerate(files.items()):
            filename = supplied.get(name)
            try:
                if not isinstance(filename, str) or not filename:
                    raise ValueError
                selected = _selected_document(filename, spec["paths"])
            except (OSError, ValueError, TypeError, RecursionError):
                raise ValueError(f"Required gateway credential file {name} is missing or invalid") from None
            staged = root / f"access-{index}.json"
            _write_private(staged, json.dumps(selected))
            paths[name] = str(staged)
        empty_env = root / "harbor.env"
        _write_private(empty_env, "# Credentials are supplied only through gateway file mounts.\n")
        yield paths, empty_env
