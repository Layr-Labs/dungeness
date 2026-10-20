# Gateway Design (MVP)

## Purpose

The gateway gives an agent controlled access to the web and its language
model while preventing general internet access. It also records usage and
enforces the run's search and token budgets.

The gateway is testbed-owned and trusted. The agent sandbox is untrusted.

## Architecture

The MVP uses one gateway container per run:

```text
Agent container
├── web requests      -> Gateway -> Exa
├── model requests    -> Gateway -> configured model provider
└── other internet    -> blocked

Verifier container
└── all network       -> blocked
```

Web access, model proxying, accounting, and budget enforcement are one
service in the MVP. They can be separated later if needed.

## Non-goals

The MVP does not include:

- a shared multi-run gateway;
- agent-to-gateway authentication;
- capability discovery or `capabilities.json`;
- MCP support;
- multiple web providers;
- a separate budget service; or
- a general-purpose HTTP proxy.

## Deployment

The gateway runs beside the agent as a separate Docker Compose service. It is
outside the agent container and has no agent-writable filesystem mounts.

```text
Run A
├── agent-a
└── gateway-a

Run B
├── agent-b
└── gateway-b
```

Because every run has its own gateway, the gateway receives its run identity
and limits at startup. Requests do not need an agent authentication token.

## Network policy

The agent and gateway share an internal Docker network. Only trusted services
join a network with external egress. Every model profile uses the gateway.
There is no agent-side credential mount or authentication-refresh proxy.

```yaml
services:
  agent:
    networks:
      - agent_internal

  gateway:
    networks:
      - agent_internal
      - external_egress

networks:
  agent_internal:
    internal: true

  external_egress:
```

The gateway is not an open proxy. Its outbound connections are restricted to:

- the Exa API; and
- the model provider selected for the run.

The verifier runs later in a separate Harbor environment with `no-network`.

## Gateway configuration

The testbed configures the per-run gateway through environment variables:

```text
TESTBED_RUN_ID=world-map-local
MAX_SEARCHES=100
MAX_FETCHES=200
MAX_MODEL_REQUESTS=500
MAX_MODEL_TOKENS=1000000
```

API provider credentials are injected only into the gateway:

```text
EXA_API_KEY=<secret>
TESTBED_OPENROUTER_API_KEY=<secret>
```

`EXA_API_KEY` is injected and required only when search or fetch has a nonzero
effective budget. It is omitted for no-web runs. Provider credentials must not
be mounted into the agent container or written to run artifacts.

ChatGPT access uses a read-only temporary access file mounted only into the
gateway. The caller owns its lifetime; Dungeness does not log in or refresh it.
Every submitted command sees only gateway URLs and a placeholder token.

### Gateway implementation layout

The gateway is split by responsibility while keeping `gateway.py` as the
stable executable and import surface:

```text
services/gateway/
├── gateway.py          # stable entrypoint, HTTP routes, middleware, lifecycle
├── gateway_runtime.py  # run-scoped web and model request orchestration
├── gateway_models.py   # provider definitions and protocol/usage parsing
├── gateway_auth.py     # provider-neutral trusted credential recipes
├── gateway_pricing.py  # trusted pricing policy and request-cost calculation
├── gateway_usage.py    # canonical events, budgets, metrics, operational logs
└── gateway_web.py      # historical-source policy and Exa request validation
```

The implementation modules do not import `gateway.py`; dependency flow remains
toward the entrypoint, which avoids circular imports and keeps protocol, policy,
accounting, and request orchestration independently testable.

## Web interface

The gateway exposes a small HTTP interface:

```text
POST /web/search
POST /web/fetch
```

Example search request:

```json
{
  "query": "compact world map contact graph construction"
}
```

Example fetch request:

```json
{
  "url": "https://example.com/paper"
}
```

Both operations are implemented through Exa. For `fetch`, Exa retrieves the
requested page; the gateway does not connect directly to the page's host.

Historical checkpoint runs use a fail-closed policy:

- Exa's `endPublishedDate` is sent as a provider-side filter.
- The gateway independently requires verified publication metadata.
- Missing, invalid, or post-cutoff dates are rejected before the agent sees the
  result.
- Known mutable source-control URLs, including repository roots and refs such
  as GitHub `main`, are rejected. Full commit-addressed URLs are eligible.
- Dated pages whose exact representation is not immutable are metadata-only;
  content-bearing fields such as highlights, text, summaries, and extracted
  entities are removed before the result reaches the agent.
- Fetch is permitted only for a result approved by an earlier search, and the
  URL must pin immutable content, such as a full Git commit or an archival
  snapshot at or before the cutoff. Returned metadata is validated again.
- Rejection reasons are written as `web.rejection` records in
  `usage/events.jsonl`; rejected
  titles, highlights, and contents are not returned to the agent.

Exa's crawl-date filter is deprecated and ignored, so Dungeness does not rely on
it. `maxAgeHours: -1` prevents a live crawl during a run but is not treated as a
historical snapshot guarantee. Broader access to mutable or undated sources
requires future source-specific snapshot resolvers, such as commit-pinned Git
content or an archival web snapshot at or before the cutoff.

The agent image contains a standard client owned by the agent integration:

```bash
web search "<query>"
web fetch "<url>"
```

The client calls the fixed gateway address:

```text
http://gateway:8080
```

The testbed adds a short generated notice to the agent instruction explaining
that direct internet is unavailable and the `web` command is available.
The instruction is for discoverability only; Docker networking enforces the
restriction.

Custom agents may execute the same command or call the HTTP endpoints
directly. MCP is not required. An MCP facade can be added later without changing
the underlying search and fetch implementation.

## Model interface

The gateway exposes a provider-compatible model endpoint. The agent adapter
changes the model client's base URL to the gateway.

For an OpenAI-compatible client:

```text
OPENAI_BASE_URL=http://gateway:8080/model/openai/v1
OPENAI_API_KEY=testbed
```

`OPENAI_API_KEY=testbed` is only a placeholder for clients that require a value.
The real provider key exists only inside the gateway.

Harnesses can use the Responses contract on fixed provider routes:

```text
/model/openrouter/v1/responses  OpenRouter API key held by the gateway
/model/chatgpt/v1/responses     ChatGPT access held by the gateway
```

Moonshot and Kimi Code expose only `/model/<provider>/v1/chat/completions`.
The gateway forwards native requests and responses and accounts for reported
usage. Harnesses own any protocol conversion; the legacy gateway adapter and
its bundled Codex/Kimi presets have been removed.

For streaming Responses API calls, the gateway forwards SSE chunks as they
arrive. It retains a request-local in-memory copy so it can extract
provider-reported usage from the final event and write the run accounting
record after the stream closes.

Additional provider-compatible routes may be added when an agent requires
them, for example:

```text
/model/anthropic/v1
```

The gateway forwards only supported model API routes. It cannot forward an
arbitrary URL supplied by the agent.

The gateway validates the declared model, usage-compatible request fields and
locally executed tools before forwarding. Provider-hosted tools and unknown
fields are rejected by the [request policy](../docs/gateway-request-policy.md).
The harness owns CLI configuration and API compatibility.

## Usage and budgets

The gateway records all run events in one ordered stream:

```text
runs/<namespace>/<run-id>/usage/
├── events.jsonl
└── summary.json
```

Each event records a source, semantic kind, run-local sequence,
`observed_at`, `recorded_at`, and kind-specific `data`. A web accounting event,
for example, includes the bounded search query or fetch URL:

```json
{
  "schema_version": 1,
  "run_id": "world-map-local",
  "sequence": 17,
  "source": "gateway",
  "kind": "web.accounting",
  "observed_at": "2026-09-05T01:02:03.456Z",
  "recorded_at": "2026-09-05T01:02:03.456Z",
  "data": {
    "operation": "search",
    "query": "Cuccaro adder Toffoli count reversible",
    "duration_ms": 420,
    "status": "success"
  }
}
```

Trusted sidecars normally POST to the gateway's authenticated internal
collector. If delivery fails after completing an action, they append the same
schema under a file lock with `sequence: null`; fallback writes are idempotent
by `(source, event_id)`.

A `model.accounting` event records provider-reported token usage when
available. An `evaluation.completed` event includes a cumulative `usage`
snapshot, so score-versus-cost trajectories require no timestamp join:

```json
{
  "schema_version": 1,
  "run_id": "world-map-local",
  "sequence": 18,
  "source": "gateway",
  "kind": "model.accounting",
  "observed_at": "2026-09-05T01:02:04.000Z",
  "recorded_at": "2026-09-05T01:02:04.000Z",
  "data": {
    "provider": "openai",
    "model": "<model-id>",
    "input_tokens": 12000,
    "cached_input_tokens": 8000,
    "cache_write_input_tokens": 1000,
    "output_tokens": 1500,
    "reasoning_tokens": 700,
    "total_tokens": 14200,
    "normalized_usd": 0.082,
    "billed_usd": 0.082,
    "pricing_tier": "base",
    "status": "success"
  }
}
```

For subscription traffic, `normalized_usd` uses the same trusted reference
prices as comparable API traffic while `billed_usd` is `null`.

The gateway creates `summary.json` when it starts and atomically refreshes it
whenever a budget counter, token total, or cost changes. During shutdown it
waits for detached model-response drains before writing the final summary, so an
agent timeout cannot leave an otherwise completed run without an accounting
record.

Before forwarding a request, the gateway checks whether its request budget has
been exhausted. It updates provider-reported token totals after each model
response and rejects new requests after a hard limit is reached. The gateway
normalizes ordinary input, cache reads, cache writes, output, and reasoning
subsets. Cost-proxy token weights come from the active trusted pricing tier:
cache reads are discounted and cache writes can carry a premium. Exact USD
accounting independently prices all input buckets and applies any full-request
long-context tier. Reasoning tokens remain a reported subset of output tokens
and are never charged twice.

Failed requests, timeouts, and retries are recorded. Usage files are audit data
and are not continuation artifacts by default.

The server also emits redaction-safe JSON operational events to stderr and
exposes Prometheus-compatible process metrics at `GET /metrics`. Every HTTP
response includes an `x-request-id`; the same identifier correlates HTTP,
provider, and usage events. Metric labels and the operational stderr event
stream must never contain prompts, search queries, fetched URLs, response
bodies, authorization headers, or provider credentials. The per-run web usage
events in `events.jsonl` are the one exception: they record the search query and
fetched URL so a reviewer can see what the agent researched. They still never
record authorization headers or provider credentials.

## Agent integration

The agent adapter has three responsibilities:

1. materialize the pinned research-agent executable in the agent image;
2. point the agent's model client at the gateway; and
3. ensure the `web` command is available to the agent.

No gateway endpoint belongs in a problem definition. Problems define what to
solve, the initial state, candidate artifacts, and verification. Gateway wiring
belongs to the testbed runtime and agent adapter.

An installed agent runs inside the agent container and uses both gateway
interfaces directly. An external agent may call the model gateway from the
testbed control plane, but that requires making the per-run gateway reachable
from the control plane. The first implementation should prefer installed
agents.

## Harbor integration

The temporary Harbor environment uses Docker Compose for the agent and gateway.
The clean verifier remains a separate Harbor verifier environment. The render
lives under the OS temporary directory during execution; `--keep-render` moves
it under the run for debugging:

```text
runs/<namespace>/<run-id>/debug/harbor-task/
├── harbor-job.yaml
├── task.toml
├── instruction.md
├── environment/
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── gateway/
│   └── web_client.py
└── tests/
    ├── Dockerfile
    └── test.sh
```

Harbor is responsible for:

- starting and stopping the containers;
- sandbox resource and time limits;
- the effective network boundary;
- transferring approved candidate artifacts; and
- running the separate verifier.

The gateway is responsible for:

- Exa and model-provider access;
- provider credential isolation;
- web and token accounting; and
- per-run budget enforcement.

## Minimum completion criteria

The MVP is complete when one installed agent can:

1. call its model through the gateway;
2. run `web search` and `web fetch`;
3. fail to reach any other internet host;
4. stop receiving gateway service after exceeding a configured budget;
5. produce per-run model and web usage logs; and
6. submit its candidate to a separate no-network verifier.
