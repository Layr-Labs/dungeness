"""Resolve a caller's endpoint and authentication method to a trusted route.

The selected route supplies its complete protocol, credential requirements,
model mappings and pricing identity. No configuration is transplanted between
routes, and no untrusted URL becomes an upstream.
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
                "authentication": [config.get("authentication_method", name)],
            }
            for name, config in sorted(registry.items())
        },
    }


def resolve_endpoint(registry, selection):
    """Exact matching includes scheme, host, port and base path; never guess."""
    if (not isinstance(selection, dict) or set(selection) != {"endpoint", "authentication"}
            or not all(isinstance(value, str) and value for value in selection.values())):
        raise ValueError("Model access requires an approved endpoint and authentication method.")
    matches = [
        name for name, config in registry.items()
        if config["upstream_default"] == selection["endpoint"]
        and config.get("authentication_method", name) == selection["authentication"]
    ]
    if len(matches) != 1:
        raise ValueError("Endpoint and authentication must identify one approved route.")
    return matches[0]


def resolve_model(registry, model):
    """Legacy provider selection stays unchanged; endpoint selection adds its ID."""
    if not isinstance(model, dict):
        raise ValueError("Model must be a mapping.")
    if not ({"endpoint", "authentication"} & set(model)):
        return dict(model)
    selection = {key: model.get(key) for key in ("endpoint", "authentication")}
    provider = resolve_endpoint(registry, selection)
    if "provider" in model and model["provider"] != provider:
        raise ValueError("Explicit provider conflicts with the selected endpoint and authentication.")
    return {**model, "provider": provider}


def model_selections(registry, models):
    """Public evidence for normalized selections; not a second configuration."""
    selections = {}
    for model in models:
        resolved = resolve_model(registry, model)
        if "endpoint" in resolved:
            selections[resolved["provider"]] = {
                key: resolved[key] for key in ("endpoint", "authentication")}
    return selections


def policy_digest(registry):
    # Bind all trusted recipe/mapping details as well as the public selection rules.
    document = {
        name: {**config, "routes": sorted(config["routes"]), "passthrough": list(config["passthrough"])}
        for name, config in sorted(registry.items())
    }
    return hashlib.sha256(canonical(document)).hexdigest()


def resolve_routes(registry, selections):
    """Validate canonical gateway selections without changing any route behavior."""
    if not isinstance(selections, dict) or len(selections) > 16:
        raise ValueError("Model access routes must be a mapping with at most 16 entries.")
    resolved = deepcopy(registry)
    for provider, selection in selections.items():
        if resolve_endpoint(registry, selection) != provider:
            raise ValueError("Gateway route differs from the approved endpoint selection.")
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
