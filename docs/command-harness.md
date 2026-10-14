# Command harnesses

`dungeness-command-v1` runs arbitrary installed software inside Harbor's
container through a trusted adapter. The harness does not choose a host Python
import, and need not identify as Codex, Claude Code, Pi, or another built-in agent.
Existing agent descriptors retain their original behavior.

An agent descriptor has the ordinary identity fields, `execution_mode: installed`,
a Dockerfile, and:

```yaml
execution:
  interface: dungeness-command-v1
  entrypoint: ["python3", "/opt/harness/agent.py"]
```

The Dockerfile needs Python 3 for the runner. Install all dependencies at build
time; the execution container has no direct internet route.

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

Kimi Code and Moonshot accept ordinary OpenAI-compatible Chat Completions at
`/model/<provider>/v1/chat/completions`, in addition to the existing Responses
adapter. Agents can use SDKs directly without a Codex dependency.
Streaming chat requests always ask for usage. When a pricing entry declares
`text_only: true`, non-text inputs/outputs are rejected and reference costs
are never presented as actual billed dollars.
Command runs reject undeclared model fallbacks, asynchronous background
inference, paid provider tools and service-tier overrides whose costs cannot
be established by the request's token ledger. Harness-executed function and
custom tools remain available.

`DUNGENESS_TASK` names the JSON task file. It contains `instruction`, `workspace`,
`models` (including gateway `base_url`), and `resume`. Subagents may be ordinary
processes or threads inside the same container. All model traffic shares the
gateway allowlist, budget and concurrency envelope.

`evaluate --json PATH` prints the existing sidecar's structured response. Each
call uploads candidate bytes; workers need not overwrite one shared path.
ECDSA verification is serialized while model work may proceed concurrently.
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
