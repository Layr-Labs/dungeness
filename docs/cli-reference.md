# Dungeness CLI and historical examples

This reference retains the detailed CLI documentation and earlier experiment examples.
Start with [the runtime quick start](../README.md) for the maintained workflow.
Personal run specs and knowledge bases mentioned below remain in the full source
repository; they are excluded from runtime distributions. Recorded `runs/` outputs
were removed from the current tree and remain in Git history (LFS objects require
repository access).


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

Prerequisites: `uv`, `uvx`, Docker, the host Codex CLI for ChatGPT
subscription authentication, and enough Docker memory for the selected task.

1. Check prerequisites and create `.env`:

   ```bash
   ./dungeness setup
   ```

2. If the run enables gateway web search, add the Exa key to `.env`. Runs with
   zero search and fetch budgets do not need it. Then authenticate with the
   host Codex CLI; ChatGPT subscription runs do not need a model API key:

   ```dotenv
   EXA_API_KEY=...
   ```

   ```bash
   ./dungeness auth login codex
   ./dungeness auth status codex
   ```

3. Configure the namespace for runs you create:

   ```bash
   ./dungeness init --namespace users/<name>
   ```

4. Create `ecdsa-fail-v2-codex-subscription.yaml` under the configured
   namespace's run-spec directory, for example
   `run-specs/users/bx/ecdsa-fail-v2-codex-subscription.yaml`. The
   run-spec namespace is inferred from the default configured in step 3:

   ```yaml
   schema_version: 1
   type: run-spec
   id: ecdsa-fail-v2-codex-subscription-1usd

   task: task:users/bx/ecdsa-fail-v2
   agent: agent:projects/dungeness/codex-subscription
   checkpoint: checkpoint:public/github/layr-labs/ecdsafail-challenge/62ae3d00d1e01d7bc640b5163cfea8dabffd8392

   agent_options:
     reasoning_effort: xhigh
     reasoning_summary: detailed

   budget:
     max_usd: 1
     max_model_tokens: 1000000

   initialization:
     mode: checkpoint

   labels:
     # Searchable metadata for filtering and comparing runs; labels do not
     # change run identity or execution behavior.
     purpose: baseline

   runtime:
     env_file: .env
     keep_render: false
     keep_images: false
     # Optional run-level override of the task's default agent deadline.
     agent_timeout_sec: 2700
   ```

5. Launch the run. For subscription agents, `max_usd` is a normalized
   experimental budget rather than the amount billed by the provider:

   ```bash
   ./dungeness run ecdsa-fail-v2-codex-subscription.yaml
   ```

To use a Kimi Code membership instead, set
`TESTBED_KIMI_CODE_API_KEY` in `.env` and select
`agent:projects/dungeness/codex-kimi-subscription`. The key is created in the
Kimi Code console and consumes membership credits, not Moonshot Open Platform
pay-as-you-go balance.

Dungeness prints the generated run ID. Persistent output is written under:

```text
runs/users/<name>/<run-id>/
  record.json
  harbor/
  usage/
    events.jsonl
    summary.json
```

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

### `auth`

Codex can use an existing ChatGPT subscription. Log in with the host Codex CLI,
or verify the current login:

```bash
./dungeness auth login codex
./dungeness auth status codex
```

The default credential is `~/.codex/auth.json`. Set
`DUNGENESS_CODEX_AUTH_FILE` to use another file. Credentials are never copied
into the repository or `record.json`.

Select the ChatGPT subscription profile in a run spec:

```yaml
agent: agent:projects/dungeness/codex-subscription
```

This profile runs `gpt-5.6-sol`. To use GPT-6 Astra through the same ChatGPT
subscription credential, select:

```yaml
agent: agent:projects/dungeness/codex-astra-subscription
```

Subscription runs retain the agent's internal-only network. Codex sends model
requests to the same Dungeness gateway used by API-backed profiles. A narrow
allowlisted proxy exists only for OAuth token refresh; it cannot reach the
ChatGPT model endpoint. The gateway reads provider-reported usage and applies
trusted reference prices to enforce the normalized USD limit between
responses. `billed_usd` remains unknown because a ChatGPT subscription is not
billed per API token.

The credential is supplied as a read-only per-run temporary copy. It is still
readable inside the Codex container, so subscription runs have weaker
credential isolation than gateway API runs.

Kimi Code membership is a separate subscription-style route. Create a key in
the Kimi Code console, add it to `.env`, and select the membership profile:

```dotenv
TESTBED_KIMI_CODE_API_KEY=...
```

```yaml
agent: agent:projects/dungeness/codex-kimi-subscription
```

This profile runs Kimi K3 with a 1,048,576-token context window. It supports
`low`, `high`, and `max` reasoning effort and defaults to `high`. The key stays
in the trusted gateway; the agent receives only a placeholder credential.
`max_usd` uses Kimi K3 reference pricing for comparable experiment budgets,
while `billed_usd` remains unknown because membership usage is not billed per
token.

The repository includes a membership smoke run:

```bash
./dungeness run ecdsa-kimi-k3-subscription-1m-smoke.yaml
```

### Supported models and routes

The maintained Codex profiles currently support GPT-6 Astra, GPT-5.6-sol,
Kimi K3, Claude Opus 5, and Claude Fable 5.1; the Claude Code profiles support
Claude Opus 5 and Claude Fable 5.1:

| Agent | Model | Access route | Host credential |
|---|---|---|---|
| `agent:projects/dungeness/codex-subscription` | GPT-5.6-sol | ChatGPT subscription | `./dungeness auth login codex` |
| `agent:projects/dungeness/codex-astra-subscription` | GPT-6 Astra | ChatGPT subscription | `./dungeness auth login codex` |
| `agent:projects/dungeness/codex-kimi-subscription` | Kimi K3 | Kimi Code membership | `TESTBED_KIMI_CODE_API_KEY` |
| `agent:projects/dungeness/codex-astra-openai` | GPT-6 Astra | OpenAI Responses API | `TESTBED_OPENAI_API_KEY` |
| `agent:projects/dungeness/codex-openai` | GPT-5.6-sol | OpenAI Responses API | `TESTBED_OPENAI_API_KEY` |
| `agent:projects/dungeness/codex-openrouter` | GPT-5.6-sol | OpenRouter Responses API | `TESTBED_OPENROUTER_API_KEY` |
| `agent:projects/dungeness/codex-kimi` | Kimi K3 | Moonshot API through Responses-to-Chat | `TESTBED_MOONSHOT_API_KEY` |
| `agent:projects/dungeness/codex-kimi-openrouter` | Kimi K3 | OpenRouter Responses API | `TESTBED_OPENROUTER_API_KEY` |
| `agent:projects/dungeness/codex-claude-openrouter` | Claude Opus 5 | OpenRouter Responses API | `TESTBED_OPENROUTER_API_KEY` |
| `agent:projects/dungeness/codex-fable-openrouter` | Claude Fable 5.1 | OpenRouter Responses API | `TESTBED_OPENROUTER_API_KEY` |
| `agent:projects/dungeness/claude-openrouter` | Claude Opus 5 (Claude Code) | OpenRouter Anthropic-compatible Messages API | `TESTBED_OPENROUTER_API_KEY` |
| `agent:projects/dungeness/claude-fable-openrouter` | Claude Fable 5.1 (Claude Code) | OpenRouter Anthropic-compatible Messages API | `TESTBED_OPENROUTER_API_KEY` |
| `agent:projects/dungeness/claude` | Claude Opus 5 (Claude Code) | Anthropic Messages API | `TESTBED_ANTHROPIC_API_KEY` |

The model and provider route are pinned by the agent manifest. Run specs select
an agent profile and may override supported reasoning options; they do not
supply an arbitrary model name.

GPT-6 Astra normally uses the `codex-astra-subscription` profile so Codex-plan
access is kept separate from API billing. `codex-astra-openai` remains
available for direct API-key runs. Both routes use Codex 0.153.3 and gateway
accounting that separates ordinary input, cache reads, and cache writes, and
selects the full-request long-context pricing tier when reported input exceeds
272,000 tokens. Reasoning tokens are included in output tokens and are not
double counted.

The direct Moonshot API profile also uses the trusted Responses-to-Chat
adapter:

```yaml
agent: agent:projects/dungeness/codex-kimi
```

Set `TESTBED_MOONSHOT_API_KEY` in `.env`. The gateway records Kimi's decoded
`reasoning_content` before converting the response for Codex, then uses Kimi's
reported token usage for the ordinary run budget and summary.

For the simpler OpenRouter path, select:

```yaml
agent: agent:projects/dungeness/codex-kimi-openrouter
```

This profile needs only `TESTBED_OPENROUTER_API_KEY`. OpenRouter's Responses
API serves `moonshotai/kimi-k3` directly. Dungeness explicitly requests
provider-visible reasoning and records the reconstructed reasoning stream plus
the untouched response events in `usage/events.jsonl`.
Kimi K3 accepts `low`, `high`, and `max` reasoning effort; Dungeness rejects
other effort overrides before starting Harbor.

The repository includes a one-dollar smoke run:

```bash
./dungeness run ecdsa-kimi-k3-openrouter-smoke.yaml
```

### Codex with Claude Opus 5

To hold the Codex harness fixed and vary only the model, select:

```yaml
agent: agent:projects/dungeness/codex-claude-openrouter
```

This profile needs only `TESTBED_OPENROUTER_API_KEY` and reuses the
`codex-openrouter` image. OpenRouter's Responses API serves
`anthropic/claude-opus-5` with function calling, maps Codex's
`reasoning_effort` (`low`, `medium`, `high`, `xhigh`) onto Anthropic thinking
budgets, and returns provider-visible reasoning items, which the gateway records
in `usage/events.jsonl`. The profile defaults to
`reasoning_summary: none` because Anthropic reasoning arrives as content rather
than an OpenAI-style summary. Pricing follows the trusted policy entry for
Opus 5 through OpenRouter.

### Claude Code

Claude Code runs as a second research agent beside Codex. The simplest route
is OpenRouter, which serves the Anthropic Messages API that Claude Code speaks:

```yaml
agent: agent:projects/dungeness/claude-openrouter
```

This profile needs only `TESTBED_OPENROUTER_API_KEY`. It reuses the pinned
Claude Code image from `agents/projects/dungeness/claude`, disables Claude
Code's built-in `WebSearch` and `WebFetch` tools so research goes through the
gateway `web` command, and bills `anthropic/claude-opus-5` from the trusted
pricing policy at the same schedule as the direct Anthropic route. Claude Code
does not take Codex-style `agent_options`; extended thinking is capped by the
profile's `MAX_THINKING_TOKENS`.

Harbor's Claude Code launcher reads `ANTHROPIC_BASE_URL` from its own process
environment to decide how to pass the model name, so `dungeness run` exports
the selected profile's gateway route before starting Harbor and records it
under `configuration.launcher.control_plane_environment`. Do not set
`ANTHROPIC_BASE_URL` in `.env`: Harbor loads `.env` with override, and a
conflicting value makes `dungeness run` refuse to start.

The direct Anthropic profile `agent:projects/dungeness/claude` uses
`TESTBED_ANTHROPIC_API_KEY` instead.

### `run`

The preferred input is an authored run specification:

```bash
./dungeness run ecdsa-fail-v2-codex-subscription.yaml
```

CLI options override values in the YAML:

```bash
./dungeness run ecdsa-fail-v2-codex-subscription.yaml \
  --max-usd 2 \
  --label purpose=comparison
```

The equivalent flag-only form remains available:

```bash
./dungeness run ecdsa-fail-v2 \
  --agent codex-subscription \
  --checkpoint 62ae3d0 \
  --max-usd 1
```

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
./dungeness runs ecdsa-fail-v2-codex-subscription.yaml
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
trajectory. Use `--jsonl` to emit the complete matching JSON lines unchanged.

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
  task: task:users/bx/ecdsa-fail
  claims:
    - claim:users/bx/runtime-effect

design:
  kind: full-factorial
  repetitions: 3

  controls:
    task: task:users/bx/ecdsa-fail
    agent_options:
      reasoning_summary: detailed
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
      - ref: agent:projects/dungeness/codex-subscription
    checkpoints:
      - ref: checkpoint:public/github/layr-labs/ecdsafail-challenge/62ae3d00d1e01d7bc640b5163cfea8dabffd8392
    reasoning_efforts:
      - low
      - medium
      - high
      - xhigh

run_labels:
  purpose: reasoning-effort-comparison

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
Quick Start contains a complete one-dollar Codex example. Optional fields
include `budget.max_model_tokens`, `initialization.resume_from`, and additional
labels.

Agent-facing web-search instructions are versioned as namespaced profiles under
`web-search/<namespace>/`. A run spec selects one qualified profile.
Omitting `web_search`, or explicitly selecting the optional profile, preserves
the existing prompt:

```yaml
web_search:
  profile: web-search-profile:system/dungeness/optional-v1
```

To require a short web-search phase before editing:

```yaml
web_search:
  profile: web-search-profile:system/dungeness/required-preflight-v1
```

The required preflight asks the agent to form one actionable implementation
hypothesis, then continue with the normal edit-and-evaluate loop. It does not
change network access, historical cutoff enforcement, or web budgets.

To require one initial search without prescribing a query count or web-search
strategy:

```yaml
web_search:
  profile: web-search-profile:system/dungeness/initial-required-v1
```

This profile asks the agent to inspect the workspace, perform at least one
relevant search before editing or evaluating, and then decide whether further
web search is useful. The rendered prompt includes the selected checkpoint's exact
historical cutoff and explains that cutoff, missing-date, and mutable-source
rejections are expected policy outcomes rather than tool failures.

Adaptive research-policy experiments use three additional profiles:

- `m2-adaptive-single-agent-v1`: the main agent owns search, interpretation,
  and each next research decision.
- `m3-planner-thin-workers-v1`: the main agent owns the agenda and synthesis,
  while read-only `research-worker thin` calls execute narrow branches.
- `m4-dedicated-researcher-v1`: one read-only
  `research-worker autonomous` call owns the search process and returns an
  evidence packet.

Nested workers use the same configured model and reasoning effort. Their model
and web calls pass through the run's existing gateway and consume the same
shared budgets; they do not receive hidden extra search or model allowance.

The profile file, including its path, contents, and SHA-256 hash, is captured in
the run record. Create a new profile ID when changing prompt behavior so runs
remain comparable. These profiles control only agent instructions; trusted
network access and cutoff enforcement remain in `policies/web/` and the
gateway.

Agent-facing evaluation-loop instructions use the same mechanism under
`evaluation/<namespace>/`. Omitting `evaluation` preserves the default
iterative profile:

```yaml
evaluation:
  profile: evaluation-profile:system/dungeness/iterative-v1
```

The evaluation profile is rendered as a separate `### Evaluation loop` section
and captured in run provenance. It controls how the agent is instructed to use
`evaluate`; the task still determines whether an evaluation sidecar exists,
which benchmark it runs, and the evaluation budget.

Research strategy and evaluation cadence belong to the harness. The former
`research_state` run-spec option has been removed; new runs reject it with a
migration message. The gateway does not inject research-effort prompts, and
Codex completion is not gated on minimum search or evaluation counts. Replay
historical experiments using their original revision rather than dropping an
experimental policy silently.

Knowledge, memory and retrieval belong to the agent image. The knowledge-base
service, command, prompt profiles and Codex hooks have been removed. New run
specs reject `initialization.knowledge_base`; move its files and retrieval code
into the harness. See [migration](../doc/knowledge-base-preload.md).

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
ecdsa-effort-sweep-codex-subscription-c6f6d2c-low-20260821T190000Z-a1b2c3d4
```

can therefore be associated with its run spec and experiment without opening
the record or running a lookup command. Explicit `run_id` and `--run-id` values
still override this convention.

Future run specs will also declare which prior artifacts the research agent may
search and retrieve. Access will go through the trusted gateway rather than a
direct run-directory mount, and the resolved view will be recorded with the
run.

An agent manifest is a complete runnable profile: it pins the agent runtime,
model, provider route or subscription authentication, API protocol, and any
trusted protocol-adapter reference. For example, Codex through OpenRouter,
Codex through a ChatGPT subscription, and Codex through Kimi are separate agent
records. Run specs select one agent rather than assembling those components
independently.

Agent manifests do not define prices, credentials, provider endpoints, or
adapter implementations. Those remain trusted system configuration. Accounting
lives in `services/gateway/pricing.yaml` under `system/dungeness`; unpriced
provider/model combinations are rejected before reaching the provider. An
optional `adapter` field may only reference an implementation under
`adapter:system/dungeness/...`.

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
problem:public/ecdsafail-challenge/ecdsa-fail
task:users/bx/ecdsa-fail
agent:projects/dungeness/codex-openrouter
run-spec:users/bx/ecdsa-fail-codex-openrouter-1usd
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
example, files under `checkpoints/ecdsafail-challenge/` retain the logical
namespace `public/github/layr-labs/ecdsafail-challenge`.
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
shared definition. Thus a user-created `agents/users/bx/codex-openrouter/`
takes precedence over the project definition for `--agent codex-openrouter`;
use `agent:projects/dungeness/codex-openrouter` when the shared definition
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

Experiment artifacts describe a controlled matrix and reference independently
runnable run specs. The maintained example is
`experiments/users/bx/ecdsa-codex-openai-subscription-effort-sweep-62ae3d0-12usd/experiment.yaml`;
its 12 cells live under
`run-specs/users/bx/ecdsa-codex-openai-subscription-effort-sweep-62ae3d0-12usd/`. Run the matrix
with:

```bash
./dungeness experiment run ecdsa-codex-openai-subscription-effort-sweep-62ae3d0-12usd
```

Each cell can also be launched with the ordinary `dungeness run <path>`
command. Experiments do not require a fixed result format.

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
    "task": "task:users/bx/ecdsa-fail",
    "problem": "problem:public/ecdsafail-challenge/ecdsa-fail",
    "checkpoint": "checkpoint:public/github/layr-labs/ecdsafail-challenge/<commit>",
    "agent": "agent:projects/dungeness/codex-openrouter",
    "run_spec": "run-spec:users/bx/ecdsa-fail-codex-openrouter-1usd"
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
   Subscription Codex forwards its ChatGPT bearer credential through the
   gateway; its separate allowlisted proxy is limited to OAuth refresh.
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
experiments/    multi-run research designs and artifact references
checkpoints/    immutable public source samples
agents/         research-agent definitions and images
verifiers/      trusted grading implementations
policies/       network, web, and budget policies
services/       trusted runtime services
src/dungeness/  backend-neutral run compiler and CLI support
adapters/       execution-system manifests and compatibility entry points
runs/           persistent run records, usage, and Harbor results
```

## Current Task

| Task | Candidate | Metric | Direction |
|---|---|---|---|
| `ecdsa-fail` | Rust secp256k1 point-add implementation | `avg_toffoli * peak_qubits` | minimize |

## Caveats

- Current module-interface `ecdsa-fail` runs use a 4 GB agent cap and an 8 GB
  evaluation/verifier cap. The caps are upper bounds, not reservations. The
  historical single-file checkpoint retains its 20 GB verifier cap because its
  single-process evaluator was measured near 15 GB.
- `dungeness verify` reuses the verifier memory limit recorded in the retained
  run. `--memory` remains available as an explicit override.
- Harbor's clean `no-network` verifier is supported on Linux. On macOS, the
  agent and evaluation-sidecar records are still produced, but official clean
  verification should run on Linux.
- A global artifact catalog and agent-visible artifact search are not yet
  implemented. Current outputs remain under their run directories.
- Subscription budgeting is normalized token accounting, not actual provider
  billing, and may exceed the configured cap by the final in-flight response.
