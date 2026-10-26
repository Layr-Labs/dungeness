"""Stage gateway credentials outside renders, records and container metadata."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import tempfile

import yaml


def _write_private(path: Path, text: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)


@contextmanager
def gateway_credentials(render: Path, env_file: Path, environment: dict[str, str]):
    """Yield a sanitized Harbor environment and empty env file for one run.

    Match Harbor's explicit env-file precedence. Only variables referenced by
    the trusted Compose render are imported from that file. Secret selectors
    are resolved separately and never passed to Harbor or Docker as values.
    Linux uses shared memory; other local platforms use a private temp directory.
    The caller must leave this context after container teardown.
    """
    # Metadata commands (providers/capabilities) are also invoked by Catalyst's
    # Python interpreter. Only execution needs the CLI's pinned dotenv runtime.
    from dotenv import dotenv_values

    compose_text = (render / "environment/docker-compose.yaml").read_text()
    compose = yaml.safe_load(compose_text)
    sources = compose["services"]["gateway"]["x-dungeness-credential-env"]
    if not isinstance(sources, dict) or any(
        not isinstance(name, str) or not isinstance(source, str)
        or not re.fullmatch(r"[A-Z][A-Z0-9_]*", name)
        or not re.fullmatch(r"[A-Z][A-Z0-9_]*", source)
        for name, source in sources.items()
    ):
        raise ValueError("Invalid gateway credential selectors; re-render the run")
    if not env_file.is_file():
        raise ValueError("Run environment file is unavailable")
    supplied = {**os.environ, **{k: v for k, v in dotenv_values(env_file).items() if v is not None}}
    values = {}
    for name, source in sources.items():
        value = supplied.get(source)
        if not value or any(ord(c) < 32 or ord(c) > 126 for c in value):
            raise ValueError(f"Required gateway credential {source} is missing or invalid")
        values[name] = value
    secret_names = set(sources) | set(sources.values()) | {
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "EXA_API_KEY"}
    # Base variables are for host process execution. Env-file imports are limited
    # to the compiler's explicit non-secret interpolation points.
    safe = {k: v for k, v in environment.items()
            if k not in secret_names and not k.startswith("TESTBED_")}
    references = set(re.findall(r"\$\{([A-Z][A-Z0-9_]*)", compose_text))
    references.discard("DUNGENESS_CREDENTIALS_FILE")
    for name in references - secret_names:
        if name in supplied:
            safe[name] = supplied[name]
    parent = "/dev/shm" if Path("/dev/shm").is_dir() and os.access("/dev/shm", os.W_OK) else None
    with tempfile.TemporaryDirectory(prefix="dungeness-credentials-", dir=parent) as directory:
        root = Path(directory)
        root.chmod(0o700)
        credential_file = root / "credentials.json"
        _write_private(credential_file, json.dumps(values))
        empty_env = root / "harbor.env"
        _write_private(empty_env, "# Credentials are supplied only through the gateway file mount.\n")
        safe["DUNGENESS_CREDENTIALS_FILE"] = str(credential_file)
        yield safe, empty_env
