# Native Antigravity / Carbon integration

Status: subscription integration resumed on 2026-11-18; not enabled for
attested execution. API-key integration is outside this work.

## Supported integration surface

Google documents running its own `agy` CLI headlessly in scripts and CI, and
launching `agy acp` as an editor subprocess. ACP communicates over JSON-RPC on
standard input/output and reuses the CLI's cached sign-in. These interfaces
provide a route to investigate without reimplementing Google's private
subscription protocol or extracting OAuth tokens into Dungeness's generic
OpenAI-compatible provider registry.

- [Official headless interface](https://antigravity.google/docs/cli/headless/)
- [Official ACP interface](https://antigravity.google/docs/cli/acp/)
- [Installation and authentication](https://antigravity.google/docs/install?tab=cli)
- [Model availability](https://antigravity.google/docs/models/)

Carbon's CLI selections are `gemini-4-carbon-low`, `gemini-4-carbon-medium` and
`gemini-4-carbon-high`. Google lists Carbon for Ultra and Enterprise accounts.
The Orchestrator selection is a different configuration that mixes models.
The original account exposed Gemini 3.8 Flash but no Carbon. A second, Ultra
account exposes Carbon at low, medium and high effort. After completing Google's
account-verification step, that account passed a text-only Carbon Low test.

Google's [additional terms](https://antigravity.google/terms) explicitly restrict
third-party service access, including reuse of Antigravity OAuth with other
software. That restriction must not be described as a prohibition on all CLI
automation: Google separately documents headless and ACP use. Those documents
also do not establish permission for arbitrary subscription proxies,
redistribution, or every proposed embedding.

Google's current [FAQ](https://antigravity.google/docs/faq) is more explicit:
headless mode is intended for direct scripting and CI, while wrapping `agy`
inside third-party coding agents or applications is unsupported under consumer
plans. The proposed OpenRSI embedding needs a provider-supported arrangement
before rollout. A successful direct CLI test does not establish that arrangement.
This is separate from the account-verification error observed during sign-in;
we have no evidence that the proposed integration caused that error.

## What the real binary established

The [offline probe](../tools/antigravity-probe/README.md) runs the official,
checksum-verified Linux ARM64 CLI 1.5.11 with synthetic responses. No account or
paid call is involved.

1. The binary runs in the current ARM64 gateway image.
2. ACP initialization succeeds and advertises OAuth and API-key auth methods.
   This is a handshake, not a tested login.
3. A custom agent can expose an MCP execution tool and omit native shell/file
   tools. An injected undeclared shell call is rejected.
4. A completed MCP tool call produces two Carbon requests and one Flash Lite
   review request. The final usage includes only the two Carbon requests.
   Default permission mode also omits review usage. Native transcript JSONL
   observed in a separate probe likewise contained the planner usage only.
5. A CLI `SUCCESS` result alone does not prove the task completed: default
   headless permissions can decline the tool and still return success.

The [resumed probe report](../tools/antigravity-probe/observed-1.5.11-resumed.json)
checks three additional documented integration paths:

- Explicitly allowing only `mcp(openrsi/research_exec)` still produces the
  unreported Flash Lite review call.
- Eager MCP loading completes the tool with the correct declared argument
  schema, but also produces that unreported review call.
- `PreInvocation` and `PostInvocation` hooks each observe the two Carbon
  invocations. Neither observes the third, reviewer invocation, and their
  payloads contain no usage counts.

Tool execution is now confirmed by a separate journal written by the fixed-output
MCP fixture. Native step states and final success are insufficient evidence.
The fixture never executes its supplied command. The seven-case probe completes
and intentionally exits 2 because complete usage accounting fails.

The missing helper usage is a measured compatibility gap for Dungeness's
complete normalized-cost accounting. It is not a claim about actual charges
to Google's subscription balance, and it does not prove that the OAuth
transport behaves identically to the API transport used by the probe.

## Intended execution boundary

Keep the official CLI, sign-in state and accounting in a protected runner.
Expose a narrow MCP/ACP tool bridge to Dungeness's isolated research container.
Harness source and generated commands must not execute in the credential-bearing
process or mount its home directory. Trusted configuration must not load hooks,
plugins or MCP servers from the harness's writable workspace.

This is a native Antigravity agent integration, not simply another model name
for arbitrary OpenAI-compatible harness clients.

Before enabling it:

| Component | Required change |
| --- | --- |
| Dungeness | Native CLI lifecycle and tool bridge; complete trusted usage source; budget admission/cancellation; credential isolation and hostile-workspace tests |
| VM | Pin the qualified CLI and runner; enforce known provider egress; provision official sign-in securely; retain sealed result export; qualify and publish the new image |
| Manager | Distinguish native agent selection from a generic model route; show account/setup status; select Carbon effort; enable only with a compatible runtime |
| Verifier policy | Approve the measured runtime and explicit provider/agent configuration after qualification |

A usage fix must include helper and retry calls and identify their actual models.
Multiplying Carbon usage by a guessed overhead factor, treating missing usage as
zero, or calling a partial final report “settled” would not solve the gap.
Parsing undocumented local database internals is not currently a qualified
replacement. A native complete-usage interface or separately verified metering
path needs to be established first.

The current VM and manager therefore remain unchanged. Rebuilding the VM now
would only ship an unqualified binary; it would not make Carbon usable safely.

## Subscription test checkpoint

On 2026-11-18, the official Mac ARM64 CLI 1.5.11 successfully reused its cached
subscription sign-in. `agy models` exposed Gemini 3.8 Flash but no Carbon.
A text-only `gemini-3.8-flash-low` prompt completed with `SUCCESS` and the
requested response. API-key environment variables were removed, and the CLI
used a fresh workspace with a custom agent exposing no native tools.

The [sanitized smoke-test receipt](../tools/antigravity-probe/observed-1.5.11-subscription.json)
records CLI-reported usage of 1,990 input tokens and 2 output tokens. This
establishes one working subscription inference call. It does not qualify MCP
execution, Carbon availability, complete usage accounting or attested execution.

The user then signed in to an Ultra account and completed Google's additional
account verification. The same text-only test with `gemini-4-carbon-low`
returned exactly `carbon subscription ready` (plus a newline), with exit 0 and
`SUCCESS`. The [Carbon receipt](../tools/antigravity-probe/observed-1.5.11-carbon-subscription.json)
records 1,996 input tokens and 7 output tokens, as reported by the CLI.
This establishes working Carbon subscription inference. It does not qualify
tool execution, complete accounting or attested execution.

For another account, complete `agy acp --login --disable-telemetry`
interactively, then use `agy models` to check actual entitlement. Enter
authorization codes only into the official CLI, not into a shared transcript.
Do not fall back to an API key when subscription authentication is unavailable.

This live check is needed because the offline probes exercise a synthetic API
transport; they do not establish identical behavior on Google's subscription
transport. Until a complete metering source is qualified, label any live test
usage as CLI-reported and do not submit it as a fully accounted attested run.

## Independent API option

Carbon also has a documented Gemini API route. A separately labeled API-key
provider can use Dungeness's metered gateway, but requires API billing and is not
Antigravity subscription access. Do not silently substitute it for “Carbon in
agy.” See [Gemini OpenAI compatibility](https://aistudio.google.com/docs/openai).
