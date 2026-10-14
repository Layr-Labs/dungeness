# Agent instructions for this knowledge base

Your goal is to improve the ecdsa.fail secp256k1 point-addition score while preserving correctness, reversibility, ancilla cleanliness, and phase cleanliness.

## Required reading order

1. Read `index.md`.
2. Read `concepts/benchmark-contract.md`.
3. Read `concepts/porting-to-ecdsa-fail.md`.
4. Read only the concept pages relevant to the part of the circuit you intend to change.
5. Before implementing an architectural rewrite, read `concepts/resource-model.md` and `concepts/approximate-arithmetic.md`.

For a fast one-shot run, read `agent-pack.md` instead.

## Evidence discipline

- Treat **[PAPER]** and **[CODE]** statements as source knowledge, not proof that a Rust port is correct.
- Treat **[INFERENCE]** statements as hypotheses.
- Do not claim a win from source inspection, emitted gate counts, a reduced test, or a guessed cost.
- A candidate is valid only after the untouched full benchmark writes a passing `score.json`.
- Preserve failed experiments in notes when they teach a reusable constraint.

## Benchmark discipline

- Edit only paths allowed by `benchmark.json`.
- Do not modify the harness, score calculation, tests, random seed derivation, or generated score.
- Do not skip uncomputation, leak garbage, or rely on reset semantics.
- Do not assume a low failure probability is sufficient: the benchmark rejects a run if any tested shot fails.
- Compare score, not Toffoli count alone. The objective is approximately `average_executed_toffoli * peak_qubits`.

## Search strategy

Search the repository before writing new primitives. Existing implementations may already contain:

- measurement-based uncomputation;
- pseudo-Mersenne/Solinas reduction;
- truncated comparisons;
- a reversible GCD or Kaliski state machine;
- dialog/history storage;
- low-space constant adders;
- profiling or peak-owner diagnostics.

Map the paper's concepts onto existing primitives before attempting a wholesale port.

## Change strategy

Prefer this order:

1. Remove redundant work or fuse adjacent operations.
2. Reuse known-zero or known-constant registers at peak.
3. Specialize arithmetic to `p = 2^256 - 2^32 - 977`.
4. Substitute a cheaper exact primitive.
5. Introduce a bounded approximation with an explicit failure model.
6. Attempt the dialog/bit-vector architectural rewrite.

The final item has the largest theoretical upside and the largest implementation risk.

## Logging

Append a dated entry for every benchmarked candidate. When this knowledge base
is served read-only by Dungeness, write the entry to
`knowledge-base-notes/log.md` in the workspace instead of modifying source
`log.md`:

```text
## [YYYY-MM-DD] experiment | short title
- Base commit:
- Hypothesis:
- Files changed:
- Result:
- Score / Toffoli / qubits:
- Correctness:
- Interpretation:
- Next action:
```
