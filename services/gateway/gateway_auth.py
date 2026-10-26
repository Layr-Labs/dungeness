"""Resolve operator-owned authentication recipes without provider-specific logic.

Recipes never come from a model request. A configured credential file that is
missing or invalid fails closed; it does not select a fallback identity.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat


def credential_value(name, *, private_values=None):
    """Resolve a credential name; file mode never falls back to environment."""
    filename = os.environ.get("DUNGENESS_CREDENTIALS_FILE")
    if filename is None:
        # Standalone gateway compatibility. Compiled runs always require a file.
        return os.environ.get(name)
    try:
        fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_nlink != 1:
                raise ValueError
            raw = stream.read(128 * 1024 + 1)
        if len(raw) > 128 * 1024:
            raise ValueError
        values = json.loads(raw)
        if not isinstance(values, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) for k, v in values.items()
        ):
            raise ValueError
    except (OSError, ValueError, UnicodeError):
        raise ValueError("Gateway credential file is unavailable or invalid.") from None
    if private_values is not None:
        private_values.update(v for v in values.values() if v)
    return values.get(name)


def profile_authentication(profile):
    """Build an authentication recipe from a validated operator profile."""
    source = {"headers": {
        profile.get("credential_header", "authorization"): {
            "env": profile["credential_env"],
            "prefix": profile.get("credential_prefix", "Bearer "),
        },
        **{name: {"literal": value} for name, value in profile["headers"].items()},
        **{name: {"env": env} for name, env in profile.get("credential_headers", {}).items()},
    }}
    if profile["credential_kind"] == "session-token":
        source["expires_at"] = {"env": profile["credential_env"] + "_EXPIRES_AT"}
    return {"sources": [source]}


def _value(spec, document, private_values=None):
    if "env" in spec:
        value = (os.environ.get(spec["env"], spec["default"]) if "default" in spec
                 else credential_value(spec["env"], private_values=private_values))
    elif "path" in spec:
        value = document
        for part in spec["path"]:
            value = value.get(part) if isinstance(value, dict) else None
    else:
        value = spec.get("literal")
    if (not isinstance(value, str) or not value
            or any(ord(c) < 32 or ord(c) > 126 for c in value)):
        raise ValueError("Gateway authentication value is missing or invalid.")
    return spec.get("prefix", "") + value


def authentication_headers(recipe, *, private_values=None):
    """Render a trusted recipe from environment, credential file, or fixed values."""
    selected = None
    document = {}
    for source in recipe["sources"]:
        file_env = source.get("file_env")
        if file_env:
            filename = os.environ.get(file_env)
            if not filename:
                continue
            try:
                with Path(filename).open("rb") as stream:
                    raw = stream.read(128 * 1024 + 1)
                if len(raw) > 128 * 1024:
                    raise ValueError
                document = json.loads(raw)
                if not isinstance(document, dict):
                    raise ValueError
                if private_values is not None:
                    def collect(value):
                        if isinstance(value, str) and value:
                            private_values.add(value)
                        elif isinstance(value, dict):
                            for item in value.values(): collect(item)
                    collect(document)
            except (OSError, ValueError, UnicodeError):
                raise ValueError("Gateway credential file is unavailable or invalid.") from None
        selected = source
        break
    if selected is None:
        raise ValueError("Gateway authentication source is unavailable.")
    if "expires_at" in selected:
        try:
            stamp = _value(selected["expires_at"], document, private_values)
            expiry = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
                raise ValueError
        except (ValueError, OverflowError):
            raise ValueError("Access expired or expiry is invalid; renew locally. No credential fallback.") from None
    headers = {}
    for name, spec in selected["headers"].items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            raise ValueError("Invalid configured authentication header.")
        headers[name] = _value(spec, document, private_values)
        if private_values is not None and ("path" in spec or ("env" in spec and "default" not in spec)):
            private_values.add(_value({**spec, "prefix": ""}, document))
    return headers
