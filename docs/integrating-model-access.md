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

Select an **access route + model** in each `model_access.models` entry. The
`provider` field is the route ID; Dungeness derives the fixed upstream endpoint
and authentication method from that route. Run `./dungeness providers --details`
to inspect the installed routes, endpoints, models and required credential inputs.

```yaml
model_access:
  models:
    - provider: claude-subscription
      upstream_id: anthropic/claude-opus-5
      request_model: claude-opus-5
      api: anthropic-messages
      name_format: request
```

The route supplies credential requirements, model mappings and prices. The
trusted launcher prepares the selected account's credentials separately; never
put credentials in the run specification or harness.

<a id="choosing-an-endpoint-and-authentication-for-a-run"></a>
<details>
<summary>Compatibility with existing endpoint-based configurations</summary>

Existing model profiles with `endpoint` and `authentication` remain supported.
The pair must resolve to exactly one registered route; an explicit `provider`
must agree. URLs match exactly, including scheme and base path. Unknown or
ambiguous choices fail without fallback. This form selects the same route and
does not allow custom destinations, headers, prices or usage parsers. Use
`provider` + model for new configurations.

</details>

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

### Grok API access

Select the official xAI API route and Grok 4.7:

```yaml
model_access:
  models:
    - provider: xai
      upstream_id: x-ai/grok-4.7
      request_model: grok-4.7
      api: openai-responses
      name_format: request
```

The trusted launcher supplies `TESTBED_XAI_API_KEY` through its private env file.
The gateway sends it as a bearer token to the fixed `https://api.x.ai/v1`
endpoint. The harness uses its assigned gateway URL and placeholder `testbed`
key with a Responses-compatible client. No protocol translation is performed.
Chat Completions is also supported through `api: openai-chat`.

Use Grok's supported reasoning effort (`low`, `medium`, `high` or `xhigh`).
Replay native reasoning items, including `encrypted_content`, and local function
results unchanged. Use `store: false` and explicit conversation history; remote
conversation retrieval and provider-hosted tools such as X search, web search
and code execution are unavailable. See the
[Grok developer guide](https://docs.x.ai/developers/grok-4-7).

The pinned OpenRouter reference rates meter input, cached input and output
(including reasoning), with the long-context tier starting at 200,000 input
tokens. This is normalized comparison cost; the provider's `cost_in_usd_ticks`
remains in the retained native response and is not interpreted as `billed_usd`.
This route uses an API key, not a Grok subscription. It does not enable a hosted
platform's funding policy or qualify an attested release.

The [API terms](https://x.ai/legal/terms-of-service-enterprise) permit product
integrations, subject to their conditions and the
[acceptable-use policy](https://x.ai/legal/acceptable-use-policy). The latter
restricts using the service or outputs to develop competing models or products;
route availability is not a determination that every research use is permitted.

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

Routes belong in the trusted registry, not the run specification.
`authentication_method` is the route's public label (`bearer` or `api-key`).
The route's `authentication` recipe describes the actual token source and any
additional headers. To support another approved endpoint using bearer tokens,
add its route data with `authentication_method: bearer`; the same credential
renderer handles it. A new wire protocol can still require adapter code.

For attested integrations, `python tools/export-access-policy.py` exports the
derived endpoint/method/model policy and registry/pricing digests. The application
must freeze that policy in its measured runtime, approve it at the verifier and
bind the selected endpoint, method, model and policy digest into run inputs.
Enabling local configuration alone does not qualify an attested release.

### Adding an endpoint or protocol

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

### Native Google protocol

The Google routes expose native `generateContent` and `streamGenerateContent`.
Use a Google client, not an OpenAI client. The gateway validates the native
request, adds credentials and forwards the conversation without converting its
messages, function calls, signatures or response events. Usage is parsed into
our ledger separately; native response usage fields remain unchanged.

For a harness using the Google Python SDK:

```python
import json, os
from google import genai
from google.genai import types

model = json.load(open(os.environ["DUNGENESS_TASK"]))["models"][0]
assert model["api"] == "google-genai"
client = genai.Client(
    api_key="testbed",
    http_options=types.HttpOptions(base_url=model["base_url"], api_version="v1beta"),
)
response = client.models.generate_content(
    model=model["request_model"],
    contents="Return 42",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    ),
)
```

The same client setup works for both Gemini API and Vertex routes: the gateway
supplies the real key or bearer token and the approved Vertex project path.
The SDK stays in API-key mode with the placeholder; the harness does not run ADC
or receive project credentials. Execute local tools in the harness and replay the
returned native content, including thought signatures, with its function results.
Native JSON and fragmented SSE tool rounds are tested with `google-genai==3.6.1`.
See the [SDK configuration](https://googleapis.github.io/python-genai/) and
[Google API reference](https://ai.google.dev/api/generate-content).

#### Installed Google routes

`dungeness providers --details` lists both routes and their required inputs:

| `provider` | Service | Private launcher inputs |
| --- | --- | --- |
| `google` | Gemini API, `generativelanguage.googleapis.com` | `TESTBED_GEMINI_API_KEY` |
| `google-vertex` | Vertex AI, `aiplatform.googleapis.com`, global location | `TESTBED_VERTEX_ACCESS_TOKEN`, `TESTBED_VERTEX_ACCESS_TOKEN_EXPIRES_AT`, `TESTBED_VERTEX_PROJECT_ID` |

Both routes include `gemini-4-carbon`, `gemini-4-neon`, `gemini-4-argon` and
`gemini-4-hydrogen`, with pinned OpenRouter reference rates. For example:

```yaml
model_access:
  models:
    - provider: google-vertex
      upstream_id: google/gemini-4-carbon
      request_model: gemini-4-carbon
      api: google-genai
      name_format: request
```

The compiler supplies `api: google-genai` and the harness base URL
`http://gateway:8080/model/google-vertex`. The SDK appends
`/v1beta/models/{model}:generateContent` or `:streamGenerateContent?alt=sse`.
Use `google` for the Gemini API route. Real credentials stay in private gateway
staging. The routes do not fall back to each other.

For Vertex, sign in on the host using `gcloud auth application-default login`.
The trusted launcher obtains a Cloud-scoped access token from that login and
supplies its actual expiry as an ISO 8601 timestamp. Select the Cloud project
explicitly; it needs billing, the Vertex API enabled, and permission to call the
model. No API is enabled or billing changed by Dungeness. Refresh tokens stay
on the host. Renewal during a run is not implemented; use a fresh token and a
run duration that fits its remaining validity.

The registry's `project_header` reads the project only from the gateway's
trusted authentication recipe. A validated project ID or number is inserted
into `/projects/{project}/locations/global/publishers/google` beneath the fixed
Vertex base URL. Neither a harness header nor a supplied URL can choose the
destination. Other regions require a separately reviewed route.

These are API-billed routes, not Google AI Ultra browser or Antigravity
subscription allowances. Account/model availability is determined by Google.
For setup details, see [Vertex authentication](https://cloud.google.com/vertex-ai/generative-ai/docs/start/gcp-auth)
and [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key).

Google subscription access is not supported. Use the API credentials listed above.

The native `usageMetadata` receipt supplies input, cached, output and thinking
token counts. Output accounting includes `candidatesTokenCount + thoughtsTokenCount`;
repeated streaming counters are cumulative, not additive. Missing or invalid
final receipts block further model admissions. OpenRouter supplies the pinned
**reference prices**; requests go directly to the selected Google API endpoint.

Only text, thinking, structured JSON and locally executed function calls are
supported. Hosted tools, remote cached content, file/media inputs and unreviewed
operations are rejected. Native camelCase and snake_case field names are accepted
without rewriting them; duplicate aliases are rejected. The gateway can insert
an omitted output allowance for budget enforcement. Explicit allowances are
honored or rejected, never silently reduced.

Check a native request offline (the model is in the URL, not the JSON body):

```sh
python tools/validate-model-request.py --provider google --model gemini-4-carbon \
  --operation generateContent --request request.json
```

The runtime advertises `google-native-protocol-v1`. Earlier experimental Google
Chat Completions configurations must switch to `api: google-genai` and a native
client; the translation endpoint is removed. OpenAI and Anthropic interfaces are
unchanged. Attested users need a rebuilt, approved runtime before selecting this
protocol; a source update does not publish or approve a VM.
