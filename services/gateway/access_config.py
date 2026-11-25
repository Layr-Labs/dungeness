"""Load trusted route configuration without credentials, environment or network."""
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

CONFIG_PATH = Path(__file__).with_name("model-access.json")
OPERATIONS = {
    "responses", "responses/compact", "chat/completions", "completions",
    "embeddings", "models", "messages", "messages/count_tokens",
}
TRANSPORT_HEADERS = {
    "host", "content-type", "content-length", "transfer-encoding", "connection",
    "accept", "accept-encoding", "cookie", "proxy-authorization",
}


def _matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def _text(value):
    return isinstance(value, str) and all(32 <= ord(c) <= 126 for c in value)


def _require(condition):
    if not condition:
        # Do not echo configuration values: a mistaken input might be a secret.
        raise ValueError("Invalid trusted model-access configuration.")


def _value(spec, file_source):
    _require(isinstance(spec, dict))
    selectors = set(spec) & {"env", "path", "literal"}
    _require(len(selectors) == 1 and not set(spec) - selectors - {"default", "prefix"})
    _require("prefix" not in spec or _text(spec["prefix"]))
    if "env" in spec:
        _require(not file_source and _matches(r"[A-Z][A-Z0-9_]*", spec["env"]))
        _require("default" not in spec or (_text(spec["default"]) and bool(spec["default"])))
    elif "path" in spec:
        _require(file_source and "default" not in spec)
        _require(isinstance(spec["path"], list) and bool(spec["path"])
                 and all(isinstance(part, str) and bool(part) for part in spec["path"]))
    else:
        _require("default" not in spec and _text(spec["literal"]) and bool(spec["literal"]))


def _authentication(recipe):
    _require(isinstance(recipe, dict) and set(recipe) == {"sources"})
    sources = recipe["sources"]
    _require(isinstance(sources, list) and len(sources) == 1)
    source = sources[0]
    _require(isinstance(source, dict) and "headers" in source)
    file_keys = {"file_env", "host_env", "mount_path"}
    _require(not set(source) - {"headers", "expires_at"} - file_keys)
    file_source = bool(set(source) & file_keys)
    if file_source:
        _require(file_keys <= set(source))
        _require(all(_matches(r"[A-Z][A-Z0-9_]*", source[key]) for key in ("file_env", "host_env")))
        mount = source["mount_path"]
        _require(isinstance(mount, str) and mount.startswith("/run/dungeness/")
                 and ".." not in PurePosixPath(mount).parts and ":" not in mount)
    headers = source["headers"]
    _require(isinstance(headers, dict) and bool(headers))
    for header, spec in headers.items():
        _require(_matches(r"[a-z][a-z0-9-]*", header) and header not in TRANSPORT_HEADERS)
        _value(spec, file_source)
    if "expires_at" in source:
        _value(source["expires_at"], file_source)


def load_access_routes(path=CONFIG_PATH):
    """Read the pinned file; malformed or missing configuration has no fallback."""
    document = json.loads(Path(path).read_text())
    _require(isinstance(document, dict) and set(document) == {"schema_version", "access_routes"})
    _require(type(document["schema_version"]) is int and document["schema_version"] == 1)
    return validate_access_routes(document["access_routes"])


def validate_access_routes(entries):
    """Validate the single registry, including any translated legacy profiles."""
    _require(isinstance(entries, dict) and bool(entries))
    required = {
        "authentication", "routes", "upstream_env", "upstream_default",
        "auth", "billed", "passthrough", "usage_parser",
    }
    result, aliases, variables = {}, set(), set()
    for name, config in entries.items():
        _require(_matches(r"[a-z][a-z0-9-]{0,47}", name))
        _require(isinstance(config, dict) and required <= set(config)
                 and not set(config) - required - {"gateway_route", "models", "model_header", "transport", "project_header", "authentication_method"})
        if "authentication_method" in config:
            _require(_matches(r"[a-z][a-z0-9-]{0,47}", config["authentication_method"]))
        url = config["upstream_default"]
        _require(_text(url) and bool(url) and " " not in url and "\\" not in url)
        parsed = urlsplit(url)
        _require(parsed.scheme == "https" and bool(parsed.hostname)
                 and not parsed.username and not parsed.password
                 and not parsed.query and not parsed.fragment and parsed.path.startswith("/"))
        operations = config["routes"]
        _require(isinstance(operations, list) and bool(operations)
                 and all(isinstance(item, str) and item in OPERATIONS for item in operations))
        _require(len(set(operations)) == len(operations))
        _require(config["auth"] == "gateway_secret" and type(config["billed"]) is bool)
        _require(config["usage_parser"] in ("openai", "anthropic"))
        transport = config.get("transport", "passthrough")
        _require(transport in ("passthrough", "google-generate-content"))
        if transport != "passthrough":
            _require(set(operations) <= {"chat/completions", "models"}
                     and "chat/completions" in operations and config["usage_parser"] == "openai")
        variable = config["upstream_env"]
        _require(_matches(r"[A-Z][A-Z0-9_]*", variable) and variable not in variables)
        variables.add(variable)
        alias = config.get("gateway_route", name)
        _require(_matches(r"[a-z][a-z0-9-]{0,47}", alias) and alias not in aliases)
        _require(alias == name or alias not in entries)
        aliases.add(alias)
        headers = config["passthrough"]
        _require(isinstance(headers, list) and all(
            _matches(r"[a-z][a-z0-9_-]*", header) and header not in TRANSPORT_HEADERS
            for header in headers))
        _authentication(config["authentication"])
        if "project_header" in config:
            # Vertex's project is caller-owned account configuration. Only a
            # trusted authentication header may supply this single path segment.
            header = config["project_header"]
            _require(transport == "google-generate-content"
                     and _matches(r"[a-z][a-z0-9-]*", header)
                     and header in config["authentication"]["sources"][0]["headers"]
                     and header not in headers)
        if "models" in config:
            _require(isinstance(config["models"], dict))
            for model, mapping in config["models"].items():
                _require(_matches(r"[A-Za-z0-9._:-]{1,120}", model))
                _require(isinstance(mapping, dict) and set(mapping) == {"upstream", "catalog"})
                _require(_matches(r"[A-Za-z0-9._:-]{1,120}", mapping["upstream"]))
                _require(_matches(r"[a-z0-9-]+/[A-Za-z0-9._:-]{1,120}", mapping["catalog"]))
        model_header = config.get("model_header")
        if model_header is not None:
            _require(_matches(r"x-[a-z0-9-]+", model_header))
            _require(all(model_header not in source["headers"]
                         for source in config["authentication"]["sources"]))
            _require(model_header not in headers)
        result[name] = {**config, "routes": set(operations), "passthrough": tuple(headers)}
    return result


ACCESS_ROUTES = load_access_routes()
