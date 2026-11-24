# Runtime upgrades and compatibility

An application normally pins a tested Dungeness revision. Updating a source
checkout, updating an application's pin, and deploying a packaged VM are separate
actions. A merge to Dungeness does not perform the latter two.

## Before updating a caller

1. Keep the current runtime and its existing runs available. Test a clean checkout
   of the candidate revision in a separate workspace.
2. Read `dungeness capabilities` and `dungeness providers --details`. Check the
   caller's required capabilities, route IDs, models and trusted pricing.
3. Run the caller's real compiler/adapter contract tests against that revision.
4. Exercise a complete local container run: credentials, the actual harness,
   model request/response handling, accounting, evaluation and cleanup. Use
   synthetic responses first, with a fixture-owned registry destination.
5. Qualify any deployment-specific packaging, hardware or attestation changes
   before changing the application's pin. Keep the prior pin for recovery.

Passing compilation does not establish container behavior. Passing a synthetic
run does not establish account entitlement, live-provider compatibility or
hosted acceptance. A Mac development run does not substitute for the enclosing
platform's Linux or attested-VM qualification.

The OpenRSI consumer contract command is in
[runtime compatibility](runtime-contract.md#verification). The runtime's own
checks are in [development](development.md).

## Credential-access changes

The existing `provider` field, route IDs, gateway URLs and private input names
are preserved. In documentation, use **access route**, not “connection,” for
the selected service and authentication method.

`dungeness providers --details` adds credential descriptions; `providers` without
that flag keeps its original JSON shape. The optional
`model-credential-inputs-v1` capability identifies the new preparation contract.

Newly compiled runs add `x-dungeness-credential-files` alongside the existing
`x-dungeness-credential-env` metadata. The launcher stages selected fields from
private login files instead of mounting the original document. Required source
files must be private regular JSON files with no symlink or extra hard link.
Original files are neither modified nor deleted. Old renders without file
metadata retain their old file mount; recompile to obtain managed snapshots.

Direct integrations keep the preparation context open until every container
using its mounts has stopped. See the
[launcher guide](integrating-model-access.md#integrating-a-trusted-launcher).

## Route configuration

Endpoints and authentication recipes now live in
[`services/gateway/model-access.json`](../services/gateway/model-access.json).
Package this file and its loader with the runtime; there is no embedded fallback
when it is absent or invalid. Existing `providers.json` extension profiles remain
supported. The default extension registry is empty.

## Fixed upstream destinations

The trusted registry determines each upstream. Legacy `*_UPSTREAM_BASE_URL`
settings are valid only when they name that registered destination. Remove
obsolete overrides before an upgrade; an alternate endpoint requires a reviewed
registry change.

Older smoke tests that redirect `OPENAI_UPSTREAM_BASE_URL` to a local mock must
be migrated. Use a disposable test runtime with a synthetic registry destination,
as the Docker checks do. Never re-enable arbitrary destinations in production
just to make an old test pass. Keep fixture changes out of release artifacts.

## Removed bundled routes

Grok and MiniMax access routes and reference prices have been removed, including
their OpenRouter model entries. Existing runs requiring them need their previous
runtime pin; this revision does not fall back to another model or account.
OpenAI API, ChatGPT, Anthropic API, Claude account access and OpenRouter remain.

## Retired interfaces

| Old input or behavior | Current replacement |
| --- | --- |
| Bundled Codex, Claude Code, Pi or Prime Agent launchers; native agent options | Package the agent in a Docker image and use `dungeness-command-v1`. |
| Dungeness login or OAuth-refresh proxy | Resolve an explicitly selected account in the trusted caller; stage temporary credentials for the gateway. |
| `research_state`, run-spec `evaluation` strategy profiles | Implement research state, evaluation cadence and completion decisions in the harness. |
| `initialization.knowledge_base` and host retrieval hooks | Bundle permitted files and retrieval tools in the harness; use the assigned problem service for task resources. |
| External search/fetch or `web_search.mode: optional` | External web is disabled. Legacy access-only aliases resolve to disabled; web endpoints return HTTP 410. |
| Schema-v1 scaffolds with problem-specific preparation | Use [declarative schema-v2 scaffolds](scaffolds.md). |
| World-map split evaluator | Supply a challenge-owned evaluator for the intended full task. |
| Direct Kimi Code/Moonshot routes | These route IDs remain retired. A different supported route needs its own account and explicit model selection. |

Rejection messages and historical record readers remain for compatibility.
Removing an old active feature does not authorize deleting earlier run artifacts.
Replay historical implementations at their original source revision.

## Documentation and tooling changes

The [documentation index](README.md) separates harness, operator and launcher
instructions. Gateway architecture describes the active implementation; retired
design sketches remain in Git history. Platform login, funding, submission and
Mac release instructions are owned by the platform's matching deployment.

The offline request checker now defaults to the bundled YAML reference schedule
and checks the route's supported operation. Existing explicit `--pricing` JSON
schedules remain supported. Runtime source exports now include the integration
guides and checker; no credentials, local notes or run outputs are added.
