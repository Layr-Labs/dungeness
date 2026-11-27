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

The core suite skips the Harbor adapter tests when Harbor is absent. Run them
separately on Python 3.12:

```sh
uv run --isolated --locked --python 3.12 --group harbor python script/check.py --harbor-only
```

Gateway and Harbor dependency groups are intentionally mutually exclusive:
the pinned Harbor needs a different Uvicorn version than the gateway. They run
in separate environments in production as well. The Harbor check fails if its
dependency is unavailable; it does not silently skip. CI runs both commands.

When `UV_OFFLINE=1` is set and the checkout contains `uv.lock`,
`dungeness run` launches Harbor with the locked `harbor` dependency group.
With network access and `UV_OFFLINE` unset, warm the cache once from the
repository root using the Python version and cache directory for the offline run.

```sh
uv run --isolated --locked --python 3.12 --group harbor harbor --version
```

An earlier online run through `uvx` can leave different dependency versions
in the cache.

This warms the cache without changing the checkout's `.venv`. The CLI's
shebang resolves script dependencies using package index metadata, which may
be absent from the offline cache. Start offline runs with the project lock:

```sh
UV_OFFLINE=1 uv run --isolated --locked --python 3.12 python dungeness run …
```

This is currently a source-checkout runtime. The project manifest does not
provide a wheel or console entrypoint: installed assets and workspace paths
must be separated before claiming that packaging contract.

## Component ownership

Harbor integration lives in `src/dungeness/execution/harbor.py`.
It owns Harbor job/task rendering, the pinned launch command, control-plane
environment preparation, trusted-adapter validation and result interpretation.
It accepts validated inputs and explicit paths; importing it does not load the
compiler, gateway or Harbor SDK. The SDK-dependent `CommandAgent` remains at
`adapters/harbor/command_agent.py` to preserve the job's trusted import path.
The compiler and CLI retain compatibility imports for existing callers.

Run orchestration lives in `execution/runner.py`: rendering, launch, outcome
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
before teardown. Children remain in the caller's process group so OpenRSI's
group cancellation continues to reach them. Termination gets a ten-second grace
period before killing an unresponsive child. Cleanup attempts all stages even
when record finalization fails, and secondary errors do not replace the original
execution failure or cancellation.

Configuration resolution, record lookup and standalone verification still
live in the root CLI. Model policy/accounting stays in the gateway; task
validation and generic compilation remain in the compiler.

`scaffolds.py` materializes schema-v2 scaffold manifests using explicit file
mappings and text edits that must match an expected number of times. It knows
no language filenames or problem-specific validation stages. OpenRSI's
problem sources, scaffolds and verifier bundles live in
[openrsi-problems](https://github.com/Layr-Labs/openrsi-problems/tree/main/problems).
The platform installs the selected signed package into the disposable runtime.
Candidate files and trusted edits remain separate;
submitted harnesses cannot choose the manifest or load preparation code.
See [trusted scaffolds](scaffolds.md).

`credential_access.py` owns the trusted launcher's explicit credential preparation
API. `execution/credentials.py` adapts compiled Compose metadata and env-file
precedence to that API. Neither performs login, refresh or account discovery.
The shared `model_access.py` interface loads access routes and authentication
recipes from `services/gateway/model-access.json`; the gateway applies them to inference requests.
See [integration](integrating-model-access.md) before adding an access route.

## Making changes

1. Identify the owner of the behavior using the component boundaries above.
2. Add a focused regression for a changed execution or security contract.
3. Update the canonical guide and [migration notes](migration.md) if callers must adapt.
4. Run the applicable offline, container and consumer checks.
5. Treat consumer runtime pins and deployments as separate, qualified updates.

Keep CLI commands, record collection paths, schemas and execution behavior
stable during module extraction. Configuration and record modules must not start
services or import container orchestration. Compilation should produce an
execution plan; the execution adapter owns launching and cleanup. The gateway
owns model policy and accounting. Problem preparation and grading belong to
trusted problem implementations. Submitted harnesses must never select Python
modules imported on the host.

Preserve the behavioral tests when moving code. Where a feature is deliberately
retired, test explicit rejection rather than silently ignoring its old settings.
Update exports, documentation links and OpenRSI consumer tests with each
affected boundary. Changes to model credentials, accounting, isolation or
candidate verification need their own focused validation.

Compiler and record tests use a disposable runtime populated from synthetic
records under `tests/fixtures/runtime/`. Challenge grader tests live with the
OpenRSI problem assets. No Dungeness check requires an OpenRSI checkout.

Resume provenance hashes the copied candidate in the rendered workspace.
Single files retain SHA-256 of raw bytes. Directory hashes use SHA-256 of
`dungeness-resume-directory-v1\n` followed by compact ASCII JSON. Entries are
sorted by relative path components and contain `[path, "directory"]` or
`[path, "file", content_sha256, executable_boolean]`; the root itself is omitted.
This records empty directories and executable flags without depending on host
paths, timestamps, or ambiguous concatenations of names and file contents.

For network-policy changes, also run `make check-run-isolation` with Docker
access. It exercises two simultaneous runs with synthetic credentials; see
[per-run isolation](network-isolation.md). This is separate from the offline suite.

## Integration checks

`python3 script/check-gateway-isolation.py` requires Docker and exercises the gateway with
synthetic credentials and mock inference. `make check-run-isolation` tests two
simultaneous runs. Neither uses paid accounts. Test-only upstreams belong in a
synthetic trusted registry, never in a production endpoint override.

Before updating a platform's pin, run its real compiler contract tests against
a clean candidate commit and exercise its execution adapter with a synthetic
provider. See [runtime compatibility](runtime-contract.md#verification). Record
what was tested: offline compatibility, Docker execution and deployed service
qualification are distinct results.
