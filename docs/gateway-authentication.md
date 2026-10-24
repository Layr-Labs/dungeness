# Gateway authentication

The harness sends inference in a supported wire protocol using its assigned
gateway URL and a placeholder credential. The gateway authenticates the upstream
connection using operator-owned configuration. Authentication does not translate
the request or choose research settings.

## LLM access routes

The gateway ships four access routes. A route identifies an upstream endpoint
and authentication recipe, not a model or a blanket permission to use an account.

| Route | Access mechanism |
| --- | --- |
| `openai` | OpenAI API key |
| `openai-chatgpt` | Temporary ChatGPT account access token and account ID |
| `anthropic` | Anthropic API key |
| `openrouter` | OpenRouter API key; models from multiple vendors |

ChatGPT subscription access remains supported through `openai-chatgpt`.
Dedicated Kimi and Grok integrations have been removed; neither is a configured
access route. A Grok model accessed through OpenRouter uses the OpenRouter API
route and credential, not a Grok subscription credential.

The checked-in `services/gateway/providers.json` contains no additional routes.
Operators can add compatible routes through that trusted registry; harnesses
cannot register arbitrary upstream destinations. Each hosted command run is
restricted to its declared provider/model allowlist. The configuration field
remains named `provider` for compatibility.

## Authentication recipes

`services/gateway/gateway_auth.py` resolves authentication recipes. Recipes
specify headers whose values come from an environment variable, a field in a
credential JSON file, or a fixed value. An optional expiry source is checked
before request admission. The resolver has no provider-name branches and does
not use billing status to choose an authentication mechanism.

Built-in recipes live beside the provider destinations in `gateway_models.py`.
They preserve the existing environment names and credential-file mounts.
ChatGPT's recipe reads its access token and account ID from the staged file.
A missing, malformed, or incomplete credential file fails closed. Caller-supplied
bearer tokens are never used to authenticate upstream requests.

For compatible providers in `providers.json`, bearer substitution remains the
default. These optional fields configure different authentication headers:

```json
{
  "credential_env": "EXAMPLE_API_KEY",
  "credential_header": "x-api-key",
  "credential_prefix": "",
  "credential_headers": {
    "account-id": "EXAMPLE_API_KEY_ACCOUNT"
  }
}
```

This is a fragment of a complete trusted provider profile. Additional credential
variables must be namespaced under `credential_env` and must not collide with
other credentials or transport headers. Operators supply the corresponding
`TESTBED_EXAMPLE_API_KEY_ACCOUNT` variable; the compiler exposes it only to the
gateway, for a run that permits this provider. These fields are not a new
solver-controlled credential-grant format.

Session-token profiles require their existing `*_EXPIRES_AT` value. Credential
expiry does not trigger an API-key fallback or an automatic login/refresh.
Catalyst's local login readers remain responsible for extracting temporary
access from provider login files.

Trusted authentication headers override any allowed client metadata. Destinations
remain operator-controlled, redirects are not followed, and unknown providers
cannot borrow the default provider's credentials. The gateway does not log
resolved authentication values.

Usage parsing, pricing, allowed models, request restrictions, and budget
enforcement remain separate from authentication. Streaming requests still
request usage where required. The harness owns reasoning preferences.

## Credential non-disclosure and container boundary

The gateway has no credential-read, environment-dump or arbitrary-file endpoint.
It substitutes credentials only on fixed upstream routes. Hosted command runs
require an explicit nonempty provider/model allowlist; missing or malformed
configuration prevents startup. Existing local compatibility modes without that
requirement are not the hosted command configuration.

Provider HTTP errors return a fixed code, request ID, upstream status and
retryability instead of the provider's raw error message or headers. Successful
response bodies and retained response traces redact literal credential values,
including JSON-escaped and URL-escaped forms. Streaming filtering handles values
split across transport chunks. Credential-file values, including account metadata
and ID tokens, are included in this filter. Unknown usage still blocks further
model admission; redaction does not authorize a zero-cost receipt.

This is protection against accidental credential echo, not a proof against all
exfiltration. It cannot recognize every transformation, partial disclosure or
credential reconstructed across separate semantic messages. A compromised gateway
process or trusted upstream remains outside this guarantee. No submitted harness
should receive the gateway's credential mount or real-key environment variables.

Generated gateway containers use a read-only root, no Linux capabilities,
`no-new-privileges`, a 1 GiB memory limit, 128-process limit and two-CPU ceiling.
Only the usage volume is persistent and writable; `/tmp` is a bounded 128 MiB
tmpfs for task-file spooling. Credential files remain read-only. These settings
apply to the gateway, not the agent's writable workspace or evaluator containers.
The ChatGPT gateway retains the invoking UID/GID so its private 0600 credential
mount remains readable without granting extra capabilities.

Requests are limited to 32 MiB and 30 seconds to receive their body, with eight
active non-probe requests. Health, status and metrics accept at most 1 KiB bodies.
Provider responses are bounded at 64 MiB; the stream relay has bounded queue
entries and stops waiting on a stalled client after 30 seconds. Disconnected
clients do not suppress provider-usage collection. Oversized or interrupted
responses without usage leave accounting unknown, never assumed free.

Regression tests run in the normal offline suite. The additional Docker smoke
check uses synthetic credentials and a local mock provider, never real model
access:

```sh
python3 script/check-gateway-isolation.py  # add --sudo if Docker requires it
```

It verifies inference, usage records, credential redaction, read-only root and
credential mounts, temporary-file spooling, dropped capabilities and
`no-new-privileges`. CI runs this check on pushes and pull requests.

### Live integration evidence (2026-10-24)

Local run `local-8dd9cb86b0344bfb` exercised stock Codex with GPT-6 Astra/high
through the hardened gateway. Docker inspection confirmed the read-only root,
read-only credential mount, writable usage volume and temporary directory,
zero effective capabilities, and `NoNewPrivs=1`. Six model requests completed
with settled accounting. Further model admission returned 429 after exhaustion;
the harness exited and the separate final verifier accepted its retained circuit
(local score 22,711,406,592). All run containers were removed on completion.

The configured one-credit admission cap resulted in 1.721452 normalized credits
of settled usage, including in-flight overshoot. This check validates gateway
compatibility and isolation, not a strict one-dollar spending guarantee. A scan
of 119 retained output files found no literal credential values. This is local
test evidence, not an official remote result or proof of a production rollout.
