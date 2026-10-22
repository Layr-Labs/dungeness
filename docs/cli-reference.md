# Dungeness CLI reference

Start with [the runtime quick start](../README.md). Personal experiments, knowledge
bases and recorded outputs are archived separately from this repository. Examples
below show configurations you can author; they are not bundled historical runs.

![Dungeness Spit](../assets/dungeness-spit.jpeg)

*Dungeness Spit, the repository's namesake.*

Research-agent results are difficult to compare when agents start from
different source states, use different budgets, or have access to knowledge
published at different times. Dungeness makes those conditions explicit and
reproducible.

Each run starts an agent from an immutable public checkpoint, routes model and
web access through a metered gateway, limits which files can be submitted, and
grades the result with a clean verifier. Dungeness preserves the resolved
configuration, provenance, usage, metrics, and outputs as a canonical run
record.

This creates a durable history of research attempts that can be replayed,
compared, continued, and eventually searched without treating an execution
framework's generated files as the source of truth.

## Quick Start

Follow the [runtime quick start](../README.md#quick-start-for-operators).
Create a `dungeness-command-v1` descriptor and Dockerfile for your harness,
then select its model policy independently in `model_access` in the run spec.
The bundled `command` example only prints its task and makes no model calls.
Catalyst solvers normally use the public Catalyst CLI to build or submit a
`catalyst-exec-v1` harness; Catalyst creates this descriptor automatically.

Bundled Codex, Claude Code, Pi and Prime Agent launchers have been retired,
along with Dungeness's login command, native reasoning flags and refresh proxy.
Historical native-agent runs require their pinned older runtime. Their recorded
results remain readable. For new runs, install and configure your agent inside
the harness image, including any CLI flags or session-resume behavior.

### Commit before every run

A run must start from a clean, committed Dungeness worktree. Before launching:

1. Finish and validate every intended input, including the run spec, knowledge
   base, prompt profile, agent profile, policy, service code, and framework
   changes.
2. Commit those inputs to a dedicated branch.
3. Confirm that `git status --porcelain` prints nothing.
4. Launch the committed run spec from that exact checkout.

Do not leave the run spec uncommitted. There is no recursive dependency: the
run spec does not contain the Dungeness commit. At launch, Dungeness records
the current `HEAD` commit in `record.json`, together with the branch, dirty
state, tracked-diff fingerprint, and untracked-file hashes. The generated run
record and run ID are outputs and do not need to be included in the source
commit.

If unrelated user changes make the worktree dirty, do not fold them into the
experiment commit. Stop and ask the owner, or prepare the run from a dedicated
clean worktree. A dirty run is explicitly marked
`reproducible_from_commit: false`.

Harbor automatically runs the clean verifier after the agent finishes. The
manual `verify` command is only needed to rerun verification later.

`usage/events.jsonl` is the canonical chronological run event stream. Each line
has a schema version, source, event kind, run-local sequence number,
`observed_at`, `recorded_at`, and event-specific `data`. It interleaves:

- model requests, including the effective prompt and tool definitions;
- provider-visible reasoning summaries or `reasoning_content`;
- complete model response events, tool calls, and usage;
- web-search queries and returned results; and
- web-fetch URLs and returned contents;
- evaluator scores with the cumulative normalized USD at that point; and
- retained historical knowledge-base and research-state records, when present.

Trusted sidecars submit events to the gateway's authenticated internal
collector; the agent container cannot read the collector token. `summary.json`
is an atomically refreshed derived cache of current usage and evaluation state.

The event log never records authorization headers or provider credentials. It can
contain source code, tool output, prompts, and retrieved documents, so treat it
as a potentially sensitive run artifact. OpenAI does not expose raw hidden
chain-of-thought; OpenAI routes therefore record requested reasoning summaries
and token counts, while models such as Kimi can expose readable
`reasoning_content`.

## Command Line

Show available commands:

```bash
./dungeness --help
./dungeness <command> --help
```

### `capabilities`

```sh
./dungeness capabilities
```

Print the versioned runtime capability declaration as JSON without initializing
a workspace or contacting a model. Integrators can also read
`runtime-contract.json` directly. See the [compatibility contract](runtime-contract.md).

### `init`

Configure the default namespace for newly created user records:

```bash
./dungeness init --namespace users/bx
```

The configuration normally lives at
`~/.config/dungeness/config.toml`. Run namespace resolution is:

```text
--namespace
DUNGENESS_NAMESPACE
user configuration
otherwise: error
```

Use `DUNGENESS_CONFIG` to select a different user configuration file.

### `setup`

Check `uv`, `uvx`, and Docker, then create `.env` from `.env.example` when
needed:

```bash
./dungeness setup
```

### Model access

Use the [command model-access contract](command-harness.md) and
[gateway authentication configuration](gateway-authentication.md). Provider keys
are passed only to the gateway. Agent images receive a placeholder token and
allowed model URLs; they never receive native credentials or a refresh proxy.

### `run`

The preferred input is an authored run specification:

```bash
./dungeness run sample-starter.yaml
```

CLI options override values in the YAML:

```bash
./dungeness run sample-starter.yaml \
  --max-usd 2 \
  --label purpose=comparison
```

A run spec with `model_access` is required for command execution.

Common run options:

| Option | Meaning |
|---|---|
| `--namespace` | Namespace of the new run record |
| `--agent` | Override the selected research agent |
| `--checkpoint` | Override the public starting checkpoint |
| `--max-usd` | Model-spend cap |
| `--max-model-tokens` | Model-token cap |
| `--label KEY=VALUE` | Add searchable metadata; repeatable |
| `--fresh-start` | Blank the checkpoint candidate before starting |
| `--scaffold-start` | Start from the task's trusted reconstruction scaffold |
| `--resume-from RUN_ID` | Continue from a prior run's candidate |
| `--run-id` | Supply an explicit unique run ID |
| `--keep-render` | Retain the temporary Harbor task for debugging |
| `--keep-images` | Retain run-scoped Docker images after teardown |

Run specs provide defaults. CLI labels are applied after run-spec labels, so a
CLI label with the same key wins.

`initialization.mode: scaffold` is distinct from `blank`. A scaffold task
constructs a whitelisted workspace without Git history or the checkpoint
candidate, supplies its declared SDK files as read-only mounts outside the
editable path, and applies the same trusted files to evaluation. The
authoritative checkpoint remains in the run record for provenance but is not
copied into the agent workspace.

### `runs`

Find every canonical run produced from a run spec:

```bash
./dungeness runs sample-starter.yaml
```

The result includes status, reasoning effort, score, and run ID. Repeated and
interrupted attempts remain visible. Use `--latest` for the newest attempt or
`--json` for machine-readable output.

### `evals`

Read every canonical evaluation event recorded for a run:

```bash
./dungeness evals <run-id>
```

The target may also be a run directory, its `usage` directory, or an explicit
`usage/events.jsonl` path. The default output is a compact score-and-cost
trajectory, including [challenge-defined metrics](evaluation-events.md).
Use `--jsonl` to emit the complete matching JSON lines unchanged.

### `experiment`

Create `experiment.yaml` under the configured namespace's experiment directory,
for example `experiments/users/bx/runtime-sweep/experiment.yaml`, and edit the
controls and axes:

```yaml
schema_version: 1
type: experiment
id: runtime-sweep

labels:
  status: planned

relations:
  task: task:projects/dungeness/sample-starter
  claims:
    - claim:users/bx/runtime-effect

design:
  kind: full-factorial
  repetitions: 3

  controls:
    task: task:projects/dungeness/sample-starter
    model_access:
      models:
        - provider: openai
          upstream_id: openai/gpt-6-astra
          request_model: gpt-6-astra
          api: openai-responses
          name_format: request
    budget:
      max_usd: 1
      max_model_tokens: 1000000
    initialization:
      mode: checkpoint
    runtime:
      env_file: .env
      keep_render: false
      keep_images: false
      agent_timeout_sec: 2700

  axes:
    agents:
      - ref: agent:projects/dungeness/command
    checkpoints:
      - ref: checkpoint:public/examples/sample-challenge/62ae3d00d1e01d7bc640b5163cfea8dabffd8392

run_labels:
  purpose: harness-comparison

run_refs: []
artifact_refs: []
```

Keep the research statement and interpretation separate in `claim.yaml`:

```yaml
schema_version: 1
type: claim
namespace: users/bx
id: reasoning-effort-effect

relations:
  experiment: experiment:users/bx/runtime-sweep

statement: >-
  Requested reasoning effort affects verified improvement at equal budget.

predictions:
  - Higher effort improves median verified outcome.
  - Improvement has diminishing returns between high and xhigh.

estimands:
  primary:
    name: verified_relative_improvement
    formula: (reference_score - final_verified_score) / reference_score

analysis_plan:
  comparisons:
    - Compare effort levels within the fixed checkpoint.

limitations:
  - Three repetitions provide only an exploratory variance estimate.
```

Multiple claims may reference the same experiment, including competing
analyses created by other users or research agents. Claim catalog tooling is
not implemented yet, so claim identity is authored explicitly.

The experiment remains the executable core: controls, axes, repetitions, and
run-spec references. The claim carries the hypothesis and rules for
interpreting the resulting runs, so revising an analysis does not change what
was executed.

Materialize one independently runnable run spec per matrix cell:

```bash
./dungeness experiment create \
  runtime-sweep
```

The command validates the template, writes qualified `relations.run_specs`
back into it, and creates the files under
`run-specs/users/bx/runtime-sweep/` when the configured namespace is
`users/bx`. The namespace path is inferred from the configured default and
recorded explicitly in the experiment and generated run specs. Creation does
not launch agents or spend model budget.

Validate and review an experiment first:

```bash
./dungeness experiment run \
  runtime-sweep \
  --dry-run
```

Run all referenced cells sequentially:

```bash
./dungeness experiment run \
  runtime-sweep
```

The command displays the run count and nominal USD budget before asking for
confirmation. Use `--yes` for noninteractive execution and
`--continue-on-error` to attempt later cells after a failure. Every cell still
uses the ordinary `run` path and produces an independent canonical run record.
The experiment artifact is not automatically rewritten with results yet.

### `verify`

Every normal run is verified automatically. To rerun the exact clean verifier
later, first create the run with `--keep-render`, then execute:

```bash
./dungeness verify <run-id>
```

An explicit candidate path may be supplied as the second positional argument.

### `clean`

Release Docker containers, networks, and run-scoped images left behind by
finished runs:

```bash
./dungeness clean
```

Every run creates two Docker networks and several run-scoped images. `run`
tears down the environment and removes those images by default, including
after an interrupt. Use `--keep-images` or `runtime.keep_images: true` only
when the images are needed for debugging. Docker's built-in address pools hold
only 31 networks in total, so environments orphaned by an earlier kill will
eventually make every new run fail during compose with `all predefined address
pools have been fully subnetted`. `run` checks for room before rendering and
points here when it is short.

`clean` refuses to touch anything while a run is still executing, since a live
environment is indistinguishable from a leaked one; pass `--force` only when
you know the run is dead, and `--yes` to skip confirmation. To raise the
ceiling permanently, set `default-address-pools` in `~/.docker/daemon.json`
(this restarts the daemon, which kills any run in flight).

### `prune`

Permanently remove a local run:

```bash
./dungeness prune <run-id>
```

Prune asks for confirmation and refuses to remove a run referenced by another
canonical run record. Use `--yes` to skip confirmation in automation.

## Run Specifications

A run spec is a namespaced, reviewable configuration for one execution. The
starter run spec declares a one-dollar budget and an independent model policy. Optional fields
include `budget.max_model_tokens`, `initialization.resume_from`, and additional
labels.

Research strategy, memory, worker topology and evaluation cadence belong to the
harness. Configure only web access in the run spec:

```yaml
web_search:
  mode: disabled  # or optional, subject to trusted web policy and budget
```

`disabled` sets search and fetch budgets to zero. `optional` exposes only the
trusted, metered web tools allowed by the task. Neither grants direct internet
access or injects search instructions. The old `disabled-v1` and `optional-v1`
profile references are accepted as access-only compatibility aliases. They do
not select or constrain the harness architecture. The mandatory
[gateway request policy](gateway-request-policy.md) blocks provider-hosted search
and accepts only reviewed inference fields and locally executed tools in either
mode.

Strategy profiles, run-spec `evaluation`, `research_state`, and
`initialization.knowledge_base` are rejected with migration messages. Bundle
research instructions, documents, retrieval code and subagents into the harness.
See [command harnesses](command-harness.md).
The task still selects the trusted evaluator and its resource limits. Runtime
instructions describe candidate paths, tools, accounting and the deadline;
they do not prescribe evaluation frequency or researcher topology.

When a run spec omits `namespace`, its identity namespace is inferred from the
configured default. The resulting run namespace is resolved independently
through `--namespace`, the environment, or user configuration. Both resolved
namespaces are recorded in the canonical run record.

Root-level YAML files under `run-specs/` are ignored by Git. Place a spec in a
descriptive subdirectory when it should be committed or shared.

Task, agent, and checkpoint references are fully qualified because each record
may belong to a different namespace. The exact run-spec YAML, including its
path and SHA-256 hash, is embedded in the resulting `record.json`.

Generated run IDs begin with the run-spec ID:

```text
<run-spec-id>-<UTC timestamp>-<unique suffix>
```

Experiment-generated run-spec IDs already include the experiment and matrix
cell identity. A run directory such as:

```text
sample-harness-sweep-command-c6f6d2c-r1-20260821T190000Z-a1b2c3d4
```

can therefore be associated with its run spec and experiment without opening
the record or running a lookup command. Explicit `run_id` and `--run-id` values
still override this convention.

Future run specs will also declare which prior artifacts the research agent may
search and retrieve. Access will go through the trusted gateway rather than a
direct run-directory mount, and the resolved view will be recorded with the
run.

An agent manifest declares a Docker image and `dungeness-command-v1`
entrypoint. It cannot select a host adapter, native authentication or host
launcher configuration. Choose providers and models independently in
`model_access`. The harness owns its coding-agent installation and options.

Prices, credentials and upstream endpoints remain trusted gateway configuration.
Accounting uses `services/gateway/pricing.yaml`; unpriced combinations are
rejected before reaching the provider.

> Whether access to another agent's artifacts is appropriate is a decision for
> the run-spec author. Dungeness will enforce and record the declared policy; it
> will not impose one universal definition of cheating.

## Namespaces and Types

Every manifest stores a local `id`, a `type`, and a `namespace`. References use
their fully qualified form:

```text
<type>:<namespace>/<id>
```

Examples:

```text
problem:public/sample-challenge/sample-problem
task:projects/dungeness/sample-starter
agent:projects/dungeness/command
run-spec:users/bx/sample-starter-1usd
run:users/bx/<run-id>
```

A namespace is a naming and administrative scope. It is not automatically an
owner, visibility rule, semantic category, or filesystem path.

Current conventions:

| Namespace | Purpose |
|---|---|
| `users/<name>` | User-authored definitions and runs |
| `projects/dungeness` | Reusable definitions maintained by this project |
| `public/github/<org>/<repo>` | Imported public Git history |
| `public/<project>` | Public semantic records |
| `system/dungeness` | Trusted policies, services, and adapters |

Important record types:

| Type | Meaning |
|---|---|
| `problem` | Stable semantic research objective and metric |
| `task` | Executable representation of a problem |
| `checkpoint` | Immutable public Git starting state |
| `agent` | Research-agent implementation and model configuration |
| `run-spec` | Authored configuration for one execution |
| `run` | One resolved execution attempt |
| `artifact` | Output referenced by a run; richer catalog support is future work |
| `experiment` | Authored multi-run design executed through referenced run specs |
| `claim` | Research statement, estimands, analysis plan, and limitations |

System manifests additionally use `policy`, `service`, and `adapter`.

Physical directories are organized for humans and do not define identity. For
example, files under `checkpoints/sample-challenge/` retain the logical
namespace `public/examples/sample-challenge`.
Physical paths conventionally mirror namespaces for human organization, but
the CLI infers that prefix from the configured default. For example,
`experiment run runtime-sweep` resolves beneath
`experiments/users/bx/` when the default is `users/bx`. Manifest fields remain
authoritative.

The same convention applies to editable tasks and agents:

```text
tasks/users/bx/<task>/task.yaml
agents/users/bx/<agent>/agent.yaml
```

`dungeness init` creates the namespace directories. Unqualified task and agent
names first resolve in the configured namespace, then fall back to a unique
shared definition. Thus a user-created `agents/users/bx/command/`
takes precedence over the project definition for `--agent command`;
use `agent:projects/dungeness/command` when the shared definition
must be selected explicitly.

See [DESIGN.md](../DESIGN.md) for the complete model and conventions.

## How Records Connect

```text
problem <- task

run-spec
  -> task
  -> agent
  -> checkpoint

experiment
  -> run-spec (one or more)

claim
  -> experiment

run
  -> run-spec
  -> task
  -> problem
  -> agent
  -> checkpoint
  -> resumed_from (optional)
```

Cross-namespace references are normal. A run in `users/alice` may use a task in
`users/bx`, an agent in `projects/dungeness`, and a checkpoint in
`public/github/...`.

User-authored experiment manifests can describe a controlled matrix and reference
independently runnable run specs. The `experiment` command operates on those local
inputs; the repository no longer bundles personal experiment matrices. Each cell
can also be launched with `dungeness run PATH`. Experiment authoring never starts
model calls; executing a matrix consumes the configured model allowance.

## Run Records

Each new execution writes `runs/<namespace>/<run-id>/record.json` before
Harbor starts and finalizes it with status, usage, scores, and execution
summary. Commands accept a run ID without requiring its namespace path.

The universal envelope is:

```json
{
  "schema_version": 1,
  "id": "<run-id>",
  "type": "run",
  "namespace": "users/bx",
  "created_at": "2026-08-20T20:00:00.000Z",
  "published_at": "2026-08-20T21:00:00.000Z",
  "labels": {"purpose": "baseline"},
  "relations": {
    "task": "task:projects/dungeness/sample-starter",
    "problem": "problem:public/sample-challenge/sample-problem",
    "checkpoint": "checkpoint:public/examples/sample-challenge/<commit>",
    "agent": "agent:projects/dungeness/command",
    "run_spec": "run-spec:users/bx/sample-starter-1usd"
  },
  "data": {}
}
```

`data.configuration` preserves the complete non-secret configuration:

- authored source manifests with paths and SHA-256 hashes;
- resolved policies, resources, verifier settings, initialization, and limits;
- parsed Harbor task, job, and Compose documents;
- the exact rendered instruction; and
- Harbor, LiteLLM, and Python launcher versions.

Environment-file contents and real provider credentials are never copied into
the record.

## Execution Boundary

1. Dungeness checks out the selected checkpoint.
2. It renders a temporary Harbor task in the OS temporary directory.
3. The agent works inside an internal-only Docker network.
4. Model and web calls pass through the trusted gateway for metering, budgets,
   tracing, credential policy, and historical web cutoff enforcement.
   Provider credentials are held only by the gateway. No refresh proxy is
   supplied to the harness.
   Historical web search fails closed: undated, post-cutoff, and known mutable
   results are removed before the agent sees them. Mutable dated pages are
   metadata-only, and full fetches require immutable version-pinned URLs.
5. Only approved candidate paths reach the evaluation sidecar and final clean
   verifier.
6. Run containers, networks, volumes, and run-scoped Docker images are removed
   unless image retention was requested.
7. The temporary render is deleted unless `--keep-render` was selected.

Gateway details are documented in
[services/DESIGN.md](../services/DESIGN.md).

## Repository Layout

```text
problems/       semantic objectives
tasks/          executable problem representations
run-specs/      local and intentionally shared single-run configurations
experiments/    locally authored experiments (created when needed)
checkpoints/    immutable public source samples
agents/         research-agent definitions and images
verifiers/      trusted grading implementations
policies/       network, web, and budget policies
services/       trusted runtime services
src/dungeness/  backend-neutral run compiler and CLI support
adapters/       execution-system manifests and compatibility entry points
runs/           persistent run records, usage, and Harbor results
```

## Challenge assets

Dungeness ships no benchmark. Operators install trusted tasks, checkpoints,
scaffolds and verifiers from their challenge package. Examples in this document
use synthetic record names; they are not runnable bundled challenges. Resource
limits belong to the installed task and the resolved run configuration.

## Caveats

- `dungeness verify` reuses the verifier memory limit recorded in the retained
  run. `--memory` remains available as an explicit override.
- Harbor's clean `no-network` verifier is supported on Linux. On macOS, the
  agent and evaluation-sidecar records are still produced, but official clean
  verification should run on Linux.
- A global artifact catalog and agent-visible artifact search are not yet
  implemented. Current outputs remain under their run directories.
- Subscription budgeting is normalized token accounting, not actual provider
  billing, and may exceed the configured cap by the final in-flight response.

### Optional model-token ceiling

The standard budget policies have no model-token ceiling. Model usage remains
metered, with USD, request, concurrency and execution-time controls unchanged.
Use `--max-model-tokens N` for an explicit ceiling, or `--no-model-token-limit`
to disable one inherited from a custom policy. In a run spec,
`budget.max_model_tokens: null` explicitly disables the policy ceiling.
The gateway represents an unlimited token allowance as JSON `null` in `/status`.
