# Runtime distribution and research history

The maintained runtime consists of the CLI/compiler, trusted gateway and
services, Harbor adapters, the generic command-agent example and policies.
Challenge-owned tasks, verifiers, checkpoints and scaffolds must be installed
separately; the default source bundle does not contain a benchmark.
Personal run specs, knowledge bases, experiment reports and recorded outputs
are research material, not installation dependencies.

## Build a source bundle

After committing and testing the intended revision:

```sh
python3 script/export_runtime.py --revision HEAD \
  --output /tmp/dungeness-runtime.tar.gz
```

The exporter reads **only the selected Git commit**, never local credentials or
uncommitted files. Its allowlist excludes `runs/`, personal knowledge bases,
personal run specs, experiments, reports, Git history and tests. No personal
task directories are included. Catalyst generates its task and checkpoint from
its own trusted problem package. The exporter rejects symlinks and LFS pointers in the selected runtime. It refuses to replace
an existing archive.

`RUNTIME_SOURCE.json` records the source commit and SHA-256 of each bundled
file. The command prints the archive digest. The same revision produces
identical archive bytes.

The bundle is source for running Dungeness locally; it is not an official
Catalyst evaluation or a hosted service. It contains no provider credentials.

The optional local transcript viewer is excluded by default. Include it with
`--include-transcript-tools` when needed; full checkouts have it under
`tools/transcripts/`. The CLI prints its launch command only when installed.

## Install a bundle

Verify its digest against the trusted release record, then:

```sh
tar -xzf dungeness-runtime.tar.gz
cd dungeness-runtime
git init
git add .
git commit -m "Install Dungeness runtime"
./dungeness --help
```

Git, uv, uvx and Docker remain prerequisites. Initialize the local Git tree
because execution records require committed inputs. Keep `RUNTIME_SOURCE.json`
to identify the upstream revision separately from local experiment commits.
Follow the [quick start](../README.md); model calls use the operator's account.
Checkpoint source access and image-build dependency downloads are still required.

## Local run output

The CLI creates `runs/<namespace>/<run-id>/` when needed. `runs/` is ignored
as a whole; execution outputs are no longer committed or uploaded through LFS.
The runtime, optional transcript tools, `evals`, `verify`, continuation and cleanup commands still
read locally retained runs. Removing tracked output does not disable them.

Commit reproducible inputs under `run-specs/`, `tasks/` and `agents/`. Retain
outputs in local or service artifact storage, and publish selected results through
the owning service. Tests create synthetic runs in temporary directories.

Reports, result charts and result tables are also excluded from the current
source tree and ignored for future commits. Store them with the corresponding
run artifacts.

This repository starts from a reviewed source snapshot with fresh history;
historical runs and reports are retained in the separate private research archive.
Authorized operators can recover an earlier run from that archive at its original
revision, including any required LFS objects. Do not merge or push archive branches
into this repository: doing so would reintroduce their historical records.

## Retired research-state experiments

The experimental research-state profiles, controller, prompt injection and
completion gates have been removed. Their recipes are no longer active run
specs. Recover them from the original source revision in the private research
archive; the cleanup also retained an external backup of the removed files.
The CLI and transcript viewer can still read historical records, but cannot
launch the removed controller. Knowledge-base services and read hooks are also
removed. Personal corpora and experiment recipes have been moved out of this tree.

## Research-strategy migration

Run-spec `evaluation` profiles and strategy-bearing `web_search.profile` values
are rejected before source checkout or model execution. Put evaluation cadence,
search planning and worker orchestration in the harness. The runtime reports
interfaces, budgets and deadlines without prescribing a research loop.

External web search and fetch are disabled. `web_search: {mode: disabled}` is
the effective setting; legacy `optional` requests also resolve to disabled.
Only the old `disabled-v1` and `optional-v1` profile references remain accepted
as compatibility aliases, without loading profile files. Disabled access still
zeros search and fetch budgets. Direct agent egress remains blocked.

The unused world-map development/holdout split evaluator is retired; tasks
requesting it fail explicitly. Full-benchmark verification is retained. The old
Dungeness-specific Yukon manifest, placeholder workflow and submission slot are
removed; Catalyst owns its Yukon integration.
