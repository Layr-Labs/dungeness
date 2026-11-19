# Google subscription work — paused

Paused at the user's request on 2026-11-18. Preserve this work for resumption;
do not merge or enable Google execution as part of the Claude/GPT changes.

## Saved branches

- Dungeness: `feat/native-antigravity-carbon`, [draft PR #33](https://github.com/Layr-Labs/dungeness/pull/33).
  The latest executable test changes are in `14b44df`.
- Manager: `feat/native-antigravity-carbon`, commit
  [`d583f74`](https://github.com/Layr-Labs/openrsi-space-dev/commit/d583f74).
  This adds Google model choices and an authenticated, read-only subscription check.
- Enchantment: no Google execution or VM changes were implemented.

The local checkouts are under
`/Users/bxue/Documents/enchantment/local/carbon-native/`.
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

## Direction when resumed

The user explicitly wants subscription access, not a substitution with separately
billed API-key access. Use **OpenRouter reference prices** for normalized cost,
as in the platform's other subscription accounting. The public price snapshot
saved alongside the probes is research input; it has not been installed as a
trusted runtime pricing policy. Missing token usage must not become a zero cost.

Do not assume the complete Antigravity CLI must be the model backend. The
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
impossible, or the cause of earlier account-verification errors.

Sources:

- [Gemini CLI Code Assist client](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/code_assist/server.ts)
- [Antigravity authentication](https://antigravity.google/docs/install/)
- [Antigravity headless CLI](https://antigravity.google/docs/cli/headless/)
- [Antigravity FAQ](https://antigravity.google/docs/faq)
- [OpenRouter public model catalog](https://openrouter.ai/api/v1/models)

## Merged work outside this pause

GPT-6.1 Terra gateway support was merged in
[Dungeness PR #35](https://github.com/Layr-Labs/dungeness/pull/35),
merge commit `2480bde40f3ae2865d2ddd2328f03d60a0a8f120`.
That PR contains no Google changes. It adds gateway support, not a new manager
model entry or a rebuilt Mac VM.
