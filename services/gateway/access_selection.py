"""Validate public per-run choices against an immutable access-route registry.

Only endpoint and authentication recipe identifiers are caller-selected. Secrets,
URL paths, model aliases, parsers and prices are not configurable here.
"""
from copy import deepcopy
import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def public_policy(registry):
    """Export only public policy. This is derived data, never a second registry."""
    return {
        "schema_version": 1,
        "routes": {
            name: {
                "endpoint": config["upstream_default"],
                "transport": config.get("transport", "passthrough"),
                "operations": sorted(config["routes"]),
                "authentication": sorted(
                    other for other, recipe in registry.items()
                    if compatible(config, recipe)
                ),
            }
            for name, config in sorted(registry.items())
        },
    }


def compatible(config, recipe):
    # Authentication may carry protocol headers or a project selector. Do not
    # transplant it between unrelated hosts, transports or path templates.
    return (config["upstream_default"] == recipe["upstream_default"]
            and config.get("transport", "passthrough") == recipe.get("transport", "passthrough")
            and config.get("project_header") == recipe.get("project_header")
            and config.get("project") == recipe.get("project"))


def policy_digest(registry):
    # Bind all trusted recipe/mapping details as well as the public selection rules.
    document = {
        name: {**config, "routes": sorted(config["routes"]), "passthrough": list(config["passthrough"])}
        for name, config in sorted(registry.items())
    }
    return hashlib.sha256(canonical(document)).hexdigest()


def resolve_routes(registry, selections):
    """Return a private copy; never mutate defaults shared with another run."""
    if not isinstance(selections, dict) or len(selections) > 16:
        raise ValueError("Model access routes must be a mapping with at most 16 entries.")
    resolved = deepcopy(registry)
    for provider, selection in selections.items():
        if (provider not in registry or not isinstance(selection, dict)
                or set(selection) != {"endpoint", "authentication"}):
            raise ValueError("Model access selection requires an approved route, endpoint and authentication.")
        config = registry[provider]
        recipe_id = selection["authentication"]
        if (not isinstance(selection["endpoint"], str)
                or selection["endpoint"] != config["upstream_default"]
                or not isinstance(recipe_id, str) or recipe_id not in registry
                or not compatible(config, registry[recipe_id])):
            raise ValueError("Endpoint or authentication method is not allowed for this route.")
        resolved[provider]["authentication"] = deepcopy(registry[recipe_id]["authentication"])
        resolved[provider]["billed"] = registry[recipe_id]["billed"]
    return resolved


def selection_evidence(registry, selections):
    resolve_routes(registry, selections)
    document = {"schema_version": 1, "policy_sha256": policy_digest(registry), "routes": selections}
    return {**document, "sha256": hashlib.sha256(canonical(document)).hexdigest()}


def export_policy(registry, prices):
    """Public endpoint/method/model policy for attestation admission.

    Prices and their identity are frozen too; caller-controlled price tables are
    not part of a selection. Applications may narrow this exported policy.
    """
    policy = {**public_policy(registry), "registry_sha256": policy_digest(registry),
              "pricing_sha256": hashlib.sha256(canonical(prices)).hexdigest()}
    for name, config in registry.items():
        models = {}
        for entry in prices["entries"]:
            if entry["provider"] != name:
                continue
            for model in entry["request_models"]:
                mapping = config.get("models")
                if mapping and (model not in mapping or mapping[model]["catalog"] != entry["upstream_id"]):
                    continue
                if model in models:
                    raise ValueError("Ambiguous model pricing policy.")
                models[model] = entry["upstream_id"]
        policy["routes"][name]["models"] = models
    return policy
