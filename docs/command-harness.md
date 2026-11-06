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

Harness authors and coding agents must implement
[request-error handling](#required-request-error-handling) in their model adapter
or CLI wrapper; a gateway error is not automatically feedback to the research model.

An agent descriptor has the ordinary identity fields, `execution_mode: installed`,
a Dockerfile, and:

```yaml
execution:
  interface: dungeness-command-v1
  entrypoint: ["python3", "/opt/harness/agent.py"]
```

The Dockerfile needs Python 3 for the runner. Install all dependencies at build
time; the execution container has no direct internet route. Each run uses
[isolated internal bridges](network-isolation.md), with no host bridge address.
Raw sockets, network administration and setuid/file-capability escalation are
unavailable; ordinary sockets, subprocesses and workspace writes remain supported.

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
An enclosing service such as OpenRSI can install a frozen, authenticated
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

## Required request-error handling

Read the [gateway recovery contract](gateway-request-policy.md#recovering-from-a-rejected-request)
when building or adapting a harness. Errors expose recovery fields under
`diagnostic` or, for provider and transport-bound errors, `error`:

| `run_action` | `retryable` | Required harness behavior |
| --- | --- | --- |
| `stop` | `false` | Stop model calls and preserve completed work and accounting. |
| `continue` | `true` | Retry with bounded backoff while the run's time and budget permit. |
| `continue` | `false` | Correct the request or choose another supported approach before continuing. Do not resend it unchanged. |

Inspect the stable error `code` and `action`; HTTP status or subprocess exit code
alone is insufficient. Retain safe diagnostics and the request ID. Do not treat
every HTTP 400 as the end of research or every HTTP 429/500 as retryable.
If an SDK or CLI exits on an API error, its wrapper must handle that outcome;
`run_action: continue` does not restart the process or deliver feedback to the model.
Use the framework's supported recovery interface. Do not fabricate successful
responses, alter retained evidence, or silently strip signed/encrypted history.
If recovery is not possible, report that limitation and preserve the best result.

The current gateway does not accept image inputs, including rendered PDF pages.
Local image processing and OCR inside the sandbox are allowed; send extracted
text instead. An image rejection follows the ordinary correctable-error path.

Before selecting the final candidate, collect outstanding evaluation results
within the remaining run time and choose the best verified candidate available.
Do not overwrite a newer verified improvement with an older checkpoint merely
because the model subprocess exited.

Test the actual adapter/wrapper offline with a rejected request followed by a
corrected successful request, bounded retries, a stop condition, and an evaluation
finishing after the model subprocess exits. A gateway-only mock does not prove
that an unmodified agent CLI or wrapper recovers.

## Migrating bundled agents

The bundled Codex, Claude Code, Pi and Prime Agent presets, native launchers,
CLI login helper and OAuth refresh proxy are removed. Package your preferred
agent in the submitted Docker image and launch it from `execution.entrypoint`.
Set CLI options, reasoning settings and protocol compatibility inside the harness;
run-level native `agent_options` are rejected. To resume, implement
`execution.resume_entrypoint` and retain session state inside the container.

OpenRSI's current submission interface is `openrsi-exec-v1`; its adapter also accepts historical harness manifests. Its public CLI
accepts a Dockerfile and entrypoint and installs the trusted command adapter.
The `agents/projects/dungeness/command` example is only a no-model smoke command.
Historical bundled-agent experiments require their original runtime revision.
