"""Trusted model access routes shared by the compiler and gateway.

The public selector is still called ``provider``. Definitions contain no secret
values and are never supplied by a harness. Runtime parsers are named here and
resolved by the gateway; reading this registry needs no server dependencies.
"""
from pathlib import Path
import json
import os
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gateway_auth import profile_authentication
from provider_profiles import PROFILES


# Configuration is data; retain the historical exports for existing callers.
from access_config import ACCESS_ROUTES, validate_access_routes


def configured_provider(name, profile):
    """Normalize the existing providers.json format into an access-route definition."""
    return {
        "authentication": profile_authentication(profile),
        "routes": set(profile["routes"]),
        "upstream_env": name.upper().replace("-", "_") + "_UPSTREAM_BASE_URL",
        "upstream_default": profile["base_url"],
        "auth": "gateway_secret",
        "billed": profile["billed"],
        "passthrough": (),
        "usage_parser": "openai",
        "models": profile["models"],
        "model_header": profile["model_header"],
    }


DEFAULT_MODEL_ACCESS = validate_access_routes({
    name: {**config, "routes": sorted(config["routes"]), "passthrough": list(config["passthrough"])}
    for name, config in {
        **ACCESS_ROUTES,
        **{name: configured_provider(name, profile) for name, profile in PROFILES.items()},
    }.items()
})

from access_selection import resolve_routes

# Set once by the trusted launcher before importing the gateway. Requests cannot
# change it. Invalid explicit input never falls back to the default registry.
ACCESS_SELECTION = json.loads(os.environ.get("DUNGENESS_ACCESS_SELECTION", "{}"))
MODEL_ACCESS = resolve_routes(DEFAULT_MODEL_ACCESS, ACCESS_SELECTION)

# Historical import aliases; HTTP registration uses the full registry.
OPENAI_ROUTES = MODEL_ACCESS.get("openai", {}).get("routes", set())
ANTHROPIC_ROUTES = MODEL_ACCESS.get("anthropic", {}).get("routes", set())
OPENROUTER_ROUTES = MODEL_ACCESS.get("openrouter", {}).get("routes", set())
CHATGPT_ROUTES = MODEL_ACCESS.get("openai-chatgpt", {}).get("routes", set())


def credential_names(config):
    """Required private values, derived from the very recipe the gateway applies."""
    names = set()
    for source in config["authentication"]["sources"]:
        for spec in [*source["headers"].values(), source.get("expires_at", {})]:
            if "env" in spec and "default" not in spec:
                names.add(spec["env"])
    return names


def credential_files(config):
    """Existing private-file inputs; no credential is opened during compilation."""
    return [source for source in config["authentication"]["sources"] if "file_env" in source]


def credential_requirements(access_routes, selections=None):
    """Describe selected private inputs without reading credentials or logging in.

    Each current route uses one explicit authentication source. Alternative
    sources/account selection need a deliberate contract instead of requiring
    every possible credential or silently choosing a fallback.
    """
    registry = MODEL_ACCESS if selections is None else resolve_routes(MODEL_ACCESS, selections)
    result = {"schema_version": 1, "environment": {}, "files": {}}
    for name in sorted(set(access_routes)):
        if name not in registry:
            raise ValueError("Unknown model access route.")
        config = registry[name]
        if len(config["authentication"]["sources"]) != 1:
            raise ValueError("Access route requires explicit authentication source selection.")
        for key in sorted(credential_names(config)):
            result["environment"][key] = "TESTBED_" + key
        for source in credential_files(config):
            specs = [*source["headers"].values(), source.get("expires_at", {})]
            result["files"][source["host_env"]] = {
                "gateway_env": source["file_env"],
                "mount_path": source["mount_path"],
                "paths": [spec["path"] for spec in specs if "path" in spec],
            }
    return result


def gateway_base_url(provider, api):
    route = MODEL_ACCESS[provider].get("gateway_route", provider)
    suffix = "" if api == "anthropic-messages" else "/v1"
    return f"http://gateway:8080/model/{route}{suffix}"


def upstream_model(config, model):
    """Resolve configured aliases without changing built-in provider semantics."""
    if "models" not in config:
        return model
    if config["models"]:
        if model not in config["models"]:
            raise ValueError("Model is not mapped by the trusted provider profile.")
        return config["models"][model]["upstream"]
    if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", model):
        raise ValueError("Use the direct provider model ID without a vendor prefix.")
    return model


def validate_upstream_settings(environment):
    """Accept legacy settings only when they name the registered destination.

    Keep the variable names to diagnose old deployments instead of silently
    changing their destination. Never include a supplied URL in an error: it
    could contain credentials. Requests always use the registry's URL.
    """
    for name, config in MODEL_ACCESS.items():
        variable = config["upstream_env"]
        value = environment.get(variable)
        if value is not None and value.rstrip("/") != config["upstream_default"].rstrip("/"):
            raise ValueError(
                f"{variable} cannot override the fixed upstream for {name}; "
                "select a supported provider from the trusted registry."
            )
