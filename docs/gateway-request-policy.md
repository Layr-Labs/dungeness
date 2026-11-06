# Gateway request policy

## Offline checks and output limits

OpenRSI enables bounded request reservations with a default maximum of **65,536
output tokens per request**, separately from the run's spending limit. Oversized
explicit limits are rejected before generation, not silently truncated. Claude
Code harnesses should set `CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000`. This is a gateway
policy, not the provider model's maximum output capacity.

Use the same field and reservation validator as the gateway without making calls:

```sh
python tools/validate-model-request.py --provider claude-subscription \
  --operation messages --request request.json \
  --pricing docs/examples/local-subscription-pricing-20261030.json
```

The JSON request must include the selected model. This checks body fields and
output limits and reports the conservative reservation. It does not validate
credentials, live balance, provider eligibility, transport headers or actual
upstream behavior. A strict mock can import `validate_generation` from
`services/gateway/gateway_reservations.py`. Rejected live requests emit a safe
`gateway.model_request_rejected` event without prompt or credential contents.

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
The gateway does not translate requests or responses into another protocol.

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

## Conversation history compatibility

History is validated for the configured provider and API operation, separately
from model, tool, routing and spending controls. OpenRouter Responses reasoning
items support `format` and `signature`; Chat Completions uses `reasoning_details`.
A format identifier is optional, inert metadata: when present it must be a
nonempty string of at most 128 characters, rather than one of a fixed list of
versions. The gateway preserves accepted history, including signatures,
encrypted content, item order and tool associations, without removing fields.
Requests are limited to 8 MiB and 64 levels of JSON nesting.

Unknown history structures fail explicitly with HTTP 400 and the diagnostic code
`conversation_history_rejected`. Safe diagnostics include the request ID, schema
version, location and item/field position where available, and whether the request
reached the provider. Arbitrary field names and history contents are not echoed.
Update to a compatible runtime or report the request ID; do not remove reasoning
or signatures to work around a rejection. Capability restrictions remain enforced.

Streaming is relayed unchanged. Clients must retain complete items delivered by
`response.output_item.done`, even when the final response has an empty `output`,
and must not treat unfinished items from an interrupted stream as complete.
A rejected continuation does not erase earlier accounting or candidates and does
not trigger an automatic provider retry or restart.

Unused optional control fields should be omitted. Unsupported controls require a
reviewed protocol extension; there is no agent-controlled policy bypass.

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
Positive cases cover local Codex/Claude-style tool histories, SDK loops, configured providers, compaction, token counting, embeddings and local model discovery.

## OpenRouter usage and charges

OpenRouter calls record provider-reported `billed_usd`, `billing_source` and
`upstream_request_id` alongside pinned-price `normalized_usd`. The same gateway
code runs locally and in hosted evaluations. Charges come from response
`usage.cost`, or a bounded HTTPS lookup of that exact generation when needed;
shared-key balance deltas are never used for attribution. Lookup credentials stay
inside the gateway, and the generation endpoint is not exposed to the harness.

A missing charge remains unknown and blocks further model admissions. Actual
charges and the existing normalized ceiling both constrain the run; in-flight
requests can still exceed a cap. Other provider routes keep their existing
accounting. Cost records are not proof that a solver-authored local trace is genuine.

### Bounded request admission

The trusted run-spec can enable `model_access.bounded_requests: true` and set
`model_access.max_output_tokens` (default 65,536). The compiler puts these only
in the gateway environment. Harness requests cannot change this policy.

With the guard enabled, text generation gets an explicit output-token limit
(up to 16,384 if omitted, reduced to fit available credits), and the ledger atomically reserves both token and
USD estimates across concurrent requests. Estimates use UTF-8 request bytes plus
framing allowance and the most expensive configured input/cache/output rates,
including a long-context tier only when the conservative input bound exceeds its threshold. Only one completion is permitted. Actual settled
provider usage remains authoritative; missing accounting blocks further calls.

This is deliberately conservative: large cached histories may be rejected even
when their eventual bill would be lower. It is not a universal tokenizer or a
provider-enforced cash guarantee. Opaque encrypted history is preserved, but its
request must wait for other calls and reserves the entire remaining allowance.
Ciphertext length is not treated as a token count. A single opaque-history call
can still exceed a soft limit; actual provider usage settles it. Provider-side
state references and operations without a supported output bound are rejected.
Explicit output limits are preserved or rejected, never silently reduced.
Sizing and admission use the same ledger lock. Rejections include a request ID,
code, available credits and required reservation, without the request content.
If the reservation exceeds all remaining credits even after active calls settle,
the gateway returns HTTP 400 with `retryable: false` and `x-should-retry: false`.
Shorten the context or lower the explicit output limit before trying again;
repeating the same request will not help. A reservation that could fit after
active calls settle still returns HTTP 429 with `retryable: true`.
Use ordinary generation routes. OpenRSI local and remote runs enable this same
policy; standalone Dungeness runs can select it in the run spec.

A provider-enforced, expiring per-run key is an additional financial boundary;
gateway estimates do not protect a key stolen from the gateway or host.

## Recovering from a rejected request

A rejected request does **not** automatically end the research run. The gateway
uses an explicit stop list in `gateway_errors.py`. Other errors leave the run
open. Read the recovery fields in `diagnostic` (request/admission errors) or
`error` (provider/transport-bound errors), rather than inferring recovery from
HTTP status alone. Existing error envelopes remain compatible.

| Case | `run_action` | `retryable` | Harness action |
| --- | --- | --- | --- |
| Invalid history, unsupported input or tool, unauthorized model, excessive output limit | `continue` | `false` | Correct the request, then continue the same run. |
| Request reservation exceeds remaining credits or tokens | `continue` | `false` | Reduce context or an explicit output limit; retain completed work. |
| Active requests temporarily reserve the needed allowance, or gateway capacity is full | `continue` | `true` | Wait for active calls to settle; retry with bounded backoff. |
| Connection/pool failure known to occur before dispatch | `continue` | `true` | Retry with bounded backoff. The failed attempt still counts toward the request limit. |
| Provider rate limit or transient failure with settled accounting | `continue` | `true` | Retry with bounded backoff. |
| Actual request/token/spend limit exhausted | `stop` | `false` | Stop inference; save and verify the best candidate. |
| Credentials unavailable, authentication/access denied, or required operator configuration missing | `stop` | `false` | Preserve work and report the safe error/request ID. |
| Unknown charges after dispatch, incomplete accounting, or cancellation | `stop` | `false` | Preserve work; inspect accounting/status. Do not start a paid replacement automatically. |
| Interrupted response with complete accounting | `continue` | `false` | Inspect the partial response; do not replay incomplete history or assume the operation completed. |

`error_schema_version: 1`, `category`, `action`, and `request_id` accompany these
fields. `category` is `run_stopping`, `retryable`, or `correctable`; `run_action`
is the simpler stop/continue decision. `x-should-retry: false` prevents supported
SDKs from blindly retrying permanent request errors. Unknown request errors
are nonfatal but **not** permission to resend an unchanged request. Bound all
retries by attempts and the run deadline. The gateway never retries inference
on the harness's behalf.

Current model input is text and supported local-tool history only. **Image,
audio and document input blocks are unsupported**, including locally rendered
PDF pages and inline images. Assigned PDFs can still be read locally: extract
text before constructing model requests. This is ordinary request validation,
not an image-specific stop rule. Nothing is silently removed from conversation
history; signed or encrypted reasoning must remain intact. If safe correction
is impossible, retain the candidate and return an actionable harness error.

A gateway response cannot force an SDK or subprocess to resume. Harness wrappers
must catch request failures and use this contract. Do not treat every HTTP 400
as a fatal research failure, and do not treat every HTTP 429 as retryable.
For streamed responses, HTTP 200 can precede a later interruption. Retained
`gateway.model_recovery_required` events record recovery guidance; clients must
also require a protocol completion event before considering history complete.
`upstream_request_sent: true` records dispatch, not proof of provider receipt;
`false` means a local rejection or a known pre-dispatch transport failure.

### Fast regression loop

Run offline gateway scenarios before a paid end-to-end test:

```sh
PYTHONPATH=services/gateway python -m unittest discover \
  -s services/gateway/tests -p 'test_error_recovery.py'
PYTHONPATH=services/gateway python -m unittest discover -s services/gateway/tests
```

The focused suite exercises failure → correction → successful continuation,
retained accounting/work, budget pressure versus exhaustion, provider errors,
transport uncertainty, and capability controls. All upstream calls are mocked.
The full suite additionally covers signed history round trips and interrupted
streams. Add each newly observed failure as an offline reproduction here before
running another research experiment.
