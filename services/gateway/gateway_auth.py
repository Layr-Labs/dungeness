"""Resolve operator-owned authentication recipes without provider-specific logic.

Recipes never come from a model request. A configured credential file that is
missing or invalid fails closed; it does not select a fallback identity.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re


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


def _value(spec, document):
    if "env" in spec:
        value = os.environ.get(spec["env"], spec.get("default"))
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


def authentication_headers(recipe):
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
            except (OSError, ValueError, UnicodeError):
                raise ValueError("Gateway credential file is unavailable or invalid.") from None
        selected = source
        break
    if selected is None:
        raise ValueError("Gateway authentication source is unavailable.")
    if "expires_at" in selected:
        try:
            stamp = _value(selected["expires_at"], document)
            expiry = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
                raise ValueError
        except (ValueError, OverflowError):
            raise ValueError("Access expired or expiry is invalid; renew locally. No credential fallback.") from None
    headers = {}
    for name, spec in selected["headers"].items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            raise ValueError("Invalid configured authentication header.")
        headers[name] = _value(spec, document)
    return headers
