# Runtime distribution and research history

The maintained runtime consists of the CLI/compiler, trusted gateway and
services, Harbor adapters, shared agent/task definitions and policies.
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
personal tasks/run specs, experiments, reports, Git history and tests. It
rejects symlinks and LFS pointers in the selected runtime. It refuses to replace
an existing archive.

`RUNTIME_SOURCE.json` records the source commit and SHA-256 of each bundled
file. The command prints the archive digest. The same revision produces
identical archive bytes.

This creates an internal source distribution. It neither publishes a package
nor changes repository access. A third-party installer requires a separately
approved distribution location and access/license policy. Catalyst solvers
can submit remotely without installing Dungeness.

## Install an authorized bundle

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
The runtime, watcher, `evals`, `verify`, continuation and cleanup commands still
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
launch the removed controller. Knowledge-base retrieval and its direct-read
hook remain independent of that controller.
