# Local operator guide

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
See [command harnesses](command-harness.md). This is the only execution
interface. Solvers may package any coding agent, including Codex or Claude Code,
inside their submitted image; Dungeness does not install or configure it.

This guide is for a standalone operator using a source checkout. OpenRSI users
should follow their platform's setup and submission instructions: the platform
installs trusted problem inputs, selects its runtime pin and controls publication.
Local Dungeness runs do not create official scores or attestation receipts.

## Quick start for operators

Prerequisites: Git, uv, uvx, Docker and access to the pinned task source. Linux
is required for Harbor's clean no-network verification. macOS supports development
and agent/sidecar runs, but does not establish equivalent final verification.
The assigned task declares its agent and verifier resource requirements.

### 1. Configure your workspace and model access

```sh
./dungeness setup
./dungeness init --namespace users/alice
```

Choose your own namespace. `setup` checks required tools and creates `.env`
from the example if needed; it does not install Docker or log in to a provider.
Inspect the routes and required inputs supported by this checkout:

```sh
./dungeness capabilities
./dungeness providers --details
```

Configure only the selected route's inputs in the private `.env`, for example
`TESTBED_OPENAI_API_KEY`. ChatGPT uses `DUNGENESS_CODEX_AUTH_FILE`, pointing to a
private login document; Claude account access uses a token and its actual expiry.
The caller obtains and refreshes those credentials before the run. The launcher
stages only required fields for the gateway and removes its copies after teardown.
See [authentication](gateway-authentication.md) and [account access](local-subscriptions.md).
Never commit credentials or put them in the harness image.

**Model calls consume your API credits or subscription allowance.** A normalized
USD cap is an experimental comparison budget, not a guaranteed cash-billing
limit. Actual usage is retained, including any final-response overshoot.
Credentials stay outside committed inputs. API-backed providers use `.env`;
command harnesses receive gateway access rather than your upstream credentials.
All supported harnesses use this same credential boundary.

### 2. Prepare a committed run

Install a trusted challenge package containing its task, problem, checkpoint and
verifier into the corresponding record directories. Dungeness ships the runtime
and a command-agent example; challenge definitions belong to the challenge owner.
OpenRSI's public CLI prepares these inputs for its local and remote runs.

Write a run spec under `run-specs/users/alice/` selecting the installed task,
agent, checkpoint, model access and limits. See the
[run-spec reference](cli-reference.md). Install agent dependencies into its
image before execution; the research container cannot download them.

Commit the trusted inputs and run spec on your experiment branch:

```sh
git switch -c research/alice-run
git add tasks/ problems/ checkpoints/ verifiers/ scaffolds/ agents/ run-specs/
git commit -m "Configure trusted task and run inputs"
git status --short
```

Run from a clean checkout so provenance includes an exact source revision.
Keep unrelated changes separate from experiment inputs.

### 3. Run and inspect

The following command starts model usage under the limits you selected:

```sh
./dungeness run run-specs/users/alice/run.yaml
./dungeness runs run-specs/users/alice/run.yaml
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
| `dungeness`, [`src/`](../src/README.md) | CLI, compiler, records and execution lifecycle |
| `adapters/`, `services/`, `policies/` | Trusted execution, metering and isolation |
| `agents/projects/dungeness/` | Generic command-agent example |
| `tasks/`, `run-specs/` | Operator-installed task definitions and run inputs |
| `verifiers/`, `checkpoints/`, `problems/`, `scaffolds/` | Trusted challenge assets installed by the caller |
| `tools/transcripts/` | Optional local transcript viewer; excluded from default runtime bundles |
| `runs/` | Generated local output; not committed |

The [runtime exporter](runtime-distribution.md) creates a reproducible source
bundle without personal experiments or run output. New user-authored inputs
and run outputs belong in local or service storage. See [migration notes](migration.md)
for retired interfaces and upgrading existing pins.

Each top-level directory has a short README describing its ownership and entry points.

## Documentation and checks

- [Bring your own command harness](command-harness.md)
- [Gateway authentication](gateway-authentication.md)
- [CLI reference](cli-reference.md)
- [Runtime distribution and artifact retention](runtime-distribution.md)
- [Record and configuration model](../DESIGN.md)
- [Gateway architecture](../services/DESIGN.md)
- [Runtime compatibility contract](runtime-contract.md)
- [Development and component boundaries](development.md)

Offline regression checks from a full source checkout use locked dependencies:

```sh
make check
```

The gateway and Harbor use separate dependency environments. These checks do not
launch paid model runs or establish Docker/provider compatibility.

## Compatible provider profiles

The gateway records HTTP 400 JSON `invalid_request_error` responses as zero-token
receipts and releases their credit reservations. Rejected requests still count
toward the request limit. HTTP 422 responses, ambiguous errors, and successful
responses without usage remain accounting failures and block subsequent model
calls. No provider-name exception infers free usage from a plain-text error.

[`services/gateway/model-access.json`](../services/gateway/model-access.json) defines
the standard routes;
`services/gateway/providers.json` is an empty extension registry by default.
Operators can add reviewed profiles for compatible upstreams before compiling a
run and building its gateway image. Profiles define the fixed HTTPS endpoint,
protocol routes, credential injection and reference model mappings; the gateway
implements the shared protocol and accounting. Credentials stay outside source
and reach only the gateway. The submitted harness receives a placeholder.

Profiles and pricing are trusted operator inputs, never accepted from the
harness or its run request. The checkout includes reference pricing in
`services/gateway/pricing.yaml`. An enclosing platform may install its own pinned
schedule; the exact schedule and registry used for the run must be retained. Tests use synthetic providers under `.invalid`
domains to check routing, authentication, expiry and usage accounting without
provider accounts or live inference.
