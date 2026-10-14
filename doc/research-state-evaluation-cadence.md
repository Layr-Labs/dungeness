# ResearchState evaluation-cadence implementation

Status: implemented prototype
Last updated: 2026-08-27

For the shorter architectural explanation, start with
[`research-state-runtime-path.md`](research-state-runtime-path.md). In
particular:

```text
normal model calls -> gateway injects one fresh ResearchState item
final completion   -> Codex Stop hook checks enforced minimums
```

These are separate mechanisms. Per-request state delivery does not depend on
the Stop hook.

## 1. Purpose

The prototype tests whether Dungeness can tune how frequently an autonomous
agent uses the authoritative benchmark evaluator.

The previous mechanism supplied an evaluation target in the initial prompt and
checked the minimum only when Codex attempted to stop. That mechanism did not
control behavior during the run. A Kimi-high run spent its full $12 model
budget while producing only four distinct authoritative evaluations.

The current implementation adds two capabilities:

1. Dungeness computes how many evaluations should have occurred at the current
   model-budget position.
2. Dungeness injects a fresh authoritative ResearchState developer item into
   every Responses API model request.

The prototype remains prompt-level control during the trajectory. The
completion minimum remains a separate final condition.

## 2. Architecture

```text
                         trusted environment events
                    +--------------------------------+
                    |                                |
                    v                                v
          model gateway usage                 evaluation sidecar
          tokens, USD, requests               candidate digest,
                    |                         validity, score
                    +---------------+----------------+
                                    |
                                    v
                        Python ResearchState service
                        - counters and deduplication
                        - budget progress
                        - evaluations due
                        - evaluation debt
                        - completion eligibility
                                    |
                         GET /model-view before
                         every Responses request
                                    |
                                    v
                            model gateway
                    adds one fresh developer item
                                    |
                                    v
                              Kimi / LLM
```

The controller is a separate Python service. The gateway transports state but
does not own the research policy. The gateway is authoritative for web-search
events, and the evaluation sidecar remains authoritative for candidate
identity, validity, and score.

## 3. Components

### 3.1 ResearchState service

File: `services/research-state/server.py`

The service is one run-scoped `ThreadingHTTPServer` process. State is held in
memory while the run is active and persisted as:

```text
usage/events.jsonl                 # source: research-state
usage/research-state-summary.json
usage/research-state-final.json
```

The current prototype does not use SQLite. Concurrency is protected by a
process-local reentrant lock. Events are idempotent by `event_id`.

The service owns:

- assigned web-search and evaluation controls;
- model token and normalized-USD progress;
- distinct web-query identities;
- distinct evaluated-candidate identities;
- best valid score and candidate digest;
- progressive evaluation cadence;
- completion deficits and intervention counters; and
- the final controller summary.

### 3.2 Gateway

File: `services/gateway/gateway.py`

For every Responses request, the gateway:

1. reserves the model request in the normal usage ledger;
2. sends the current cumulative model-usage snapshot to
   `POST /events/model-usage`;
3. fetches `GET /model-view`;
4. removes any older gateway-injected ResearchState item from the outgoing
   request;
5. adds exactly one current developer item;
6. records the effective prompt and forwards the request; and
7. reports the completed response usage to ResearchState.

The gateway uses this marker to identify its own ephemeral item:

```text
## Current Dungeness research-effort state (per-request)
```

The injected item contains the compact JSON model view and an explicit
instruction when web-search or evaluation debt is positive.

If the ResearchState service is unavailable, injection fails open. The model
request continues and the failure is recorded in the gateway ledger.

### 3.3 Kimi Responses adapter

File: `services/gateway/kimi_adapter.py`

Codex sends Responses API items. Kimi Code accepts Chat Completions messages.
The adapter converts the injected `developer` item into a `system` message and
normalizes its content to a plain string.

The ResearchState item is added before the request is passed into the Kimi
adapter, so Kimi receives the same current state that is recorded in the
gateway timeline.

### 3.4 Harbor rendering

File: `adapters/harbor/build.py`

When a run enables ResearchState, the renderer:

- adds the isolated `research-state` Compose service;
- gives the gateway, evaluator, and main agent the internal controller URL;
- supplies the resolved control profile;
- supplies the model token and normalized-USD budgets;
- supplies the agent timeout and completion safeguards; and
- records the profile identity and SHA-256 in the resolved run.

The controller has no external-egress network.

### 3.5 Codex lifecycle adapter

File: `adapters/harbor/codex_gateway.py`

Codex hooks still provide:

- initial state context;
- the Stop completion check.

Per-request injection and knowledge-base behavior feedback do not depend on
those hooks. The knowledge-base sidecar reports qualifying inspiration events
directly to ResearchState for attribution to the next valid evaluation.

After a normal Codex process exit, the runner explicitly calls
`POST /finalize`. A timeout or nonzero Codex exit does not claim normal
completion. This was added after the real run exposed that service teardown
could otherwise overwrite a successfully completed run as `interrupted`.

## 4. Controller configuration

The rendered controller configuration contains:

```json
{
  "controls": {
    "evaluation": {
      "mode": "enforce_minimum",
      "level": "high",
      "minimum": 12,
      "soft_min": 12,
      "soft_max": 24,
      "global_limit": 200
    }
  },
  "model_budget": {
    "total_tokens": 5000000,
    "normalized_usd": 12.0
  },
  "agent_timeout_sec": 3600
}
```

Supported control modes remain:

```text
observe
prompt_only
enforce_minimum
```

Progressive cadence is included independently for each non-`observe`
web-search or evaluation control.

## 5. Web-search and evaluation cadence

Let:

```text
T = model tokens used
Tmax = assigned model-token budget
U = normalized USD used
Umax = assigned normalized-USD budget, when present
N = assigned final minimum for this control
C = qualifying distinct operations completed
```

Budget progress is:

```text
progress = min(1, max(T / Tmax, U / Umax))
```

If no USD budget is assigned, only the token fraction is used.

The current scheduled requirement is:

```text
required_now =
    0                              when progress = 0 or N = 0
    ceil(N * progress)             otherwise
```

Control debt is:

```text
debt = max(0, required_now - C)
```

The model also sees:

```text
remaining_final_minimum = max(0, N - E)
```

Using the maximum of token and USD progress prevents the schedule from falling
behind when either resource is consumed faster than the other.

## 6. Model-facing state

A model view has this general shape (synthetic example values):

```json
{
  "evaluation": {
    "level": "high",
    "minimum": 12,
    "soft_target": [12, 24],
    "qualifying_completed": 4,
    "duplicates": 1,
    "valid": 3,
    "invalid": 1,
    "best_score": 100,
    "best_candidate_sha256": "...",
    "cadence": {
      "budget_progress": 0.42,
      "required_now": 6,
      "debt": 2,
      "remaining_final_minimum": 8
    }
  },
  "model_usage": {
    "requests": 35,
    "tokens": 1300000,
    "token_budget": 5000000,
    "normalized_usd": 4.1,
    "normalized_usd_budget": 12.0,
    "remaining_tokens": 3700000,
    "remaining_normalized_usd": 7.9
  },
  "completion_eligible": false,
  "unmet_enforced_minimums": {
    "evaluation": 8
  }
}
```

When `debt > 0`, the developer item tells the model to perform enough distinct
web searches or candidate evaluations to clear the relevant debt before
continuing extended local work.

## 7. Qualifying evaluations

The evaluation sidecar sends:

```text
event_id
candidate_sha256
status
score
```

A distinct candidate qualifies when the sidecar returns either:

```text
valid
invalid
```

Invalid candidates qualify because they provide authoritative boundary
information. These do not qualify:

- duplicate candidate digests;
- transport failures;
- malformed or rejected submissions;
- budget rejections; and
- controller failures.

The best-candidate record updates only for valid results with a better score in
the configured metric direction.

## 8. HTTP surface

Read endpoints:

```text
GET /healthz
GET /model-view
GET /status
GET /summary
```

Trusted event endpoints:

```text
POST /events/model-usage
POST /events/web-search
POST /events/evaluation
```

Lifecycle endpoints:

```text
POST /completion-attempt
POST /finalize
```

Gateway and evaluator event endpoints accept only trusted internal service
addresses. Model-facing code cannot write authoritative counters directly.

## 9. Completion behavior

`enforce_minimum` still defines a final endpoint requirement:

```text
qualifying distinct evaluations >= assigned minimum
```

The Stop hook:

- accepts when all enforced minimums are satisfied;
- returns continuation feedback when work remains and safeguards permit; or
- accepts noncompliantly when a termination safeguard fires.

Per-request cadence and final completion are intentionally separate:

- cadence influences actions throughout the run;
- completion prevents a normal early finish below the final minimum.

Normal Codex exit now finalizes the service explicitly. Service interruption
without normal finalization remains recorded as `interrupted`.

## 10. Failure behavior

- State injection fails open so a controller outage does not destroy the base
  model trajectory.
- Failed deliveries are recorded as `research_state.delivery` events in
  `usage/events.jsonl`.
- Event snapshots are monotonic, so delayed usage messages cannot reduce the
  recorded token or USD counters.
- Duplicate event IDs are idempotent.
- State summaries are replaced atomically.
- A nonzero Codex exit does not finalize the controller as successful.

## 11. Tests

Primary tests:

```text
tests/test_research_state.py
services/gateway/tests/test_gateway.py
tests/test_record_model.py
```

Coverage includes:

- cadence calculation from tokens and USD;
- monotonic usage snapshots;
- evaluation and query deduplication;
- valid and invalid candidate classification;
- developer-item replacement;
- Kimi developer-to-system conversion;
- route-level per-request injection;
- Stop completion behavior;
- normal-exit `/finalize` behavior;
- profile rendering and Compose isolation; and
- runtime wrapper status preservation.

Most recent verification:

```text
13 ResearchState tests passed
54 gateway/Kimi tests passed
57 broader harness tests passed
Python compilation passed
git diff --check passed
```

## 12. Current limitations

- The progressive schedule is linear and currently applies only to web-search
  and authoritative-evaluation counts.
- State is in process memory during the run; JSONL and summaries provide
  persistence and auditability, but not restart recovery.
- Per-request injection is prompt-level control, not a hard tool-action gate.
- The cadence is linear in resource consumption and does not yet adapt to task
  phase, evaluation latency, candidate quality, or remaining finalization work.
- Distinct source states can produce equivalent circuits; candidate digest
  deduplication detects identical submitted files, not semantic equivalence.
- One successful run demonstrates controllability mechanics, not generality or
  causal benchmark-quality improvement.
