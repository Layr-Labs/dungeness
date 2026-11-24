# Integrating model access

For a coding agent building a solver harness, start with the harness section
below. Credential preparation belongs to the trusted launcher running outside
the harness. See [terms](model-access.md) and the
[access-route table](gateway-authentication.md#llm-access-routes).

## Building or adapting a solver harness

1. Read the `models` entries in the JSON file named by `DUNGENESS_TASK`. Use each
   selected model's `provider` (historical access-route ID), `request_model`,
   `api` and assigned `base_url`. Match the client's protocol to `api`.
2. Configure the client to call that gateway URL using the placeholder `testbed`
   credential. Real account credentials, login files and account discovery
   belong outside the harness. Do not copy them into its source or image.
3. Preserve streaming usage and tool history. Handle the gateway's structured
   [recovery responses](command-harness.md#required-request-error-handling):
   stop when instructed, retry with bounded backoff when permitted, and correct
   rejected requests before resending. Preserve the best evaluated candidate.
4. Test a complete tool-call turn, recovery and cancellation using synthetic
   upstream responses. Verify the actual harness wrapper, not only the gateway.
   Model discovery or a successful text response alone is insufficient.

The [command-harness contract](command-harness.md) documents the task file,
execution entrypoint and evaluator interface. The harness owns its agent loop.
Choosing an access route does not select Codex, Claude Code or another harness.

This is a short handoff to a coding agent:

> Integrate this harness with Dungeness's command-harness contract. Read the
> selected models and gateway URLs from DUNGENESS_TASK; use the declared protocol,
> requested model and placeholder testbed credential. Keep real credentials and
> login discovery outside the harness. Implement the documented gateway recovery
> responses and preserve evaluated candidates. Test tool history, retry, stop
> and cancellation with synthetic responses. Report the tested access routes,
> protocol limitations and remaining live checks.

## Selecting models

Model names in this guide are examples; maintained configuration lives in code.
The trusted [route configuration](../services/gateway/model-access.json) defines supported
protocols and endpoints. The installed [pricing schedule](../services/gateway/pricing.yaml)
lists exact `provider`, `upstream_id` and `request_models` combinations and their
reference rates. Use those sources rather than maintaining a separate model list
in documentation. A caller may install its own reviewed schedule.

The caller selects models in the run spec; the harness uses the resulting
`DUNGENESS_TASK` entries. For OpenAI/ChatGPT coding harnesses, use Responses and
preserve tool and encrypted reasoning history. Follow the
[request policy](gateway-request-policy.md#thinking-controls) for thinking options
and signature handling. Use the model's supported effort on each request; keep
the full assistant history when returning locally executed tool results.

Reference prices measure comparison cost, not subscription billing or account
entitlement. Adding a model requires qualifying the caller's catalog and packaged
runtime together; a selector change alone is insufficient.

## Discovering credential inputs

Run from a trusted, pinned Dungeness checkout:

```sh
./dungeness capabilities
./dungeness providers --details
```

`model-credential-inputs-v1` advertises the detailed description and preparation
interface. `providers` without the flag retains its original JSON exactly.
Detailed output adds `access_routes`, with each route's ID, fixed upstream,
operations and `credential_inputs`. No login, credential read or inference occurs.
For OpenAI API access, the input description is:

```json
{
  "schema_version": 1,
  "environment": {"OPENAI_API_KEY": "TESTBED_OPENAI_API_KEY"},
  "files": {}
}
```

`environment` maps the gateway's private field name to the launcher's input name.
It does not instruct the launcher to put real values into Docker's environment.
ChatGPT's `files` entry instead names `DUNGENESS_CODEX_AUTH_FILE`, its gateway
variable, mount destination and required JSON field paths. These descriptions
are recipes with names only. Implementation availability, account eligibility,
model availability and attested qualification are separate checks.

## Integrating a trusted launcher

Ordinary `dungeness run` already prepares credentials and tears them down after
the containers stop. A launcher supplies its existing private env file and,
for ChatGPT, the access-file path. Existing input names remain unchanged.

For a different trusted launcher, the pinned checkout exposes
`dungeness.credential_access` under `src`:

```python
from dungeness.credential_access import credential_requirements, prepare_credentials

requirements = credential_requirements(["openai", "openai-chatgpt"])
# Obtain these inputs through your trusted local setup, never a harness or prompt.
supplied = {
    "TESTBED_OPENAI_API_KEY": selected_api_key,
    "DUNGENESS_CODEX_AUTH_FILE": selected_private_login_path,
}
with prepare_credentials(requirements, supplied) as (private_paths, empty_env_file):
    # Start your backend with these private file mounts and no real-key env vars.
    # Keep this context open until every container using the files has stopped.
    # private_paths contains host paths, never credential values.
    pass
```

The example illustrates preparation, not a complete backend launcher.
`selected_api_key` and `selected_private_login_path` are values supplied by your
existing trusted account setup. The resolver reads only `supplied`; it does not
search ambient credentials, choose another account, refresh access or contact a
provider. The gateway checks expiry on admitted requests when the route's recipe
declares an expiry field; it does not infer expiry for every token format.

The returned `DUNGENESS_CREDENTIALS_FILE` is the private JSON map containing
selected key/token values. Mount it read-only at `/run/dungeness/credentials.json`
and set the gateway's variable to that container path. For each described file
input, mount its returned host path at `mount_path`, then set `gateway_env` to
that container path. Only the gateway receives these mounts. The generated
Compose configuration already does this.

Files are 0600 inside a 0700 temporary directory. Source JSON must be a bounded,
private, regular file with no symlinks or extra hard links. Only JSON fields named
by the authentication recipe are staged; unrelated refresh tokens and login
metadata stay in the original source. The original file is never deleted or
modified. Missing/malformed inputs fail with input names, not secret values.

The context removes staged files on normal exit, exceptions and cancellation
that unwinds Python. The Dungeness launcher handles SIGTERM and stops containers
before closing it. SIGKILL or host failure cannot guarantee cleanup. Existing
compiled renders without file-input metadata retain their original file mounts;
recompile to receive managed file snapshots.

## Where endpoints are maintained

Edit `upstream_default` in [model-access.json](../services/gateway/model-access.json).
This file also holds operations, authentication recipes and usage-parser names.
[access_config.py](../services/gateway/access_config.py) validates the data;
[model_access.py](../services/gateway/model_access.py) supplies the shared interface.
All routes use the same HTTP handler, including configured `gateway_route` aliases.
The gateway appends an allowed API operation to this fixed URL and rejects
conflicting environment overrides. A harness cannot choose the upstream endpoint.

## Adding an access route

Add an entry to `access_routes` in `model-access.json`, then add its model rates
to `pricing.yaml`. For example, this complete entry reuses Chat Completions:

```json
{
  "example-api": {
    "upstream_default": "https://api.example.invalid/v1",
    "upstream_env": "EXAMPLE_API_UPSTREAM_BASE_URL",
    "routes": ["chat/completions"],
    "auth": "gateway_secret",
    "billed": true,
    "passthrough": [],
    "usage_parser": "openai",
    "authentication": {
      "sources": [{
        "headers": {
          "authorization": {"env": "EXAMPLE_API_KEY", "prefix": "Bearer "}
        }
      }]
    },
    "models": {
      "example-model": {"upstream": "example-model", "catalog": "example/example-model"}
    }
  }
}
```

The caller supplies `TESTBED_EXAMPLE_API_KEY`. Discovery, credential preparation,
compiler selection and `/model/example-api/v1/chat/completions` use this entry
without adding a Python handler. `models` optionally restricts and maps public
model names; pricing and the run's model allowlist are still required.
An optional `model_header` sends the mapped model in a fixed `x-*` header.

This is trusted runtime configuration, not a harness input. An existing protocol
and authentication recipe can be configured here; a new wire format or unsupported
history fields require gateway code and policy tests. No token alone establishes
protocol compatibility or account entitlement. Older `providers.json` files are
read for compatibility; use [the migration guide](migration.md#route-configuration)
instead of maintaining both formats.

The compiler and credential resolver derive inputs from the same registry.
Current recipes support one explicit source per access route; multiple accounts,
alternative sources and refresh require a separate explicit design. Keep model
usage and reference prices complete, with no silent paid-API fallback.

Validate private staging, missing/expired credentials, field filtering and
cleanup; then streaming, tool history, accounting, error recovery and an actual
harness run. VM packaging and attested qualification follow separately.
Neither this interface nor Google discovery adds a Google execution adapter.
