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
| `grok-subscription` | `TESTBED_GROK_SUBSCRIPTION_TOKEN` and `TESTBED_GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT` | Text Chat Completions |
| `minimax-subscription` | `TESTBED_MINIMAX_CODING_PLAN_KEY` | Text Chat Completions |

Use the actual expiry supplied by the login flow; do not invent a future expiry
to make a token pass validation. Expiry is checked only where the recipe declares
it. ChatGPT's recipe has no expiry field: the caller supplies valid access and
upstream authentication errors stop model access. No route silently refreshes,
chooses another account or falls back to an API key.

A MiniMax billing key must not be relabeled as a plan key; upstream account
configuration determines which balance is consumed. Dungeness does not infer
remaining subscription allowance from the credential or route name.
Google subscription access and Kimi Code are not registered in this revision.
Adding either requires a reviewed integration and separate account validation.

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

The [2026-10-30 JSON snapshot](examples/local-subscription-pricing-20261030.json)
is retained for reproducing older experiments; it is not a live catalog or the
current default. Use the installed schedule when validating a new request.

Synthetic tests cover protocol compatibility, expiry, no fallback, accounting
and credential exclusion. Live account validation and qualification of the
packaged runtime remain separate checks; synthetic success alone proves neither.
