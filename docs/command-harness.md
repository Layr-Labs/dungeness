# Command harnesses

`dungeness-command-v1` runs arbitrary installed software inside Harbor's
container through a trusted adapter. The harness does not choose a host Python
import, and cannot select a built-in agent. This is the only supported execution path.
Research strategy, memory and completion decisions belong to the harness.
The former `research_state` controller is removed; old specs that request it
fail explicitly, as do run-spec evaluation and web-research strategy profiles.
External web search and fetch are disabled. Omitted settings and legacy
`web_search.mode: optional` both resolve to `disabled`; assigned problem resources
remain available through the internal problem service.
Historical experiments must use their original revision.

An agent descriptor has the ordinary identity fields, `execution_mode: installed`,
a Dockerfile, and:

```yaml
execution:
  interface: dungeness-command-v1
  entrypoint: ["python3", "/opt/harness/agent.py"]
```

The Dockerfile needs Python 3 for the runner. Install all dependencies at build
time; the execution container has no direct internet route.

Bundle papers, local databases, indexes and retrieval software in the harness
image, using any layout or file format your agent supports. Dungeness does not
create a knowledge service, inject retrieval instructions or intercept file
reads. Child processes can provide the agent's own local services. Remove the
old `initialization.knowledge_base` option.

The run-spec selects access independently of the harness:

```yaml
model_access:
  models:
    - provider: openai
      upstream_id: openai/gpt-6-astra
      request_model: gpt-6-astra
      api: openai-responses
      name_format: request
  max_parallel_requests: 4
  request_reservation_usd: 0.5
```

All models require entries in the trusted pricing schedule. Credentials come
from the operator's environment file using `TESTBED_<PROVIDER>_API_KEY`.
ChatGPT instead uses `DUNGENESS_CODEX_AUTH_FILE`, pointing to a private temporary
file with `tokens.access_token` and `tokens.account_id`. Mount that file only
into the gateway; no native credentials or refresh proxy are supplied to a
command harness. The caller owns credential lifetime and cleanup.

The pricing schedule is runtime data, not a source-code model whitelist.
An enclosing service such as Catalyst can install a frozen, authenticated
catalog snapshot into the isolated runtime's `services/gateway/pricing.yaml`
before compiling a run. The same snapshot is used by the compiler, gateway
and downstream verifier. Submitted agents cannot set their own rates.

Kimi Code and direct Moonshot routes are retired. Harnesses own any protocol
conversion; the gateway forwards supported native requests and meters usage.
Agents can use SDKs directly without a Codex dependency.
Streaming chat requests always ask for usage. When a pricing entry declares
`text_only: true`, non-text inputs/outputs are rejected and reference costs
are never presented as actual billed dollars.
Command runs reject undeclared model fallbacks, asynchronous background
inference, paid provider tools and service-tier overrides whose costs cannot
be established by the request's token ledger. Harness-executed function and
custom tools remain available. The
[gateway request policy](gateway-request-policy.md) applies to every command
harness: only reviewed request fields and harness-executed
tools are accepted, independently of the run's web-access setting. OpenRouter
additionally requires the trusted operator to disable account-default server
tools/plugins and set `TESTBED_OPENROUTER_INFERENCE_ONLY=1`.

`DUNGENESS_TASK` names the JSON task file. It contains `instruction`, `workspace`,
`models` (including gateway `base_url`), and `resume`. Subagents may be ordinary
processes or threads inside the same container. All model traffic shares the
gateway allowlist, budget and concurrency envelope.

`evaluate --json PATH` prints the existing sidecar's structured response. Each
call uploads candidate bytes; workers need not overwrite one shared path.
Evaluation concurrency is controlled by the challenge-owned sidecar.
The evaluator and gateway logs are the authoritative evidence, not harness logs.

The runner terminates remaining process-group children on exit and forwards
termination signals. Container teardown handles detached processes. An optional
`execution.resume_entrypoint` is selected after exit code 75 when the run has
remaining `runtime.continuation.max_resumes` and time. Normal nonzero exits fail.
No automatic host-failure recovery is implied.

Credit reservations bound admission while responses are in flight and are
released only after upstream draining/accounting. They are not enforceable
provider billing limits. Calls can cost more than their allowance; actual usage
controls subsequent admission, and missing usage stops it. A consuming benchmark
must reject over-cap or incomplete evidence. Strict dollar caps require further
provider-specific request bounds or provider-side limits.

## Migrating bundled agents

The bundled Codex, Claude Code, Pi and Prime Agent presets, native launchers,
CLI login helper and OAuth refresh proxy are removed. Package your preferred
agent in the submitted Docker image and launch it from `execution.entrypoint`.
Set CLI options, reasoning settings and protocol compatibility inside the harness;
run-level native `agent_options` are rejected. To resume, implement
`execution.resume_entrypoint` and retain session state inside the container.

Catalyst's `catalyst-exec-v1` submission contract is unchanged. Its public CLI
accepts a Dockerfile and entrypoint and installs the trusted command adapter.
The `agents/projects/dungeness/command` example is only a no-model smoke command.
Historical bundled-agent experiments require their original runtime revision.
