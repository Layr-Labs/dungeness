# Dungeness Roadmap

This file tracks the next implementation milestones. Items are ordered by
dependency: later catalog and experiment features should not be built on
incomplete run records.

## P0: Trustworthy Run Finalization

Make one run produce a complete and accurate canonical record.

- [x] Replace relative usage volume mounts with absolute paths under the
      namespace-organized run directory. Temporary Harbor rendering no longer
      changes where usage is written.
- [ ] Derive the final run state from Harbor trial results instead of treating a
      zero Harbor process exit code as a successful run.
- [ ] Record lifecycle, termination, and verification independently:
  - lifecycle: `running`, `finished`, or `cancelled`
  - termination: `completed`, `budget_exhausted`, `agent_error`, or
    `infrastructure_error`
  - verification: `passed`, `failed`, `unsupported`, or `not_run`
- [ ] Distinguish an intentional gateway budget rejection from a provider rate
      limit or agent failure.
- [ ] Document that a USD limit is checked between requests and may exceed the
      configured value by the cost of the final in-flight request, or implement
      request-level reservation for a hard ceiling.
- [x] Add an experimental Codex subscription profile with read-only temporary
      authentication, gateway accounting, auth-refresh-only egress, and
      normalized USD limits.
- [ ] Run a no-spend or minimal compatibility smoke test for subscription
      authentication, ChatGPT header compatibility, token capture, and budget
      interruption before including it in a paid experiment.
- [ ] Ingest gateway usage, evaluation summaries, Harbor exceptions, and clean
      verifier metrics into `record.json`.
- [ ] Detect unsupported clean-verifier platforms before Harbor execution.
      Record macOS verification as `unsupported` instead of reporting a
      misleading completed or failed trial.
- [ ] Return a useful CLI exit status and summary containing the run ID,
      termination reason, spend, best evaluation, and verification result.
- [ ] Run a one-dollar Codex smoke test and inspect the complete record.

Acceptance criteria:

- `record.json` never says a run succeeded when its only Harbor trial errored.
- Usage and evaluation files are present in the run directory.
- Budget exhaustion is recognizable without parsing agent logs.
- Verification status and score are explicit.
- The same finalization behavior is covered by focused tests.

## P1: Codex Subscription Effort Experiment

Use multiple real runs to validate Dungeness as a research system, not only as
an execution wrapper.

Question:

> At the public challenge-start checkpoint, how does requested Codex reasoning
> effort affect verified relative improvement under a fixed twelve-dollar
> normalized model budget?

- [ ] Complete the minimum P0 fixes needed for trustworthy records.
- [ ] Run one no-spend request-shape smoke test and one low-budget live
      subscription smoke test before launching the matrix.
- [x] Author the experiment design at
      `experiments/users/bx/ecdsa-codex-openai-subscription-effort-sweep-62ae3d0-12usd/experiment.yaml`.
- [ ] Review the four-effort matrix and obtain explicit approval before
      consuming the nominal `$48` normalized budget plus
      possible final-request overrun.
- [x] Materialize the four run specs under
      `run-specs/users/bx/ecdsa-codex-openai-subscription-effort-sweep-62ae3d0-12usd/` and reference
      them from the experiment.
- [x] Keep the hypothesis, estimands, and limitations in the related
      `claim.yaml`.
- [x] Add `dungeness experiment create` and `dungeness experiment run` as a
      thin orchestration layer over ordinary run specs.
- [ ] Execute the four run specs with the experiment labels attached to every
      run.
- [ ] Verify on Linux when available; otherwise record verification as
      `unsupported` rather than treating it as a research failure.
- [ ] Attach completed run references and analysis artifacts to the experiment
      without requiring a fixed `result.json` format.
- [ ] Compare termination reason, actual spend, evaluation count, best score,
      final verification, and candidate-artifact digest across matrix cells.
- [ ] Write a short conclusion covering both research variance and failures in
      Dungeness itself.

Acceptance criteria:

- All 12 planned runs have complete canonical records, or each missing cell has
  an explicit failure or cancellation reason.
- The experiment can be understood without reading Harbor's directory layout.
- The conclusion clearly separates agent behavior from infrastructure errors.
- Raw scores are not pooled across checkpoints; comparisons use checkpoint
  baselines and normalized improvement.
- The sweep identifies which additional experiment abstractions are justified
  by real usage beyond the initial sequential executor.

## P2: Canonical Run Artifacts

Remove the need for callers to understand Harbor's nested result layout.

- [ ] Write `runs/<namespace>/<run-id>/artifacts/manifest.json`.
- [ ] Record the final candidate, agent transcript, evaluation events, and
      relevant logs with stable paths and content hashes.
- [ ] Relate every artifact to its producing run and source checkpoint.
- [ ] Keep Harbor output as execution evidence, but make the Dungeness artifact
      manifest the stable retrieval interface.
- [ ] Make `--resume-from` consume canonical artifact metadata instead of
      traversing Harbor internals.

## P3: Local Run Discovery

Provide useful discovery before introducing a database.

- [ ] Add `dungeness list runs`.
- [ ] Add `dungeness show run <run-id>`.
- [ ] Add `dungeness search runs` with namespace, label, agent, checkpoint,
      status, metric, and time filters.
- [ ] Scan canonical JSON records initially; keep any future index derived and
      rebuildable.
- [ ] Define how older record schema versions are read or migrated.

## P4: Artifact Search and Knowledge Cutoffs

Allow people and research agents to discover prior outputs safely.

- [ ] Promote selected run outputs to first-class `artifact` records.
- [ ] Support namespace, label, relation, and timestamp filters.
- [ ] Record both creation and publication time where known.
- [ ] Add artifact search and retrieval routes to the trusted gateway. Research
      agents must not receive direct mounts of other runs or the artifact store.
- [ ] Require every run spec to declare the artifact access mode and view
      available to its agent, including explicit `none` and unrestricted modes.
- [ ] Support run-spec include and exclude rules using namespace, type, labels,
      relations, and cutoff time.
- [ ] Resolve and snapshot that view at run start.
- [ ] Apply cutoff and visibility filtering before search, ranking, result
      counts, and retrieval.
- [ ] Enforce the same resolved policy when retrieving an artifact returned by
      search.
- [ ] Record artifact searches, retrievals, and the resolved access snapshot in
      the run record.
- [ ] Add full-text search only after structured filtering works.
- [ ] Add embeddings only if real discovery queries require them.

> **Design principle:** Dungeness enforces the access view declared by the run
> spec. It does not decide whether access to another agent's work is "cheating."
> That is an experimental-design decision made by the run-spec author. Fair
> comparisons require researchers to inspect and compare the recorded access
> policies.

## P4a: Historical Web Snapshot Coverage

Extend strict cutoff enforcement without returning to provider-trust or
fail-open behavior.

- [x] Reject missing, invalid, and post-cutoff publication metadata.
- [x] Reject known mutable source-control URLs and revalidate fetch responses.
- [x] Stop relying on Exa's deprecated crawl-date filter.
- [ ] Resolve GitHub results to full commit-addressed URLs whose public
      availability is established at or before the cutoff.
- [ ] Resolve academic sources to immutable document versions and revision
      dates.
- [ ] Add archival-web snapshot retrieval at or before the cutoff.
- [ ] Bind fetch authorization to an immutable version and content digest.

## P5: Publishing and Continuation

Make useful results reusable across users and machines.

- [ ] Publish a selected run artifact as an immutable checkpoint or source
      snapshot.
- [ ] Preserve `produced_by`, parent checkpoint, and derivation relations.
- [ ] Allow another run to start from a published checkpoint by qualified
      reference.
- [ ] Define portable export and import without coupling it to Harbor paths.

## P6: Experiment Infrastructure

Reserve experiments for multi-run research design and analysis.

- [ ] Represent a question or hypothesis, controlled variables, independent
      variables, repetitions, and referenced run specs.
- [ ] Link resolved runs and arbitrary result or conclusion artifacts.
- [ ] Do not require a fixed `result.json` or conclusion format.
- [ ] Add execution, upload, and publication only after run and artifact
      records are stable.
