# Dungeness documentation

Dungeness runs a supplied harness against a supplied problem. The harness owns
the agent loop; the runtime owns execution, model mediation and evidence.

## Start here

| Your task | Read |
| --- | --- |
| Build or adapt a solver harness | [Integration guide](integrating-model-access.md), then [harness contract](command-harness.md). |
| Run Dungeness directly | [Operator quickstart](quick-start.md) and [CLI reference](cli-reference.md). |
| Integrate a manager or hosted worker | [Runtime contract](runtime-contract.md), [credential preparation](integrating-model-access.md#integrating-a-trusted-launcher), and [architecture](../DESIGN.md). |
| Upgrade an existing installation | [Migration and compatibility](migration.md). |
| Contribute to the runtime | [Development and checks](development.md). |

## Reference

| Area | Documents |
| --- | --- |
| Model access | [Terms](model-access.md), [authentication](gateway-authentication.md), [local account access](local-subscriptions.md). |
| Requests and failures | [Request policy](gateway-request-policy.md), [harness recovery](command-harness.md#required-request-error-handling), [transport diagnostics](model-failures.md). |
| Bundled model data | [GPT catalog](gpt-model-catalog.md), [Terra configuration](gpt-terra.md). These describe the pinned runtime, not live account entitlement. |
| Problems and evaluation | [Assigned resources](problem-service.md), [scaffolds](scaffolds.md), [evaluation events](evaluation-events.md). |
| Architecture | [Records and execution](../DESIGN.md), [gateway](../services/DESIGN.md), [network isolation](network-isolation.md). |
| Distribution | [Source bundles and retained outputs](runtime-distribution.md). |

Executable interfaces and current behavior are documented here. Retired behavior
is summarized in the migration guide; earlier implementations remain in Git
history. Platform setup, submission rules, Mac attestation and release approval
are owned by the relevant OpenRSI application, not this runtime.
