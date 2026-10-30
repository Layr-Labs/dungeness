# Local subscription access

These routes are for runs on the subscriber's own machine. They do not enable
remote credential submission or establish eligibility for platform funding.
The harness uses the assigned gateway URL and `testbed`; the real credential
is mounted only into the trusted gateway. Refresh credentials are not staged.

| Provider | Model | Private local input |
| --- | --- | --- |
| `grok-subscription` | `grok-4.7` | `TESTBED_GROK_SUBSCRIPTION_TOKEN` and `TESTBED_GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT` |
| `minimax-subscription` | `MiniMax-M3.1-Flash`, `MiniMax-M3` | `TESTBED_MINIMAX_CODING_PLAN_KEY` |

Use your authorized Grok login or MiniMax plan key. A MiniMax API billing key
must not be labeled a subscription key: the upstream determines which balance
is consumed. Neither route reports a fabricated cash charge or remaining plan
allowance. Expired Grok access fails closed without refresh or API-key fallback.

Both routes accept only text Chat Completions and function tools. Hosted search,
account APIs and arbitrary upstream URLs remain unavailable. No Grok CLI identity
headers are added. A harness must pair its client's request format with this
route, including helper calls and tool results. Gemini CLI's subscription route
is not enabled: its native protocol and explicit third-party OAuth restriction
need a separate integration decision.

## Reference pricing

The frozen [2026-10-30 local schedule](examples/local-subscription-pricing-20261030.json)
records the public OpenRouter reference prices and original catalog fields.
Current OpenRSI clients bundle equivalent reference entries; `--pricing` is not
required for advertised models. This file is also available for direct Dungeness
experiments. Claude Code setup is documented in the
[OpenRSI recipe](https://github.com/Layr-Labs/openrsi-space/blob/main/docs/claude-subscription.md).
It does not change the historical default schedule or query live prices during
a run. Grok's higher rate above 200,000 input tokens is retained; hosted search
is disabled. A 500,000-token context window is a client configuration, not a
500,000-token run budget. Configure it in the harness and use the separate
normalized-credit cap for total usage.

## Provider references

Checked 2026-10-30:

- [Grok headless CLI](https://docs.x.ai/build/overview).
- [MiniMax OpenAI-compatible API](https://platform.minimax.io/docs/api-reference/text-openai-api).
- [MiniMax CLI and plan access](https://github.com/MiniMax-AI/minimax-code).
- [Gemini CLI access restrictions](https://geminicli.com/docs/resources/tos-privacy/).
- [Kimi subscription restrictions](https://www.kimi.com/en/help/kimi-code/community-guidelines).

Synthetic tests exercise the installed profiles, streaming accounting, expiry,
budget rejection and secret exclusion. A provider needs separate live validation;
passing these tests alone does not establish account entitlement.
