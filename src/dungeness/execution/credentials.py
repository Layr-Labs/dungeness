"""Stage gateway credentials outside renders, records and container metadata."""
from contextlib import contextmanager
import os
from pathlib import Path
import re

import yaml

from dungeness.credential_access import prepare_credentials


@contextmanager
def gateway_credentials(render: Path, env_file: Path, environment: dict[str, str]):
    """Yield a sanitized Harbor environment and empty env file for one run.

    Match Harbor's explicit env-file precedence. Only variables referenced by
    the trusted Compose render are imported from that file. Secret selectors
    are resolved separately and never passed to Harbor or Docker as values.
    Linux uses shared memory; other local platforms use a private temp directory.
    The caller must leave this context after container teardown.
    """
    # Metadata commands (providers/capabilities) are also invoked by OpenRSI's
    # Python interpreter. Only execution needs the CLI's pinned dotenv runtime.
    from dotenv import dotenv_values

    compose_text = (render / "environment/docker-compose.yaml").read_text()
    compose = yaml.safe_load(compose_text)
    gateway = compose["services"]["gateway"]
    requirements = {
        "schema_version": 1,
        "environment": gateway["x-dungeness-credential-env"],
        "files": gateway.get("x-dungeness-credential-files", {}),
    }
    if not env_file.is_file():
        raise ValueError("Run environment file is unavailable")
    supplied = {**os.environ, **{k: v for k, v in dotenv_values(env_file).items() if v is not None}}
    with prepare_credentials(requirements, supplied) as (paths, empty_env):
        sources = requirements["environment"]
        secret_names = set(sources) | set(sources.values()) | {
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "EXA_API_KEY"}
        # Preserve legacy env-file precedence and explicit interpolation points.
        safe = {k: v for k, v in environment.items()
                if k not in secret_names and not k.startswith("TESTBED_")}
        references = set(re.findall(r"\$\{([A-Z][A-Z0-9_]*)", compose_text))
        references.discard("DUNGENESS_CREDENTIALS_FILE")
        for name in references - secret_names:
            if name in supplied:
                safe[name] = supplied[name]
        safe.update(paths)
        yield safe, empty_env
