# Gateway request policy

The gateway accepts a reviewed subset of provider APIs. Every inference route
validates requests **before provider traffic or budget
reservation**. This applies to command harnesses, legacy named agents, and runs
without `model_access`. It does not depend on the harness obeying its own settings.

The submitted container has no direct internet route. Only the trusted gateway
has provider credentials and external network access in command-harness runs.
The gateway source, container environment, pricing catalog and operator credentials
must remain outside the submitted agent's control.

## Arbitrary harnesses, explicit access

`dungeness-command-v1` accepts arbitrary installed programs, SDK loops, subprocesses
and multi-agent systems. A harness can implement its own prompts, local retrieval,
memory, tools and scheduling. It must route model traffic through the gateway and
use the supported inference protocols. Harness support does not grant arbitrary
provider API features.

The run setting:

```yaml
web_search:
  mode: disabled
```

sets the gateway's search and fetch budgets to zero. The historical
`web-search-profile:system/dungeness/disabled-v1` reference is an access-only alias
for that setting; it is not a harness template or research strategy. `optional`
permits the separately metered gateway web endpoints within the trusted task's
policy and budget. Neither setting permits provider-hosted search through a
model request. Client flags such as Codex `web_search=disabled` are additional
defenses, not the enforcement boundary.

## Supported model requests

The authoritative schemas are in
[`gateway_request_policy.py`](../services/gateway/gateway_request_policy.py).
They cover Responses (including ChatGPT compaction), Chat Completions, Anthropic
Messages and token counting, OpenRouter text completions, and OpenAI embeddings.
Moonshot and Kimi accept native Chat Completions only; the gateway does not
translate their requests or responses into another protocol.

- Unknown top-level fields and tool-envelope fields are rejected with HTTP 400.
  Unknown protocol beta headers and query controls are also rejected.
- Function tools, custom tools, recursively checked namespaces, local shell and
  patch tools, and the listed Anthropic client tools are supported. OpenAI shell
  requires `environment: {type: local}`. Tool discovery requires
  `execution: client`; discovered definitions receive the same recursive checks.
- Tool names are unrestricted. A local function named `web_search` can search
  bundled documents. Prompt text, JSON schemas and tool arguments are data; the
  policy does not scan them for forbidden words.
- Provider web search/fetch, MCP, file search, hosted shell/code execution,
  browser/computer tools and unreviewed tool types are rejected. So are plugins,
  model fallbacks/presets, `:online` model aliases and remote media references.
- Requests must send explicit history. Provider conversation IDs, previous
  response references and item references are rejected because their hidden
  state cannot be inspected. Local tool calls/results, reasoning and compaction
  history remain supported.
- The current content subset is text and local-tool data. Adding a provider
  feature or content type requires a trusted schema review, not an agent-side
  passthrough option. Pricing restrictions apply separately.
- Inference uses POST. The only accepted query marker is `beta=true` on Messages
  and token-counting routes. Model listings use GET, are served locally from the
  trusted pricing catalog, and are filtered by the run's model allowlist.
- Arbitrary request headers are not forwarded. OpenAI organization/project selection and
  opaque Codex routing/turn-state override headers are not forwarded either.

Optional SDK fields should be omitted when unused. A rejection names the
unsupported field or feature, so a harness author can remove it or request a
reviewed protocol extension. There is no agent-controlled switch to bypass this
policy.

## OpenRouter account defaults

OpenRouter can enable plugins at the account level. Its **Prevent overrides**
setting can force a plugin even when a request disables it
([provider documentation](https://openrouter.ai/docs/guides/features/plugins)).
Consequently a request filter alone cannot establish inference-only behavior
for an arbitrary OpenRouter account.

Before enabling OpenRouter, the operator must disable account-default server
tools/plugins, including enforced defaults, and keep that configuration in place.
Only then set this in the operator's environment file:

```dotenv
TESTBED_OPENROUTER_INFERENCE_ONLY=1
```

The compiler passes this assertion only to the trusted gateway as
`DUNGENESS_OPENROUTER_INFERENCE_ONLY`. Without it, OpenRouter inference is rejected
before any upstream request. Agents cannot set it in a request or run spec. The
gateway additionally injects `plugins: [{id: web, enabled: false}]`; agent-supplied
plugins are always rejected.

This flag is an operator assertion, not an automated audit of the remote account.
Use a direct provider route or leave OpenRouter disabled if that configuration
cannot be guaranteed. Gateway tests establish request-boundary enforcement; they
cannot attest to a provider's private server implementation.

## Verification

Run:

```sh
PYTHONPATH=services/gateway python -m unittest discover -s services/gateway/tests
python -m unittest discover -s tests
```

The boundary tests use mock providers. They exercise all registered inference
routes with and without model allowlists and with disabled/optional web budgets,
and assert that rejected requests cause no upstream calls or model charges.
Positive cases cover local Codex/Claude-style tool histories, SDK loops, both
Kimi protocols, compaction, token counting, embeddings and local model discovery.
