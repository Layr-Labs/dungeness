# Account and subscription access

A route selects how the gateway authenticates; an account determines entitlement
and upstream quota. A route appearing in `dungeness providers` does not establish
that your account can use every model, or that a hosted platform accepts that
route. Login and refresh belong to the trusted caller, outside the harness.

## Required inputs

Use `./dungeness providers --details` for the installed runtime's exact recipes.
These are the account routes bundled in this revision:

| Route (`provider`) | Private caller input | Protocol |
| --- | --- | --- |
| `openai-chatgpt` | `DUNGENESS_CODEX_AUTH_FILE`: private JSON with `tokens.access_token` and `tokens.account_id` | Responses and compaction |
| `claude-subscription` | `TESTBED_CLAUDE_ACCESS_TOKEN` and `TESTBED_CLAUDE_ACCESS_TOKEN_EXPIRES_AT` | Messages and token counting |

Use the actual expiry supplied by the login flow; do not invent a future expiry
to make a token pass validation. Expiry is checked only where the recipe declares
it. ChatGPT's recipe has no expiry field: the caller supplies valid access and
upstream authentication errors stop model access. No route silently refreshes,
chooses another account or falls back to an API key.

A run can explicitly choose a compatible authentication recipe at the same
approved endpoint. See [per-run access selection](integrating-model-access.md#choosing-an-endpoint-and-authentication-for-a-run).
This does not add a Google subscription login or a new gateway endpoint.

Google subscription access and Kimi Code are not registered in this revision.
Adding either requires a reviewed integration and separate account validation.

## Google integration status

Checked on 2026-11-25:

- `google` (Gemini API key) and `google-vertex` (Cloud OAuth) are registered with
  Carbon, Neon, Argon and Hydrogen reference prices. See
  [installed routes and inputs](integrating-model-access.md#installed-google-routes).
  They use API billing, not Ultra subscription quota.
- The gateway includes [Google protocol translation](integrating-model-access.md#google-protocol-translation)
  and native token accounting. Synthetic HTTP tests cover Gemini and Code Assist
  envelopes, signed multi-turn local calls, streaming, cache/thinking costs,
  unavailable usage, interrupted responses and rejection of hosted tools.
- One direct official Antigravity CLI subscription call to Carbon Low passed,
  with API-key/ADC inputs and tools disabled. The CLI reported 2,066 input and
  6 output tokens. This checks account access, not a Dungeness harness run.
- The registered Vertex Carbon route passed a native command-harness smoke:
  two live model calls, a local tool writing `42`, signed multi-turn history,
  streamed completion and provider token receipts ($0.000646 normalized cost).
  An earlier HTTP probe also verified request-limit rejection. These small tests
  do not qualify a full research run, Docker isolation or an attested VM release.
  Live Gemini API-key credentials and other registered Google models have not
  been tested here; their request, authentication and accounting tests use
  synthetic responses.
- Live subscription endpoint/authentication and a complete subscription
  harness run remain to be qualified. Google's documented OpenAI-compatible
  **API-key endpoint** is not a subscription endpoint. Token renewal is deferred.

The saved [subscription probes](https://github.com/Layr-Labs/dungeness/tree/feat/native-antigravity-carbon/tools/antigravity-probe)
also found an unreported reviewer call when testing the full Antigravity CLI
with a synthetic tool workflow. Do not treat that CLI's final usage as proven
complete metering, or turn missing usage into zero cost. The new gateway
translation sends direct model requests without that CLI. No Google subscription
route, manager option or VM release is enabled by this change.

### Comparison with nanocode

Reviewed the supplied
[revision `ef8a705`](https://github.com/nanocodexyz/nanocode/blob/ef8a70531bbda8f0295a5184c3d887bc9fd8e167/crates/backends/antigravity/README.md).
It implements Gemini wire requests, streaming, thought-signature history and
cache/answer/thinking counters. Its client retains the latest cumulative usage
snapshot rather than summing each chunk, which matches our accounting approach.
It also implements its own Antigravity-style harness tools and prompts.

That revision explicitly does **not** support Antigravity/Google AI subscription
sign-in; it supports API keys, Vertex AI credentials and a configured gateway.
We reuse our existing credential resolver and budget ledger, require complete
usage for continued inference, reject provider-hosted tools, and do not import
nanocode's automatic authentication discovery or inference retries. No nanocode
code or dependency is bundled.

## Google access-token lifetime

Checked against Google's documentation on 2026-11-24. Google documents a
[one-hour OAuth access-token lifetime](https://developers.google.com/google-ads/api/docs/oauth/credential-management#reuse_user_credentials_across_your_api_requests).
Its [OAuth token response](https://developers.google.com/identity/protocols/oauth2/web-server#exchange-authorization-code)
provides the actual remaining lifetime in `expires_in`; use that value rather
than assuming a fixed duration. This is OAuth guidance, not a confirmed
Antigravity-specific lifetime or a test of the user's account.

A fresh token does not establish two hours of uninterrupted access. Without
in-run refresh, check that remaining validity covers startup, the run and a
safety margin. Longer runs need renewal on the trusted side. The refresh token
is separate authorization material and must not enter the harness. This revision
does not implement Google login or live credential renewal.

## Credential boundary

The caller prepares the selected account's input. Newly compiled runs privately
stage the required token fields; ChatGPT refresh tokens and unrelated login
metadata are omitted. The original login file is unchanged. The staged files
are mounted read-only into the gateway and removed after container teardown.
See [authentication and file permissions](gateway-authentication.md).

The harness receives its assigned gateway URL and a placeholder credential. It
must not read login files or pass real credentials to the gateway. Its client
must implement the route's supported protocol and
[request recovery](command-harness.md#required-request-error-handling).
Provider-hosted tools, account APIs and arbitrary upstream destinations are not
available. These controls trust the host, Docker administrator and gateway.

For a manager or another trusted launcher, use the
[credential integration API](integrating-model-access.md). It performs no login,
network access or account discovery. Remote credential handling and any platform
approval rules are separate from this local runtime contract.

## Reference accounting

The bundled [pricing schedule](../services/gateway/pricing.yaml) defines supported
route/model combinations and their normalized comparison rates. A caller may
install another reviewed, pinned schedule. The actual schedule used must be
recorded with the run. A normalized dollar budget is not a subscription cash bill
or a guarantee about the provider's remaining allowance.

Synthetic tests cover protocol compatibility, expiry, no fallback, accounting
and credential exclusion. Live account validation and qualification of the
packaged runtime remain separate checks; synthetic success alone proves neither.
