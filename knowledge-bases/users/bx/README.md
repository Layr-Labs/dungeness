# Knowledge-base provenance and contamination status

Last audited: 2026-09-11.

This file records whether each knowledge base is suitable for a
leakage-controlled experiment. For this audit, **any information about the
ECDSA Fail repository makes a processed knowledge base contaminated**. This
includes the task ABI or equations, score contract, verifier behavior,
implementation structure, baseline/current architecture, or prior-run
results. It does not matter whether the repository information is public or
whether it came from a successful run.

The categories are:

- **CLEAN** — substantive content is bounded by the declared papers, with no
  information derived from or describing the ECDSA Fail repository.
- **CONTAMINATED** — the knowledge base contains or inherits any information
  about the ECDSA Fail repository. Prior-run or candidate-solution leakage is
  not required for this classification.
- **RAW** — an unprocessed source-paper collection; preprocessing
  contamination is not applicable.

For the strict eight-paper paper-only treatment, use only
`ecdsa-8-paper-paper-only-kb-v1`. A `CLEAN` label on another corpus does not
make it interchangeable with that treatment.

Contaminated knowledge bases are stored under `contaminated/` and use
references of the form
`knowledge-base:users/bx/contaminated/<knowledge-base-id>`.

## Inventory

| Knowledge base | Status | Suitable use and audit finding |
| --- | --- | --- |
| `ecdsa-32-paper-bundle-kb-v1` | **CONTAMINATED** | Contains the ECDSA Fail objective, representation and reversibility assumptions, and explicit benchmark-transfer guidance. |
| `ecdsa-32-raw-paper-kb-v1` | **RAW** | Raw 32-paper collection. |
| `ecdsa-6-precutoff-raw-v1` | **RAW** | Raw six-paper pre-cutoff collection. |
| `ecdsa-6-precutoff-user-graph-kb-v1` | **CLEAN** | Source-grounded synthesis from its declared six pre-cutoff papers. No ECDSA Fail repository information was found. It explicitly excludes prior Astra discoveries, scores, tuned parameters, and unpublished companion implementations. Suitable for the six-paper treatment, not the strict eight-paper treatment. |
| `ecdsa-8-paper-frontier-kb-v1` | **CONTAMINATED** | Derived from `ecdsa-8-paper-kb-v1`, so it inherits that KB's mixed benchmark/run provenance. |
| `ecdsa-8-paper-frontier-kb-v2` | **CONTAMINATED** | Contains the ECDSA Fail task equations, input ABI, score formula, and benchmark-specific optimization guidance. Its exclusion of prior Astra discoveries does not make it clean under this definition. |
| `ecdsa-8-paper-kb-v1` | **CONTAMINATED** | Contains current benchmark architecture, benchmark-source facts, trusted/local measured outcomes, failed local experiments, and implementation-facing adaptation guidance. |
| `ecdsa-8-paper-paper-only-kb-v1` | **CLEAN** | Approved strict eight-paper paper-only control. Its provenance boundary excludes implementation source, result history, external notes, auxiliary software, and application-specific adaptation advice. |
| `ecdsa-8-raw-paper-kb-v1` | **RAW** | Raw eight-paper collection. |
| `ecdsa-luo-space-efficient-point-addition` | **CONTAMINATED** | Contains the ECDSA Fail ABI, score formula, existing benchmark score regime, compatibility checks, and a repository-specific porting plan. The Luo companion repository alone is not the reason for this classification. |
| `ecdsa-paper-kb-v1` | **CONTAMINATED** | Uses companion Qarton code, local benchmark repository facts, the launch baseline score, and current-frontier implementation details. |
| `ecdsa-schrottenloher-frontier-kb-v1` | **CONTAMINATED** | Derived from the contaminated `ecdsa-paper-kb-v1` and retains its benchmark-adaptation provenance. |
| `ecdsa-schrottenloher-raw-paper-v1` | **RAW** | Raw Schrottenloher paper collection. |

## Audit trail

The main evidence for the classifications above is:

- `ecdsa-8-paper-kb-v1`:
  [build and experiment log](contaminated/ecdsa-8-paper-kb-v1/log.md) and
  [benchmark porting guide](contaminated/ecdsa-8-paper-kb-v1/concepts/porting-to-ecdsa-fail.md).
- `ecdsa-8-paper-frontier-kb-v1`: its
  [manifest](contaminated/ecdsa-8-paper-frontier-kb-v1/knowledge-base.yaml)
  declares
  `ecdsa-8-paper-kb-v1` as its source.
- `ecdsa-paper-kb-v1`: its
  [build log](contaminated/ecdsa-paper-kb-v1/log.md) records the companion-code
  revision, benchmark checkout, launch baseline, and local architecture.
- `ecdsa-luo-space-efficient-point-addition`: its
  [benchmark-adaptation node](contaminated/ecdsa-luo-space-efficient-point-addition/nodes/luo-benchmark-adaptation.md)
  records the ECDSA Fail ABI, objective, score regime, and compatibility tests.
- `ecdsa-schrottenloher-frontier-kb-v1`: its
  [manifest](contaminated/ecdsa-schrottenloher-frontier-kb-v1/knowledge-base.yaml)
  declares `ecdsa-paper-kb-v1` as its source.
- `ecdsa-8-paper-paper-only-kb-v1`: its
  [provenance policy](ecdsa-8-paper-paper-only-kb-v1/PROVENANCE.md) defines the
  strict eight-PDF boundary.
- `ecdsa-6-precutoff-user-graph-kb-v1`: its
  [manifest](ecdsa-6-precutoff-user-graph-kb-v1/knowledge-base.yaml) states the
  six-paper source boundary and exclusions.
- `ecdsa-8-paper-frontier-kb-v2`: its
  [coverage record](contaminated/ecdsa-8-paper-frontier-kb-v2/coverage/coverage-matrix.md)
  excludes prior Astra discoveries, but its
  [benchmark contract](contaminated/ecdsa-8-paper-frontier-kb-v2/evidence/benchmark-contract.md)
  contains ECDSA Fail repository information.
- `ecdsa-32-paper-bundle-kb-v1`: the
  [processed synthesis](contaminated/ecdsa-32-paper-bundle-kb-v1/ecdsa-fail-32-paper-knowledge-base.md)
  contains the ECDSA Fail objective and repository-specific transfer rules.

Re-audit a knowledge base and update this table whenever its source set or
processed content changes.
