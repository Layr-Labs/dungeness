# ResearchState runtime path

Status: current implementation
Last updated: 2026-08-27

This is the short architectural guide to the current ResearchState prototype.

## The important distinction

There are two separate integration paths:

```text
During the run:
  Gateway injects fresh ResearchState before every LLM request.

When Codex tries to finish:
  A Codex Stop hook asks ResearchState whether completion is allowed.
```

The Stop hook does **not** provide the normal per-request state updates. The
gateway does.

## Per-request path

```text
Codex prepares a Responses request
              |
              v
       Dungeness gateway
              |
              | POST current cumulative model usage
              v
       ResearchState service
              |
              | GET /model-view
              v
       Dungeness gateway
       - removes its previous injected snapshot
       - appends one fresh developer item
              |
              v
       Kimi adapter
       - converts developer to system
              |
              v
             Kimi
```

This happens before every model request. ResearchState snapshots therefore do
not accumulate in the conversation: the gateway recognizes its own marked
item, removes the old one, and inserts exactly one current view.

The view currently contains:

- distinct successful web searches;
- distinct authoritative evaluations;
- assigned levels and final minimums;
- model-token and normalized-USD progress;
- the number currently required by the progressive cadence;
- current search or evaluation debt;
- remaining final minimums; and
- completion eligibility.

When debt is positive, the same developer item contains a direct instruction
to clear it with useful, distinct tool actions.

## Observation path

The gateway reports successful, failed, rejected, and duplicate-aware web
search observations to ResearchState. The evaluation sidecar reports canonical
candidate digests, validity, and scores.

```text
web search result ------> gateway ----------+
                                             |
evaluation result ------> evaluation sidecar +--> ResearchState
```

The model cannot directly increment either counter. Only authoritative service
events count.

## Completion path

The Codex image contains a small ResearchState hook executable. Dungeness
installs it as a Codex Stop hook for controlled runs.

```text
Codex attempts to finish
          |
          v
      Stop hook
          |
          | POST /completion-attempt
          v
 ResearchState service
      |          |
      | accept   | block with current deficits
      v          v
    finish     continue same Codex turn
```

This is a final safety condition. It complements continuous gateway injection;
it does not replace it.

## What changed in Codex

Codex Core is unchanged.

The existing Dungeness Codex image includes the Stop-hook executable, but the
web-search and evaluation cadence calculations are not implemented inside the
image. They live in the separate Python ResearchState service. Continuous
delivery lives in the gateway.

More precisely:

| Capability | Requires changing Codex Core? | Current integration |
|---|---:|---|
| State and cadence calculation | No | Separate Python service |
| State injection before each model request | No | Dungeness gateway |
| Web-search event accounting | No | Dungeness gateway |
| Evaluation event accounting | No | Evaluation sidecar |
| Completion enforcement | No | Hook executable added to the Dungeness Codex image and installed by its wrapper |

Therefore, the current implementation changes the Dungeness Codex runtime
image and wrapper, but it does not patch the Codex source code.

## Portability limitation

The current continuous-delivery implementation is coupled to the Dungeness
gateway. An agent that sends model requests directly to a provider will not
receive a fresh ResearchState view before every model sample.

A Stop hook does not solve this limitation. It runs only when the agent
attempts to finish, not before ordinary model requests.

To support agents that do not use the Dungeness gateway, ResearchState needs a
delivery-adapter boundary:

```text
ResearchState service
        |
        +-- Dungeness gateway adapter
        +-- native agent callback or plugin
        +-- lightweight injection-only model proxy
        +-- host-owned agent-loop adapter
        +-- explicit tool-pull fallback
```

Preferred behavior is a `before_model_request` extension point that fetches the
latest model view and injects it ephemerally. This may be supplied by the agent
harness, an SDK callback, or a plugin; it does not inherently require changing
the agent's core implementation.

For an opaque agent executable with neither a pre-model callback nor a
configurable model endpoint, guaranteed per-sample injection is not possible
externally. The available choices are then:

1. add a narrow native integration to that agent;
2. route its model traffic through a small injection-only proxy; or
3. expose `research-state show` or an MCP resource and accept that reading the
   state is voluntary rather than guaranteed.

The long-term interface should separate delivery from state ownership:

```python
class ResearchStateDeliveryAdapter:
    def before_model_request(self, request): ...
    def observe_tool_event(self, event): ...
    def completion_decision(self, attempt): ...
```

The current gateway implementation should become one adapter for this
interface, not an architectural requirement of ResearchState.

## Where to look

| Concern | File |
|---|---|
| Cadence, counters, deduplication, completion policy | `services/research-state/server.py` |
| Per-request state fetch and developer-item injection | `services/gateway/gateway.py` |
| Kimi developer-to-system conversion | `services/gateway/kimi_adapter.py` |
| Codex completion hook | `agents/common/research_state_hook.py` |
| Hook installation and normal-exit finalization | `adapters/harbor/codex_gateway.py` |
| Compose and run-spec wiring | `adapters/harbor/build.py` |
| Low/medium/high targets | `research-state/system/dungeness/two-knob-v1.yaml` |

## Current experimental boundary

The prototype controls two independent quantities:

```text
web-search frequency
authoritative-evaluation frequency
```

For either control, the current progressive requirement is:

```text
progress = max(token fraction, normalized-USD fraction)
required_now = ceil(final minimum * progress)
debt = max(0, required_now - qualifying distinct count)
```

This is intentionally narrow. If the mechanism works reliably, the same
service can later expose richer research strategy state without moving policy
into the gateway or Codex hook.
