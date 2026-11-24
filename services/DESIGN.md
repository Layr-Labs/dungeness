# Gateway architecture

The gateway mediates model access for one run. It applies the trusted access-route
registry, authenticates upstream requests, enforces request and usage policy, and
records accounting. The harness controls its agent loop and local tools.

## Request path

```text
Trusted launcher
  selected credentials -> private per-run files -> gateway only

Harness -> gateway -> fixed model service
   |          |
   |          +-> assigned problem service
   |
   +-> optional evaluation sidecar

Frozen candidate -> trusted final evaluator
```

The harness receives assigned gateway URLs and a placeholder credential. It
cannot select an arbitrary destination or borrow another route's credentials.
External web search and fetch are disabled; their compatibility endpoints return
HTTP 410. Assigned task documents and pinned attachments remain available.

The gateway is a runtime component, not a credential store, login service or
harness framework. Dungeness does not refresh accounts or retry inference on the
harness's behalf.

## Ownership

| Component | Responsibility |
| --- | --- |
| Trusted caller | Select the problem, harness, models, access routes, prices, credentials and limits. |
| Compiler | Validate inputs and render the task, service topology, mounts and model allowlist. |
| Credential resolver | Stage selected secrets privately; retain them until the containers stop. |
| Execution adapter | Start the run, handle interruption, finalize records and clean up. |
| Gateway | Authenticate and validate model requests, meter usage, serve assigned resources and record events. |
| Harness | Implement the research loop, model client, tools, request recovery and candidate selection. |
| Problem/evaluator | Define the task, candidate format, validity and scoring. |

See [model-access terminology](../docs/model-access.md) and
[integration instructions](../docs/integrating-model-access.md).

## Network and filesystem boundary

The agent joins only its run's isolated internal bridge. The gateway also joins
the external-egress network and, when present, the private problem-service network.
There are no published host ports or shared project network names. The development
scorer is available on the agent's internal network; final evaluation uses a
separate no-network environment where supported.

The gateway's multiple interfaces do not enable kernel forwarding. It runs with
a read-only root, dropped capabilities and `no-new-privileges`. Only its usage
directory and bounded temporary storage are writable. Its private credential
files and internal accounting token are absent from the harness's mounts.

These controls do not protect against a compromised host, Docker administrator,
gateway or provider. See [network isolation](../docs/network-isolation.md) for the
exact topology and platform requirements, and
[credential boundaries](../docs/gateway-authentication.md#credential-non-disclosure-and-container-boundary)
for permissions and cleanup.

## Access routes and authentication

[`gateway/model-access.json`](gateway/model-access.json) holds endpoints,
operations and authentication recipes. `gateway/model_access.py` loads that
validated configuration. Older operator `gateway/providers.json` files are optional
compatibility inputs, translated into the same registry with conflicts rejected.
The compiler, credential resolver and HTTP handler use this single registry.
Each definition supplies its fixed upstream URL, supported operations,
authentication recipe and usage interpretation.

The public configuration field remains `provider` for compatibility. For example,
`openai` identifies API-key access and `openai-chatgpt` identifies ChatGPT Codex
account access; neither selects a harness.

`dungeness providers --details` describes these inputs without reading credentials.
The launcher's `dungeness.credential_access.prepare_credentials` stages only the
selected values and recipe-required JSON fields. It returns private paths, not
secret values. The gateway applies headers and checks any recipe-declared expiry
before request admission.

Destinations cannot be changed through run environment variables. Existing
`*_UPSTREAM_BASE_URL` inputs must agree with the registry. Tests substitute a
synthetic destination in trusted fixture code before starting the gateway; there
is no production switch that permits arbitrary upstream URLs.

## Protocol and policy

The gateway exposes the supported subset of each route's protocol. It does not
translate an arbitrary SDK's requests into a different protocol. Harnesses read
the model's `api`, `request_model` and `base_url` from their task document and
configure their clients accordingly.

Validation rejects unsupported fields, undeclared models, hosted tools and
unaccountable operations before upstream traffic. Supported local-tool and
reasoning history must remain intact. Account entitlement is decided upstream;
local model discovery does not test credentials or guarantee access.

Request bounds, OpenRouter account configuration, streaming semantics and
recoverable errors are specified in the
[request policy](../docs/gateway-request-policy.md). Harness authors should start
with the [recovery table](../docs/command-harness.md#required-request-error-handling).

## Accounting and results

The gateway records model admissions, complete exchanges, usage and failures in
`usage/events.jsonl`. Trusted evaluator events share the canonical stream and
include their cumulative usage snapshot. `usage/summary.json` is an atomically
refreshed cache, not a substitute for the underlying evidence.

Usage is priced against the run's trusted snapshot. Normalized comparison cost
is distinct from provider-reported cash charges. Subscription routes do not
invent per-token subscription bills. Reservations constrain admission, but
in-flight requests can exceed a soft cap.

The gateway drains admitted upstream responses after client disconnects to
recover final usage. Missing or ambiguous accounting blocks further admissions;
it is never assumed to mean a free call. The harness must preserve candidates
and handle stop, retry and correction instructions.

Provider errors and operational logs omit raw credential-bearing error bodies.
Response and trace filtering redacts known literal credential values, but is not
a general proof against transformed secret disclosure. Run traces can contain
prompts, source, tool output and responses; store them accordingly.

Dungeness records execution evidence. Acceptance, attestation, result sealing,
publication and leaderboard policy belong to the enclosing platform.

## Implementation map

| Module | Responsibility |
| --- | --- |
| `gateway.py` | Stable HTTP entrypoint, middleware, routes and lifecycle. |
| `model-access.json` | Maintained endpoints, operations and authentication recipes. |
| `access_config.py`, `model_access.py`, `provider_profiles.py` | Configuration validation, shared interface and legacy profile loading. |
| `gateway_auth.py` | Private credential reads and authentication recipes. |
| `gateway_models.py` | Protocol/model mapping, response interpretation and usage extraction. |
| `gateway_request_policy.py`, `gateway_reservations.py` | Request validation and admission estimates. |
| `gateway_runtime.py` | Per-run request orchestration and response draining. |
| `gateway_usage.py`, `gateway_pricing.py` | Ledger, events, limits and reference pricing. |
| `gateway_errors.py`, `gateway_history_diagnostics.py` | Recovery decisions and safe structural diagnostics. |
| `gateway_security.py` | Bounded I/O, redaction and credential-safe responses. |
| `gateway_web.py` | Compatibility helpers for historical web records; no outbound web implementation. |

The implementation modules do not import `gateway.py`. Historical exports remain
available there for callers, but new integrations should use the documented
file/CLI contract or credential-preparation interface.

## Validation

- `make check`: offline behavior and the separate pinned Harbor SDK contract.
- `python3 script/check-gateway-isolation.py`: synthetic inference, authentication, accounting,
  credential redaction, private mounts and container hardening.
- `make check-run-isolation`: two simultaneous run topologies, own-run operation,
  host/other-run denial and IPv4/IPv6 isolation.

Docker tests require a compatible local engine and use no real model account.
See [development](../docs/development.md) and
[runtime upgrades](../docs/migration.md) for consumer validation and the limits
of a local smoke test.
