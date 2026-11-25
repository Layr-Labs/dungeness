# Runtime compatibility contract

`runtime-contract.json` is the public capability declaration for a pinned
Dungeness runtime. Consumers may read it directly without importing internal
modules or starting a gateway. `./dungeness capabilities` prints the same JSON.
It requires no credentials, Docker daemon, user configuration or model calls.

The declaration has `schema_version: 1`, `runtime: "dungeness"`, and a list of
versioned capability names. Consumers reject unsupported schema versions and
missing required capabilities. They may ignore additional fields and unknown
capabilities. Breaking a capability's semantics requires a new capability name;
additive changes do not require an envelope version change.

| Capability | Guaranteed behavior |
| --- | --- |
| `command-harness-v1` | A `dungeness-command-v1` agent executes its entrypoint in the sandbox; submitted code cannot select host Python imports. |
| `run-model-access-v1` | The run spec selects the permitted model set and gateway request reservation/concurrency policy. |
| `priced-model-requests-v1` | Requests are validated against declared models and trusted price configuration. |
| `bounded-model-admission-v1` | Trusted runs may enable conservative per-request output/token/USD reservations; requests cannot override this policy. |
| `cache-duration-accounting-v1` | Native Messages usage distinguishes five-minute and one-hour cache writes; missing duration evidence blocks settlement. |
| `command-exit-status-v1` | The command adapter uses Harbor's `return_code`; unsuccessful harness exits cannot silently become success. |
| `rejected-request-accounting-v1` | Recognized pre-generation rejection responses settle with zero tokens and release credit reservations; ambiguous failures are not treated as free success. |
| `assigned-problem-service-v1` | A pinned read-only task service and declared attachments/resources are accessible through the gateway; attachment integrity and path constraints are checked during compilation. |
| `optional-model-token-limit-v1` | An explicit null model-token cap disables that ceiling while preserving USD and execution limits and token accounting. |
| `declarative-scaffolds-v2` | Trusted schema-v2 scaffolds declare candidate files, support files and checked text edits without problem-specific compiler code or executable host hooks. |
| `model-provider-registry-v1` | `dungeness providers` reports access-route IDs from the gateway's actual registry, including trusted runtime extensions, without credentials or model calls. The command and capability names remain unchanged. |
| `model-credential-inputs-v1` | `dungeness providers --details` describes credential inputs from the registry; `dungeness.credential_access` describes and stages explicit inputs privately. Newly compiled runs include managed file-credential snapshots and cleanup. |

This declaration is a compatibility interface, not a security attestation.
Consumers must still select a trusted runtime revision and verify that the
checkout matches their pin. It must never be loaded from a submitted harness.
The capability file is committed and included in runtime exports. Existing
run-spec, command-agent, gateway and record schemas remain unchanged.

`./dungeness providers` returns `{"schema_version": 1, "runtime": "dungeness",
"providers": [...]}`. The historical `providers` field contains access-route IDs;
see [model-access terms](model-access.md). Consumers use it to check route availability for their
selected runtime instead of maintaining a second allowlist. It describes
implemented routes, not credential validity, model prices or operator-dependent
features such as OpenRouter inference-only routing. Configure extensions only
in the trusted runtime; harnesses must not supply or replace that registry.

With `--details`, the same envelope adds `access_routes`: a list of objects with
`id`, `upstream`, `operations` and `credential_inputs`. Input descriptions have
`schema_version: 1`, `environment` (gateway field to host input name), and `files`
(host input name to `gateway_env`, `mount_path` and selected JSON `paths`).
No source-file paths, credentials or current account state are discovered.
See the [integration guide](integrating-model-access.md) for the Python interface,
mounting, lifetime and failure behavior. The compiler's
`x-dungeness-credential-files` metadata is additive; existing
`x-dungeness-credential-env` selectors and gateway paths are preserved.

## OpenRSI migration

See [migration notes](migration.md) for upgrade steps and retired interfaces.

The former `ecdsa-readable-verifier-results-v1` capability was retired when the
verifier moved to OpenRSI. Its readability guarantee is tested with that package.
Update the OpenRSI adapter together with a runtime that no longer declares it.

OpenRSI reads this contract through `openrsi_space.runtime_contract`. Older pinned
runtimes without the file temporarily use the existing source-marker checks,
isolated in `openrsi_space._legacy_dungeness`. A present but malformed or incomplete
declaration fails; it never falls back to those checks. No new capability may be
added to the legacy bridge. Remove it after supported deployments have moved to
contract-bearing pins.

The compatibility declaration allows internal modules to move, but it does not
remove other integration boundaries. OpenRSI still writes record collections
and uses the Dungeness CLI. Its real compiler contract tests also exercise
internal compiler helpers. Coordinate those tests and any explicit file/CLI
interface changes when extracting modules.

## Verification

Core tests cover command execution, model policy, token limits, scaffold/task
materialization. Challenge-owned tests cover readable verifier output. Gateway
tests cover request validation, rejected-request accounting and assigned resources. The dedicated
Harbor environment checks the adapter against the real pinned Harbor API.
See [development checks](development.md).

Before changing this contract or runtime layout, also run OpenRSI's real
compiler tests against a clean commit of the candidate runtime. From the verifier
checkout, with its dependencies installed:

```sh
OPENRSI_DUNGENESS=/path/to/clean/dungeness \
PYTHONPATH=src:/path/to/openrsi-space/src \
python -m unittest discover -s tests -p test_dungeness_contract.py
```

Those tests compile synthetic inputs without Docker, credentials or paid model
calls. They complement rather than replace a container execution smoke test
when the execution, isolation or rendering boundaries change.
