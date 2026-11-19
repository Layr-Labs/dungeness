# Google subscription work — resumed investigation

Resumed at the user's request on 2026-11-19. The target is a **drop-in
subscription model for arbitrary harnesses**, with authentication and metering
in Dungeness's protected gateway. The user briefly requested a separate API
route, then deprioritized it. No API provider was added.

**User decision, 2026-11-19:** do not use Antigravity CLI/ACP as a bridge.
It changes the harness architecture and conflicts with Google's stated
third-party embedding restrictions. The native bridge is rejected, not a
fallback to pursue. Keep the existing probes as historical evidence.

No working subscription adapter is qualified. Do not enable Google execution or
describe the investigation as a completed model integration.

## Latest findings

- Fresh discovery through the existing official CLI sign-in still exposes all
  five ordinary Google families: 17 model/effort combinations, plus three
  Orchestrator choices. The [new discovery receipt](../tools/antigravity-probe/observed-20261119-discovery.json)
  contains no inference tests or account identifiers.
- The official Linux ARM64 CLI **1.5.12** reproduces the missing-helper-usage
  result from 1.5.11 in all completed MCP variants. The
  [offline receipt](../tools/antigravity-probe/observed-1.5.12.json) comes from a
  network-isolated container with a synthetic endpoint and dummy key.
- The probe now also rejects mixed-model aggregate usage without a model
  breakdown. Correct total tokens alone cannot price Carbon and Flash Lite
  separately. The fixture's `expected_usage_by_model` is an independent
  expectation, not usage reported by the CLI.
- The official Gemini CLI source exposes a direct, structured Code Assist
  model transport. This makes it a technical lead, but does not establish
  Antigravity credential compatibility or Carbon entitlement. Google's current
  [Gemini CLI FAQ](https://geminicli.com/docs/faq/) explicitly excludes
  third-party reuse of its OAuth access. It is not a supported fallback.
- Antigravity's documented CLI/ACP surfaces run its agent. The SDK's
  [authentication instructions](https://antigravity.google/docs/install/)
  document API-key, enterprise and local-model paths, without establishing a
  consumer-subscription model endpoint for an arbitrary harness.

The concrete missing interface is a supported consumer-subscription model
transport that accepts caller-owned message/tool history and returns complete,
model-attributed usage. A native CLI agent bridge would change the requested
harness semantics and still has an unresolved accounting gap. Neither route is
enabled. This is not a claim that a private protocol is technically impossible.

The [transport assessment](native-antigravity.md#direct-model-transport-assessment)
records the inspected source revision and remaining checks. No new login,
credential extraction, live inference, VM release or manager activation was
performed during this resumption. A subsequent ACP capability/session check
reused the existing sign-in and exposed Carbon without sending a prompt. It
did not implement a bridge or qualify tool execution; the user then explicitly
rejected that direction.

## Saved branches

- Dungeness: `feat/native-antigravity-carbon`, [draft PR #33](https://github.com/Layr-Labs/dungeness/pull/33).
  The resumed branch includes current `main` through `ba38604`, the 1.5.12 probe
  and the stricter model-attribution check.
- Manager: `feat/native-antigravity-carbon`, commit
  [`d583f74`](https://github.com/Layr-Labs/openrsi-space-dev/commit/d583f74).
  This adds Google model choices and an authenticated, read-only subscription check.
- Enchantment: no Google execution or VM changes were implemented.

The original saved checkouts are under
`/Users/bxue/Documents/enchantment/local/carbon-native/`. Resumed Dungeness work
uses `/Users/bxue/.codex/worktrees/32d4/dungeness`; the original snapshots remain
unchanged.
`HANDOFF.md` there retains earlier investigation history.

## What works

The official Antigravity CLI 1.5.11 reuses the user's signed-in Ultra account.
Direct text-only tests passed for Carbon Low, Neon Low, Argon Low, Hydrogen Low
and Gemini 3.8 Flash Low. The sanitized receipts live in
`tools/antigravity-probe/observed-1.5.11-*.json`.

The manager displays those five model families, their effort choices, and a
subscription availability check. On the last check, the account exposed 17
model/effort combinations. The service invokes `agy models` only, strips
API-key/ADC environment variables, and returns no credentials or account IDs.
Ordinary dashboard polling reads cached status without launching the CLI.

These options say **Run integration pending** and are blocked for both local
and attested harness runs. They are not a functioning Google execution adapter.
Manager validation passed: 60 dashboard tests, three subscription tests and
nine JavaScript UI test scripts. Commit `d583f74` was pushed.

## What remains unresolved

The official CLI's completed MCP tool workflow made two Carbon calls and a
Flash Lite review call in the offline probe. Its final usage and invocation
hooks omitted the review call's usage. API-key transport was used only with a
synthetic, offline upstream in that probe; this does not prove identical
behavior for subscription transport. The live subscription tests were
text-only and did not qualify a harness, tool execution, or complete accounting.

No native execution adapter, direct subscription adapter, VM integration,
credential handoff, attested qualification or new VM release was completed.
Do not claim that adding the dropdown made Google runnable.

## Integration requirements

The user explicitly wants subscription access, not a substitution with separately
billed API-key access. Use **OpenRouter reference prices** for normalized cost,
as in the platform's other subscription accounting. The public price snapshot
saved alongside the probes is research input; it has not been installed as a
trusted runtime pricing policy. Missing token usage must not become a zero cost.

Do not use the complete Antigravity CLI as the model backend. The
existing GPT subscription adapter sends requests directly through the protected
gateway using the local Codex login, and meters provider response usage.
Investigate an analogous Google adapter first. Google's open-source Gemini CLI
has an authenticated Code Assist model client, but its compatibility with this
Antigravity account and Carbon has **not** been tested. Do not treat Gemini CLI
and Antigravity CLI credentials, scopes or model entitlements as interchangeable.

Keep provider authentication/transport separate from the harness, sandbox and
reference pricing. Establish accepted credentials, allowed endpoint/model,
streaming/tool-history semantics, token accounting and cancellation before
enabling the UI. Preserve credential isolation and sealed attested results.
The user has not approved unknown-cost runs or relaxing attested acceptance.

Google's consumer-plan restrictions on third-party access remain a separate
provider constraint. They are not evidence that a direct adapter is technically
impossible, or the cause of earlier account-verification errors. Resolving the
provider support question alone would not resolve the accounting or execution
requirements.

Sources:

- [Gemini CLI Code Assist client](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/code_assist/server.ts)
- [Antigravity authentication](https://antigravity.google/docs/install/)
- [Antigravity headless CLI](https://antigravity.google/docs/cli/headless/)
- [Antigravity FAQ](https://antigravity.google/docs/faq)
- [OpenRouter public model catalog](https://openrouter.ai/api/v1/models)

## Merged work outside this investigation

GPT-6.1 Terra gateway support was merged in
[Dungeness PR #35](https://github.com/Layr-Labs/dungeness/pull/35),
merge commit `2480bde40f3ae2865d2ddd2328f03d60a0a8f120`.
That PR contains no Google changes. It adds gateway support, not a new manager
model entry or a rebuilt Mac VM.
