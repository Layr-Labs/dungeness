# Dungeness Record and Execution Design

This document defines Dungeness's record model, naming conventions, execution
lifecycle, and persistence rules. See [README.md](README.md) for the
copy-paste quick start and command reference.

## Design Goals

Dungeness should:

- reproduce an agent run from a resolved, non-secret configuration;
- keep public source history independent from Dungeness task definitions;
- allow records in different namespaces to reference one another;
- preserve facts needed for future filtering by time, labels, and provenance;
- keep generated Harbor configuration temporary; and
- leave room for multi-run experiments and artifact search without imposing
  their schemas prematurely.

The core record graph is:

```text
problem <- task

run-spec
  -> task
  -> agent
  -> checkpoint

run
  -> run-spec (when used)
  -> task
  -> problem
  -> agent
  -> checkpoint
  -> resumed_from (optional)
```

The records are deliberately independent. A run can combine a task authored by
one user, an agent maintained by Dungeness, and a checkpoint imported from a
public Git repository.

## Universal Record Contract

First-class records use a common envelope:

```yaml
schema_version: 1
type: run
namespace: users/bx
id: ecdsa-fail-62ae3d00-claude-20260820T120000Z-a1b2c3d4

created_at: "2026-08-20T12:00:00.000Z"
published_at: "2026-08-20T13:00:00.000Z"

labels:
  purpose: baseline

relations:
  agent: agent:projects/dungeness/claude

data: {}
```

The universal concepts are:

| Field | Meaning |
|---|---|
| `schema_version` | Version of the record schema |
| `type` | What the record represents |
| `namespace` | Naming and administrative scope |
| `id` | Local name, unique for its type within its namespace |
| `created_at` | When the record or output was created |
| `published_at` | When it became discoverable, when known |
| `labels` | Flexible searchable metadata |
| `relations` | Qualified references to other records |
| `data` | Fields specific to the record type |

Not every source manifest needs every optional field. Persistent run records
contain the complete envelope. Timestamps use UTC RFC 3339 strings.

### Identity and References

A record's identity is the tuple:

```text
(type, namespace, id)
```

Manifests store these components separately. `id` is always local:

```yaml
type: agent
namespace: projects/dungeness
id: claude
```

Relations and command inputs may use the qualified reference:

```text
<type>:<namespace>/<id>
```

For example:

```text
agent:projects/dungeness/claude
task:projects/dungeness/ecdsa-starter
checkpoint:public/github/layr-labs/ecdsafail-challenge/62ae3d00...
run-spec:users/bx/ecdsa-fail-claude-1usd
run:users/bx/<run-id>
```

Do not store a qualified reference in `id`, repeat the type as a label, or infer
identity from a file path.

## Namespace Convention

A namespace is similar to a Kubernetes namespace: it supplies a scope for
names and a useful administrative context.

It does not inherently mean:

- owner or creator;
- read or write authorization;
- public or private visibility;
- research topic or record type; or
- physical directory.

Those concerns may later use attribution fields, access policies, visibility
fields, types, labels, and relations. Cross-namespace references are normal and
do not copy a record.

Current namespace conventions are:

| Pattern | Use |
|---|---|
| `users/<name>` | User-created definitions and runs |
| `projects/dungeness` | Reusable definitions maintained by this project |
| `public/github/<org>/<repo>` | Facts imported from public Git history |
| `public/<project>` | Public semantic records not tied to one Git revision |
| `system/dungeness` | Trusted runtime policies, services, and adapters |

Examples:

```text
problem:public/ecdsafail-challenge/ecdsa-fail
task:projects/dungeness/ecdsa-starter
agent:projects/dungeness/claude
policy:system/dungeness/gateway-only
```

The configured user namespace is the default for newly authored user records,
including run specs, experiments, and runs. It does not restrict which tasks,
agents, or checkpoints those records may reference.

Run namespace resolution is:

```text
--namespace
DUNGENESS_NAMESPACE
user configuration
otherwise: error
```

`dungeness init --namespace users/<name>` writes the user configuration.
Authored run-spec and experiment templates may omit `namespace`; Dungeness
resolves the configured default and records it in materialized identities. A
run-spec's namespace identifies that run-spec; it does not silently replace
the operator's run namespace.

### Filesystem Layout

Directories are organized for people and conventionally mirror user
namespaces, but they do not define logical identity. CLI commands infer the
configured namespace prefix, so users can write `experiment run runtime-sweep`
instead of spelling `experiments/users/bx/runtime-sweep`.

Tasks and agents use the same current-namespace lookup. An unqualified local
name first resolves under the configured namespace, then falls back only when
there is one unique matching shared record. A fully qualified reference always
selects its exact logical identity. This lets users modify or fork definitions
under:

```text
tasks/users/<name>/<task>/
agents/users/<name>/<agent>/
```

without changing project-maintained definitions under
`agents/projects/dungeness/`.

For example:

```text
checkpoints/ecdsafail-challenge/<commit>.yaml
```

may contain:

```yaml
type: checkpoint
namespace: public/github/layr-labs/ecdsafail-challenge
id: <commit>
```

Moving that manifest to another directory does not change its identity.

## Record Types

The current record types are intentionally small.

| Type | Status | Meaning |
|---|---|---|
| `problem` | Implemented | Stable semantic research objective |
| `task` | Implemented | Executable representation of a problem |
| `checkpoint` | Implemented | Immutable public source state |
| `agent` | Implemented | Research-agent implementation and model configuration |
| `run-spec` | Implemented | Authored configuration for one run |
| `run` | Implemented | One resolved execution attempt |
| `policy` | Implemented | Trusted execution policy |
| `service` | Implemented | Trusted runtime service |
| `adapter` | Implemented | Integration with an execution system |
| `artifact` | Future catalog type | Searchable output referenced by a run |
| `experiment` | Implemented orchestration | Controlled collection of run specs |
| `claim` | Authored; catalog tooling future | Research statement and interpretation plan |

Verifier bundles are trusted implementations selected by tasks. They are not
currently catalog records.

### Problem

A problem records stable meaning, independent of any one repository layout,
language, verifier, or instruction:

```yaml
type: problem
namespace: public/ecdsafail-challenge
id: ecdsa-fail

labels:
  domain: quantum-resource-estimation

data:
  objective: minimize the reversible quantum resource cost of secp256k1 point addition
  metric:
    name: ecdsafail_score
    direction: minimize
```

Different tasks can represent the same problem.

### Task

A task defines how Dungeness makes a problem executable:

- the agent instruction;
- workspace materialization;
- candidate interfaces and allowed paths;
- verifier selection;
- policies;
- evaluation mode; and
- resource limits.

```yaml
type: task
namespace: users/bx
id: ecdsa-fail

relations:
  problem: problem:public/ecdsafail-challenge/ecdsa-fail

interfaces:
  point-add-module-v1:
    candidate:
      allowed_paths: [src/point_add]
    verifier: ecdsa-fail/benchmark-sh
```

A task does not own a checkpoint. A run binds a task to a compatible public
checkpoint through the checkpoint's declared source interface.

### Checkpoint

A checkpoint records facts about one immutable source state:

```yaml
type: checkpoint
namespace: public/github/layr-labs/ecdsafail-challenge
id: 62ae3d00d1e01d7bc640b5163cfea8dabffd8392

created_at: null
published_at: null

labels:
  role: challenge-start

data:
  repository:
    url: https://github.com/Layr-Labs/ecdsafail-challenge.git
    commit: 62ae3d00d1e01d7bc640b5163cfea8dabffd8392
  history:
    anchor: c6f6d2c7f50353259241e296458afb0e651e6c37
    distance_from_anchor: 868
    counting_method: git-rev-list-ancestry-path-count
  web_cutoff: "2026-05-28T23:59:59.999Z"
  interface: point-add-module-v1
```

The commit SHA provides stable identity. `history.distance_from_anchor`
communicates a sample's position in the selected Git ancestry without unstable
ordinal names such as `k1`, `k2`, or `k3`. Another sample can be inserted
without renaming existing records.

The checkpoint does not reference a Dungeness task, problem, or verifier. It is
a neutral public source fact that different executable representations can use.

`web_cutoff` is checkpoint-specific knowledge-boundary data. It is not a
replacement for the universal `created_at` or `published_at` fields.

### Agent

An agent record describes a runnable research agent:

- package and pinned version;
- model, provider route or subscription authentication, and API protocol;
- an optional trusted protocol-adapter reference;
- Harbor agent integration and arguments;
- non-secret environment values; and
- container image.

The agent is deliberately a complete runnable profile rather than a composition
of separate model and route records. Variants such as Codex/OpenRouter,
Codex/ChatGPT-subscription, and Codex/Kimi use separate agent identities. This
keeps run specs small and makes the configuration actually tested by an
experiment explicit. If the number of combinations later becomes difficult to
maintain, model composition can be introduced from observed requirements.

Model pricing, provider credentials, upstream endpoints, and adapter
implementations are trusted gateway policy under `system/dungeness`, not
editable agent metadata. The gateway prices the actual provider/model requested
and rejects combinations absent from its catalog. An agent may optionally
select an adapter only through a qualified
`adapter:system/dungeness/<id>` reference.

Repository-maintained agents use `projects/dungeness`. A customized agent can
use `users/<name>` while keeping the same local ID without collision.

### Run Spec

A run spec is a reviewable input for one execution:

```yaml
schema_version: 1
type: run-spec
namespace: users/bx
id: ecdsa-fail-claude-1usd

task: task:projects/dungeness/ecdsa-starter
agent: agent:projects/dungeness/claude
checkpoint: checkpoint:public/github/layr-labs/ecdsafail-challenge/<commit>

budget:
  max_usd: 1

initialization:
  mode: checkpoint

web_search:
  mode: optional

labels:
  purpose: baseline

runtime:
  env_file: .env
  keep_render: false
  keep_images: false
  agent_timeout_sec: 2700
```

`runtime.agent_timeout_sec` overrides the task's default Harbor agent deadline
for this run. The rendered instruction reports this hard deadline without prescribing
work cycles or a finalization strategy.

`runtime.keep_images` defaults to `false`, so run-scoped Docker images are
removed after teardown. Set it to `true` only when those images are needed for
debugging.

`web_search.mode` controls access (`disabled` or `optional`), subject to trusted
budgets and web policy. Disabled access zeros search and fetch allowances. The
resolved access mode is captured in provenance. Research prompts, evaluation
cadence and subagent topology belong to the harness. The runtime does not load
strategy profiles or install a `research-worker` command.

Task, agent, and checkpoint references are qualified so namespace mismatches
are detected before execution. The run spec may provide labels, budgets,
initialization, and runtime defaults. Explicit CLI flags override those values
for one attempt.

A run spec is not an experiment. It specifies one run. README contains the
starter YAML; `dungeness init` configures the default namespace for resulting
runs and does not generate or modify run-spec files.

### Run

A run is one unique execution attempt. Repeating the same run spec creates a
new run ID and record:

```json
{
  "schema_version": 1,
  "type": "run",
  "namespace": "users/alice",
  "id": "ecdsa-fail-claude-1usd-20260820T120000Z-a1b2c3d4",
  "relations": {
    "run_spec": "run-spec:users/bx/ecdsa-fail-claude-1usd",
    "task": "task:projects/dungeness/ecdsa-starter",
    "problem": "problem:public/ecdsafail-challenge/ecdsa-fail",
    "checkpoint": "checkpoint:public/github/layr-labs/ecdsafail-challenge/<commit>",
    "agent": "agent:projects/dungeness/claude"
  },
  "data": {
    "status": "completed"
  }
}
```

By default, the human-readable portion of a run ID is the local run-spec ID:

```text
<run-spec-id>-<UTC timestamp>-<unique suffix>
```

Because materialized experiment cells begin their run-spec IDs with the
experiment ID, filesystem names expose both correspondences. Oversized IDs are
compacted deterministically while retaining their beginning, ending, and a
stable digest. Flag-only runs retain the task/checkpoint/agent naming fallback.

The run namespace comes from the operator's selected namespace. The relation to
the run spec preserves which authored configuration was used.

When `--resume-from` is used, the run also records a qualified `resumed_from`
relation. The prior run remains a separate immutable observation.

### Artifact

Today, run outputs are retained inside the run's Harbor result directory. There
is no global artifact catalog or top-level artifact store.

The future `artifact` type will make selected outputs first-class and
searchable. It can use the same identity, namespace, timestamp, label, and
relation concepts. We should add it only together with a canonical writer,
manifest, and storage lifecycle.

### Experiment

An experiment is the minimal operational design for a controlled group of
runs. It records:

- controlled variables;
- matrix axes or other run-selection rules;
- repetitions;
- ordered references to materialized run specs; and
- references to resulting runs or artifacts when those become available.

An experiment does not need to assert a hypothesis or prescribe an
interpretation. The same completed experiment may support multiple competing
claims.

The experiment design is authored as YAML, rather than assembled from a large
set of CLI flags. `dungeness experiment create <id-or-path>` validates a
full-factorial template, materializes one ordinary run spec per cell, and
writes their qualified references into `relations.run_specs`. A bare ID is
resolved beneath the configured namespace directory.
`dungeness experiment run <id-or-path>` then validates those references,
reports the run count and nominal budget, prompts for confirmation, and
delegates every cell to the normal run execution path. Execution is sequential
in the order authored by `relations.run_specs`.

The first implementation deliberately does not rewrite the experiment as runs
finish. Attaching resolved run references and output artifacts remains
separate from orchestration. Upload and publication are also not implemented.

### Claim

A claim is an authored research proposition and interpretation plan associated
with an experiment. It may contain:

- a statement or research question;
- predictions;
- estimands and formulas;
- an analysis and reporting plan;
- validity and failure-handling rules; and
- known limitations.

```yaml
type: claim
namespace: users/bx
id: runtime-effect

relations:
  experiment: experiment:users/bx/runtime-sweep

statement: Agent implementation affects verified improvement at equal budget.

estimands:
  primary:
    name: verified_relative_improvement
    formula: (reference_score - final_verified_score) / reference_score
```

Claims are intentionally separate from experiment execution. Multiple users or
agents may author different claims about the same experiment, and a claim can
be proposed before execution and revisited after results exist without
changing the experiment's run matrix. Conclusions and analyses do not require
a fixed file format; they can later be represented as referenced artifacts.

There is no claim-specific CLI or catalog implementation yet. For now, a claim
is an explicitly identified YAML record stored beside the experiment that it
references.

Personal experiment matrices and analysis scripts are archived separately.
The generic experiment CLI accepts user-authored local manifests and creates
ordinary run specs; it does not supply a research strategy.

### System Types

Trusted components use `system/dungeness`:

```yaml
type: policy
namespace: system/dungeness
id: gateway-only
```

Policy manifests are referenced by tasks and validated during resolution.
Services and adapters use one descriptor at the component root, such as
`services/gateway/service.yaml` and `adapters/harbor/adapter.yaml`. Ordinary
implementation files do not each need record metadata.

## Labels, Relations, and Time

These dimensions are independent:

- **Namespace** scopes names.
- **Type** selects record meaning and schema.
- **Labels** add flexible filtering dimensions.
- **Relations** preserve provenance and dependencies.
- **Time** supports historical queries and cutoffs.

Labels should describe facts useful for filtering:

```yaml
labels:
  purpose: baseline
  domain: quantum-resource-estimation
```

Do not encode a type, namespace, or security decision as a label. A label is
metadata, not authorization.

Relations use qualified references:

```yaml
relations:
  problem: problem:public/ecdsafail-challenge/ecdsa-fail
```

Use `created_at` for creation time and `published_at` for discoverability when
known. Domain-specific time fields, such as a checkpoint's `web_cutoff`, may be
added under `data`.

Future agent search should filter forbidden records before label matching,
full-text search, ranking, or result counts. The experiment designer or runner,
not the record schema, will choose the accessible namespace, type, label, and
time view.

## Execution Lifecycle

The preferred command is:

```bash
./dungeness run ecdsa-fail-codex-openrouter.yaml
```

Dungeness then:

1. resolves the run namespace;
2. validates the run spec and all qualified references;
3. resolves the problem, task, checkpoint, agent, policies, interface, verifier,
   resources, initialization, and budget;
4. creates a unique run ID and
   `runs/<run-namespace>/<run-id>/record.json`;
5. checks out the selected source commit;
6. renders Harbor configuration into an OS temporary directory;
7. executes the agent, metered evaluation, and automatic clean verification;
8. finalizes the run record with status, usage, score, and execution summary;
9. removes the temporary render unless `--keep-render` was requested.

The flag-only form is supported for ad hoc runs:

```bash
./dungeness run projects/dungeness/ecdsa-starter \
  --agent claude \
  --checkpoint 62ae3d0 \
  --max-usd 1
```

It resolves the same records and writes the same canonical run format.

## Persistent Run Storage

Each run lives under:

```text
runs/<namespace>/<run-id>/
  record.json
  harbor/
  usage/
    events.jsonl
    summary.json
  debug/
    harbor-task/     # only with --keep-render
```

`record.json` is canonical Dungeness metadata. Harbor output remains execution
evidence and run-local artifacts. The temporary render is not canonical and
there is no top-level `generated/` directory.

The run record is written before execution and finalized afterward. Its
`data.configuration` contains:

- `sources`: authored manifests, paths, SHA-256 hashes, and parsed content;
- `resolved`: effective references, interfaces, policies, resources, verifier
  settings, initialization, continuation, and limits;
- `generated`: parsed Harbor task, job, Compose topology, and exact rendered
  instruction; and
- `launcher`: pinned launcher versions and environment-file path.

Environment-file contents and real provider credentials are never recorded.

`usage/events.jsonl` is the append-only canonical stream ordered by a per-run
sequence number. Every record includes its source, kind, observed and recorded
timestamps, and event-specific data. The trusted gateway writes model inputs,
provider-visible reasoning, model outputs, tool calls, web activity, evaluator
scores and operational events into this stream. Evaluator events also carry the cumulative normalized
USD snapshot needed to plot score against cost without joining separate logs.
`usage/summary.json` is an atomically refreshed derived cache, not another raw
event stream.

Trusted sidecars send events to an authenticated, internal-only gateway
collector. Its random token is stored in the shared usage volume, which is not
mounted into the agent container. Provider authorization headers are never part
of event payloads. OpenAI reasoning summaries are recorded when returned, but
raw hidden chain-of-thought is unavailable; adapters for models that expose
`reasoning_content` record that field before protocol conversion.

If the collector is unavailable after a sidecar action has completed, that
trusted sidecar appends the same schema under a file lock with `sequence: null`
and evaluator completions include the latest readable usage snapshot. Fallback
writes are idempotent by `(source, event_id)`; normal collected events always
have an integer sequence.

Kimi K3 profiles constrain reasoning effort to the model's supported
`low`, `high`, and `max` values. The direct Moonshot adapter must preserve each
assistant message's `reasoning_content` with its tool calls on the following
turn; the OpenRouter Responses profile relies on the native Responses history
while retaining the untouched upstream events in the canonical event stream.

### Subscription Codex

`agent:projects/dungeness/codex-subscription` reuses the pinned Codex image but
authenticates with a ChatGPT subscription. The launcher:

1. validates the host's file-backed Codex login;
2. copies it into a mode-`0600` temporary directory;
3. mounts that directory read-only for one Harbor run; and
4. deletes the temporary copy afterward.

The agent remains on the internal Docker network. A trusted
`service:system/dungeness/codex-subscription-proxy` accepts only HTTP CONNECT
requests to `auth.openai.com` for OAuth token refresh. Model requests use
Codex's custom Responses provider at
`http://gateway:8080/model/chatgpt/v1`; the gateway forwards the ChatGPT bearer
credential to the fixed upstream Codex endpoint. The proxy cannot reach that
model endpoint and is not a generic web proxy.

The gateway extracts provider-reported usage, applies
`policy:system/dungeness/model-pricing`, and rejects the next request once the
normalized USD limit is reached. Like API accounting, this is a
between-response limit and can overshoot by the final response. Subscription
runs record `normalized_usd`, `billed_usd: null`, and
`accounting_method: gateway`.

This mode deliberately has a reduced credential-isolation classification:
Codex must be able to read the temporary OAuth credential. The persistent host
credential is never writable from the container, and refreshed container state
is not copied back.

`dungeness prune <run-id>` permanently removes an unreferenced local run. It
does not yet implement catalog retention, publication, or artifact garbage
collection.

## Trust Boundary

The agent receives a workspace copied from the selected checkpoint. Only task
approved candidate paths reach:

- the metered evaluation sidecar; and
- the final clean, no-network verifier.

The agent cannot modify trusted evaluator sources, gateway records, or verifier
implementation. API credentials remain gateway-only. Subscription Codex is the
explicit exception: it receives a read-only temporary OAuth credential and is
therefore marked reduced-isolation. All model and web calls pass through the
trusted gateway; the subscription proxy is restricted to OAuth refresh.

Verifier bundles live under top-level `verifiers/` because they are trusted
execution implementations, not children of a problem or checkpoint:

```text
verifiers/<family>/<bundle>/
  Dockerfile
  evaluator.lock.yaml
  grade.py
  serve.py
  test.sh
```

The evaluator lock pins the source revision and lists the trusted files copied
into the clean verifier. Third-party notices travel with copied third-party
files.

## Search and Publication Direction

Canonical files remain the source of truth. A future SQLite or other search
index should be derived and rebuildable.

Research agents must access prior artifacts only through a trusted catalog
route on the gateway. They must not receive a direct mount of `runs/`, a search
index, or an artifact store. The gateway applies the resolved run policy to
both search and retrieval and records every operation.

The run spec will explicitly select the agent's artifact view. It should
support at least:

```yaml
artifact_access:
  mode: query       # none, query, snapshot, or all
  include:
    - namespace: public/**
    - namespace: users/alice
      labels:
        status: published
  exclude:
    - labels:
        system.hidden: "true"
  published_before: "2026-05-28T23:59:59.999Z"
```

This schema is illustrative and not implemented yet. At run start, Dungeness
will resolve the declaration into an immutable access snapshot and store its
identity in the run record.

> **Artifact access is part of experimental design.** Dungeness must enforce
> the view selected by the run-spec author, but it must not assume that access
> to another research agent's artifacts is inherently cheating. A study may
> intentionally test isolated discovery, collaboration, continuation, or full
> access to prior work. Reproducibility comes from recording the chosen policy,
> not from imposing one universal policy.

Future search should support:

- namespace, type, label, and timestamp filters;
- relations from artifacts to producing runs and source checkpoints;
- exact publication or knowledge cutoffs;
- a resolved, immutable agent-visible search view per run;
- gateway-mediated search and retrieval audit records; and
- cross-namespace references without duplicating payloads.

Record metadata should describe facts. The run or future experiment design
should decide which facts and artifacts an agent may access. Namespace alone
must not be treated as visibility or authorization.

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
tests/          record, resolver, CLI, and lifecycle tests
```

This layout is for human navigation. Record identity always comes from the
manifest's `type`, `namespace`, and local `id`.
