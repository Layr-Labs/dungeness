"""Trusted model connections shared by the compiler and gateway.

The public selector is still called ``provider``. Definitions contain no secret
values and are never supplied by a harness. Runtime parsers are named here and
resolved by the gateway; reading this registry needs no server dependencies.
"""
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gateway_auth import profile_authentication
from provider_profiles import PROFILES


OPENAI_ROUTES = {"responses", "chat/completions", "embeddings", "models"}
ANTHROPIC_ROUTES = {"messages", "messages/count_tokens"}
OPENROUTER_ROUTES = {"responses", "chat/completions", "completions", "messages", "models"}
CHATGPT_ROUTES = {"responses", "responses/compact"}

MODEL_ACCESS = {
    "openai": {
        "authentication": {"sources": [{"headers": {
            "authorization": {"env": "OPENAI_API_KEY", "prefix": "Bearer "},
        }}]},
        "routes": OPENAI_ROUTES,
        "upstream_env": "OPENAI_UPSTREAM_BASE_URL",
        "upstream_default": "https://api.openai.com/v1",
        "auth": "gateway_secret",
        "billed": True,
        "passthrough": ("openai-beta", "idempotency-key"),
        "usage_parser": "openai",
    },
    "anthropic": {
        "authentication": {"sources": [{"headers": {
            "x-api-key": {"env": "ANTHROPIC_API_KEY"},
            "anthropic-version": {"env": "ANTHROPIC_VERSION", "default": "2023-06-01"},
        }}]},
        "routes": ANTHROPIC_ROUTES,
        "upstream_env": "ANTHROPIC_UPSTREAM_BASE_URL",
        "upstream_default": "https://api.anthropic.com/v1",
        "auth": "gateway_secret",
        "billed": True,
        "passthrough": ("anthropic-beta", "anthropic-version"),
        "usage_parser": "anthropic",
    },
    "claude-subscription": {
        "authentication": {"sources": [{
            "expires_at": {"env": "CLAUDE_ACCESS_TOKEN_EXPIRES_AT"},
            "headers": {
                "authorization": {"env": "CLAUDE_ACCESS_TOKEN", "prefix": "Bearer "},
                "anthropic-version": {"literal": "2023-06-01"},
            },
        }]},
        "routes": ANTHROPIC_ROUTES,
        "upstream_env": "CLAUDE_SUBSCRIPTION_UPSTREAM_BASE_URL",
        "upstream_default": "https://api.anthropic.com/v1",
        "auth": "gateway_secret",
        "billed": False,
        "passthrough": ("anthropic-beta", "anthropic-version"),
        "usage_parser": "anthropic",
    },
    "openrouter": {
        "authentication": {"sources": [{"headers": {
            "authorization": {"env": "OPENROUTER_API_KEY", "prefix": "Bearer "},
        }}]},
        "routes": OPENROUTER_ROUTES,
        "upstream_env": "OPENROUTER_UPSTREAM_BASE_URL",
        "upstream_default": "https://openrouter.ai/api/v1",
        "auth": "gateway_secret",
        "billed": True,
        # OpenRouter serves both OpenAI and Anthropic operations.
        "passthrough": ("http-referer", "x-title", "openai-beta",
                        "anthropic-beta", "anthropic-version"),
        "usage_parser": "openai",
    },
    "openai-chatgpt": {
        "authentication": {"sources": [{
            "file_env": "DUNGENESS_CHATGPT_AUTH_FILE",
            "host_env": "DUNGENESS_CODEX_AUTH_FILE",
            "mount_path": "/run/dungeness/auth.json",
            "headers": {
                "authorization": {"path": ["tokens", "access_token"], "prefix": "Bearer "},
                "chatgpt-account-id": {"path": ["tokens", "account_id"]},
            },
        }]},
        "gateway_route": "chatgpt",
        "routes": CHATGPT_ROUTES,
        "upstream_env": "CHATGPT_UPSTREAM_BASE_URL",
        "upstream_default": "https://chatgpt.com/backend-api/codex",
        "auth": "gateway_secret",
        "billed": False,
        # Trusted account headers override any client-supplied metadata.
        "passthrough": (
            "chatgpt-account-id", "originator", "version", "session_id",
            "session-id", "thread-id", "conversation_id", "x-openai-subagent",
            "x-client-request-id", "x-codex-turn-metadata", "x-codex-installation-id",
            "x-oai-attestation", "x-responsesapi-include-timing", "traceparent",
            "user-agent", "openai-beta",
        ),
        "usage_parser": "openai",
    },
}


def configured_provider(name, profile):
    """Normalize the existing providers.json format into a connection definition."""
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


MODEL_ACCESS.update({name: configured_provider(name, profile) for name, profile in PROFILES.items()})


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
