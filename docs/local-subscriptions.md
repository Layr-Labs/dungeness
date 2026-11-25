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

A run can select an approved endpoint, authentication method and model without
specifying a route name. The pair resolves to the existing registered route and
its credential requirements. See [per-run access selection](integrating-model-access.md#choosing-an-endpoint-and-authentication-for-a-run).
Google access uses the separate `google` (Gemini API key) and `google-vertex`
(Cloud OAuth) routes. Both use API billing; Google subscription access is not
supported. See [Google API setup](integrating-model-access.md#installed-google-routes).

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
