# Google API access

`google-api` connects Dungeness's protected gateway directly to Google's
[OpenAI-compatible Gemini API](https://aistudio.google.com/docs/openai).
The arbitrary harness retains its own prompts, reasoning preferences, tools and
agent loop. Google subscription integration is on hold; this route uses an API
key and the API project's billing.

## Configuration

Put `TESTBED_GEMINI_API_KEY` in the private env file passed to `dungeness run
--env-file`. The launcher stages it as `GEMINI_API_KEY` in the gateway's private
credential file. Only the gateway gets the real key; the harness receives
`OPENAI_API_KEY=testbed` and its gateway base URL.

Choose a model in the trusted run specification:

```yaml
model_access:
  models:
    - provider: google-api
      upstream_id: google/gemini-4-carbon
      request_model: gemini-4-carbon
      api: openai-chat-completions
      name_format: request
```

This is a model-access fragment, not a complete run specification. Supported
request models are `gemini-4-carbon`, `gemini-4-neon`, `gemini-4-argon`,
`gemini-4-hydrogen`, and `gemini-3.8-flash`. Model availability and quota are
determined by the API project.

The harness sends `POST /model/google-api/v1/chat/completions` to the gateway.
For example, an OpenAI-compatible Python client inside the harness can use:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
)
response = client.chat.completions.create(
    model="gemini-4-carbon",
    messages=[{"role": "user", "content": "Explain this function."}],
    reasoning_effort="high",
    max_tokens=1024,
)
```

The fixed upstream is
`https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`.
OpenRouter is only a reference-price source. No subscription credentials,
Antigravity processes or prompt identity rewrites participate.

## Protocol and accounting

The first route supports text Chat Completions, streaming and harness-executed
function tools. It does not translate Responses, Anthropic Messages or native
Gemini `generateContent` requests. A harness must support this wire protocol.

Gemini tool calls can carry `extra_content.google.thought_signature`. Keep this
metadata attached when replaying assistant messages and tool calls; dropping it
can make the next turn fail. Dungeness validates this narrow metadata envelope
and forwards it unchanged. For bounded admission, opaque signed history reserves
all remaining budget exclusively because its token size cannot be bounded from
ciphertext. It does not manufacture signatures or rewrite prompts.
Google's [signature guidance](https://aistudio.google.com/docs/thought-signatures?generate-content=true#openai)
explains why history must preserve the provider's returned state.

The gateway requests streaming usage and requires a completed SSE stream plus
integer prompt, completion and total counters. Gemini compatibility responses
can exclude thinking from `completion_tokens`; for this text/function-only
route, total minus prompt supplies the full output bucket. Explicit reasoning
counts are checked against either the additive or inclusive completion format,
so reasoning is priced once. Missing or inconsistent counters stop further
admission rather than treating the request as free.

Reference prices are pinned in `services/gateway/pricing.yaml` from the
[2026-11-19 catalog snapshot](examples/google-api-pricing-20261119.json).
Reported cache reads receive their reference discount. When Google omits cache
details, the reference calculation grants no cache discount; it can therefore
overstate input cost. This is not a Google invoice. `billed_usd` remains unknown,
and credits, free quotas, tax and billing discounts are not inferred.

Hosted search, code execution, remote content, explicit cached-content references
and arbitrary `extra_body` controls remain outside this route. They would need
separate request-policy and accounting support.

## Qualification

Offline tests exercise all five installed model mappings through the actual
gateway, private-key substitution, unchanged prompts, a tool-result round trip,
split SSE transport, thinking/cache accounting, model restrictions and
missing-usage lockout. No real API key or paid request is used.

Live account/model validation and any manager or attested VM rollout are separate
qualification steps. This Dungeness change does not activate the earlier
subscription dropdowns or publish a rebuilt VM.
