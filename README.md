# Dungeness

Dungeness runs research agents under controlled conditions. It starts from a
pinned checkpoint, isolates the agent's network, meters declared model calls,
and independently verifies candidate solutions. A run retains its configuration,
usage events, intermediate scores and final artifacts.

**Any installed harness can run as a command.** Its source, knowledge and tools
live in its image. Dungeness does not provide a knowledge-base service or
choose how an agent retrieves or processes its own files.
Model access and trusted prices are configured separately.
Research strategy, memory, evaluation cadence and completion decisions belong to
the harness. The runtime does not inject research-state prompts or enforce
experimental search/evaluation quotas.
See [command harnesses](docs/command-harness.md). Existing Codex, Claude Code and
other maintained adapters remain supported.

The source is public and can be used for local development and controlled agent
runs. Catalyst solvers can also submit source and authorized temporary model
access directly to the remote service without installing Dungeness. Local runs
do not create official Catalyst scores or receipts.

## Quick start for operators

Prerequisites: Git, uv, uvx, Docker and access to the pinned task source. Linux
is required for Harbor's clean no-network verification. macOS supports development
and agent/sidecar runs, but does not establish equivalent final verification.
The starter uses up to 4 GiB for its agent and 8 GiB for its verifier, plus runtime
and build overhead.

### 1. Configure your workspace and model access

```sh
./dungeness setup
./dungeness init --namespace users/alice
```

Choose your own namespace. For the starter's ChatGPT subscription route, install
Codex and sign in locally:

```sh
./dungeness auth login codex
./dungeness auth status codex
```

**Model calls consume your API credits or subscription allowance.** A normalized
USD cap is an experimental comparison budget, not a guaranteed cash-billing
limit. Actual usage is retained, including any final-response overshoot.
Credentials stay outside committed inputs. API-backed providers use `.env`;
command harnesses receive gateway access rather than your upstream credentials.
Native subscription adapters have a different credential boundary; see the
[authentication reference](docs/cli-reference.md#auth).

### 2. Prepare a committed run

```sh
cp run-specs/projects/dungeness/ecdsa-starter.yaml run-specs/users/alice/ecdsa-starter.yaml
```

Edit this copy to choose your agent, provider/model, normalized spending cap,
token cap and time limit. The maintained starter uses Codex with GPT-6 Astra,
high effort, a $1 cap and no web access. Other providers and arbitrary harnesses
use the same metering/verification boundary. Agent-owned tools must be installed
before execution; the research container cannot download dependencies.

Commit the intended inputs before running, on your own experiment branch:

```sh
git switch -c research/alice-starter
git add run-specs/users/alice/ecdsa-starter.yaml
git commit -m "Configure ECDSA starter run"
git status --short
```

Run from a clean checkout so provenance includes an exact source revision.
Keep unrelated changes separate from experiment inputs.

### 3. Run and inspect

The following command starts model usage under the limits you selected:

```sh
./dungeness run run-specs/users/alice/ecdsa-starter.yaml
./dungeness runs run-specs/users/alice/ecdsa-starter.yaml
./dungeness evals RUN_ID
```

Harbor runs the clean verifier after the agent finishes. Inside the container,
`evaluate --json PATH` checks an intermediate candidate; the evaluator and gateway
record its score and cumulative usage independently of the harness's logs.

Outputs are created locally under `runs/<namespace>/<run-id>/`. They are ignored
by Git and excluded from runtime distributions. Keep them in local or service
artifact storage; commit run **inputs**, not traces. `verify`, continuation,
the optional transcript tools and cleanup commands still work on retained local outputs.

## Runtime and research material

| Location | Purpose |
| --- | --- |
| `dungeness`, `src/dungeness/` | CLI, run compiler and provenance |
| `adapters/`, `services/`, `policies/` | Trusted execution, metering and isolation |
| `agents/projects/dungeness/`, `tasks/projects/dungeness/` | Maintained adapters and starter task |
| `run-specs/projects/dungeness/` | Small maintained run examples |
| `verifiers/`, `checkpoints/`, `problems/` | Grading and pinned task identities |
| `tools/transcripts/` | Optional local transcript viewer; excluded from default runtime bundles |
| `doc/` | Implementation notes |
| `runs/` | Generated local output; not committed |

The [runtime exporter](docs/runtime-distribution.md) creates a reproducible source
bundle without personal experiments, knowledge bases or run output. Personal knowledge bases, run recipes, experiments and reports are archived
separately. New user-authored inputs and run outputs belong in local or service storage.
This repository starts from a reviewed source snapshot with fresh history.
Historical runs and reports are retained separately in the private research
archive.

## Documentation and checks

- [Bring your own command harness](docs/command-harness.md)
- [Gateway authentication](docs/gateway-authentication.md)
- [CLI reference](docs/cli-reference.md)
- [Runtime distribution and artifact retention](docs/runtime-distribution.md)
- [Record and configuration model](DESIGN.md)
- [Gateway architecture](services/DESIGN.md)
- [Implementation notes](doc/README.md) (full repository only)

No-model-call regression checks from a full source checkout, using a Python
environment with the gateway's pinned requirements installed:

```sh
python -m unittest discover -s tests
PYTHONPATH=services/gateway python -m unittest discover -s services/gateway/tests
python -m unittest discover -s tools/transcripts -p 'test_*.py'
```

Use an environment with Harbor 0.18.0 for the adapter API contract tests. These checks do not launch paid model runs or establish Docker
provider compatibility. Use an explicitly funded smoke run for that boundary.

## Compatible provider profiles

The gateway records recognized input rejections before generation as zero-token
receipts and releases their credit reservations. This includes HTTP 400 JSON
`invalid_request_error` responses and the Grok subscription proxy's HTTP 422
plain-text JSON-deserialization errors. Rejected requests still count toward the
request limit. Other 422 responses, ambiguous errors, and successful responses
without usage remain accounting failures and block subsequent model calls.

`services/gateway/providers.json` is trusted runtime configuration for fixed
OpenAI-compatible upstreams. It ships direct `xai` API-key access and
`grok-subscription` CLI session access, pinned to `grok-4.7`. Set
`TESTBED_XAI_API_KEY`, or `TESTBED_GROK_SUBSCRIPTION_TOKEN` together with
`TESTBED_GROK_SUBSCRIPTION_TOKEN_EXPIRES_AT`, outside source. The compiler mounts
these into the gateway only; command harnesses receive a placeholder.
Session expiry fails closed and does not fall back to an API key.
The Grok subscription profile sends no CLI identity, client-version,
authentication-response, or model-override headers. It uses the request body's
model and the gateway's own `User-Agent`. Live compatibility without those
headers remains unverified.

Profiles configure inference routes, fixed headers, model overrides and reference
catalog identity. Adding a compatible provider does not require a new HTTP route.
Do not accept profiles from agent input. Catalyst supplies its service-owned
registry and frozen pricing snapshot during preparation; standalone runs must
also provide trusted model pricing. Grok gateway tests use a mock upstream;
live subscription entitlement remains to be verified with an account.
