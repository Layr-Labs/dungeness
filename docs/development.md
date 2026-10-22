# Development

Use uv and Python 3.11 or 3.12 for the core/gateway checks. The root
`pyproject.toml` and `uv.lock` define reproducible development dependencies.
Run all checks from the repository root with `make check`. The two component
commands are `make check-core` and `make check-harbor`. The core command runs:

```sh
uv run --locked --group gateway python script/check.py
```

This runs core, gateway and transcript suites in separate interpreters. It does
not start Docker or call model providers. It checks that the gateway container's
requirements match the pinned development requirements. Change both declarations
and regenerate `uv.lock` when deliberately updating gateway dependencies.

The core suite skips one Harbor adapter test when Harbor is absent. Run that
contract separately on Python 3.12:

```sh
uv run --isolated --locked --python 3.12 --group harbor python script/check.py --harbor-only
```

Gateway and Harbor dependency groups are intentionally mutually exclusive:
the pinned Harbor needs a different Uvicorn version than the gateway. They run
in separate environments in production as well. The Harbor check fails if its
dependency is unavailable; it does not silently skip. CI runs both commands.

This is currently a source-checkout runtime. The project manifest does not
provide a wheel or console entrypoint: installed assets and workspace paths
must be separated before claiming that packaging contract.

## Boundaries during cleanup

The first execution extraction lives in `src/dungeness/execution/harbor.py`.
It owns Harbor job/task rendering, the pinned launch command, control-plane
environment preparation, trusted-adapter validation and result interpretation.
It accepts validated inputs and explicit paths; importing it does not load the
compiler, gateway or Harbor SDK. The SDK-dependent `CommandAgent` remains at
`adapters/harbor/command_agent.py` to preserve the job's trusted import path.
The compiler and CLI retain compatibility imports for existing callers.

Run orchestration now lives in `execution/runner.py`: rendering, launch, outcome
handling, record finalization and render retention/disposal. It takes explicit
paths, a renderer command and retention settings; it does not resolve CLI flags
or load run specs. Record persistence is supplied through two typed callbacks,
so the runner does not import the CLI or own the record schema.

`records.py` owns atomic JSON persistence, Git provenance and run-record
initialization/finalization, including read-only historical evidence compatibility.
It receives an explicit storage root, launcher metadata and an execution-result
interpreter. It imports neither execution nor the compiler/gateway. The CLI
supplies the Harbor interpreter and retains its existing helper entry points.

`execution/environments.py` owns run-scoped Docker discovery and teardown;
the CLI's administrative `clean` command uses those same operations.
`execution/process.py` streams subprocess output and reaps interrupted children
before teardown. Children remain in the caller's process group so Catalyst's
group cancellation continues to reach them. Termination gets a ten-second grace
period before killing an unresponsive child. Cleanup attempts all stages even
when record finalization fails, and secondary errors do not replace the original
execution failure or cancellation.

Configuration resolution, record lookup and standalone verification still
live in the root CLI. Model policy/accounting stays in the gateway; task
validation and generic compilation remain in the compiler.

`scaffolds.py` materializes schema-v2 scaffold manifests using explicit file
mappings and text edits that must match an expected number of times. It knows
no language filenames or problem-specific validation stages. Catalyst owns its
ECDSA scaffold and verifier bundles under `src/catalyst/problem-set/ecdsa-fail/`
and installs them into the disposable runtime. Candidate files and trusted edits remain separate;
submitted harnesses cannot choose the manifest or load preparation code.
See [trusted scaffolds](scaffolds.md).

The current extraction order is:

1. Establish reproducible checks and a [public runtime contract](runtime-contract.md).
2. Retire only features whose removal has been explicitly agreed.
3. Separate configuration/records, compilation, execution and gateway ownership.
4. Move problem-specific preparation out of the generic compiler.
5. Separate installed assets from mutable run workspaces and finish packaging.

Keep CLI commands, record collection paths, schemas and execution behavior
stable during module extraction. Configuration and record modules must not start
services or import container orchestration. Compilation should produce an
execution plan; the execution adapter owns launching and cleanup. The gateway
owns model policy and accounting. Problem preparation and grading belong to
trusted problem implementations. Submitted harnesses must never select Python
modules imported on the host.

Preserve the behavioral tests when moving code. Where a feature is deliberately
retired, test explicit rejection rather than silently ignoring its old settings.
Update exports, documentation links and Catalyst consumer tests with each
affected boundary. Changes to model credentials, accounting, isolation or
candidate verification need their own focused validation.

Compiler and record tests use a disposable runtime populated from synthetic
records under `tests/fixtures/runtime/`. Challenge grader tests live with the
Catalyst problem assets. No Dungeness check requires a Catalyst checkout.
