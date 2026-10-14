# Agent instructions for the unified KB

Your goal is to improve the current `ecdsa.fail` secp256k1 point-addition score while preserving value correctness, reversibility, clean ancillas, and relative phase.

## Required reading

1. `index.md`
2. `concepts/benchmark-contract.md`
3. `concepts/current-benchmark-architecture.md`
4. `paper-matrix.md`
5. `concepts/compatibility-and-conflicts.md`
6. `experiment-map.md`

For a one-shot context, read `agent-pack.md`.

## Ground truth order

When sources disagree, use this order:

```text
untouched benchmark result
current benchmark source
current benchmark memory notes
pinned companion code
paper
cross-paper inference
```

Paper claims are not benchmark validation. Older benchmark notes may describe superseded architectures.

## Current architectural facts

**[BENCHMARK]** The live point-add path is a fixed-depth ping-pong division/multiplication design:

```text
signed binary-GCD-style walk
  -> sign/history tape
  -> coefficient replay
  -> reverse walk and tape cleanup
```

The tape plus replay registers owns the peak. Generic checkpointing and radix-4 variants have already been tried locally and were unfavorable. Re-check the current source and latest trusted run before relying on any specific round count or score.

## How to use the papers

Use Schrottenloher for:

```text
history/replay architecture
secp256k1 folds
approximate comparisons
phase-specific arithmetic
```

Use Litinski for:

```text
controlled add-subtract identities
schoolbook correction accounting
possible multiplication subcomponents
```

Use Luongo for:

```text
formal measurement-based uncomputation
expected-cost modular-adder variants
phase-correction protocols
```

Use Gidney for:

```text
constant-addition with two or three clean ancillas
dirty-half borrowing
carry venting and repair
zero-overhead controls
```

Use Spooky Pebbling for:

```text
time–space lower bounds
schedule design
ghosting semantics
```

Use Luo for:

```text
field-register demolition
active-window and liveness proofs
shared EEA storage
low-space fallback architecture
```

Use Khattar for:

```text
explicit versus implicit Bézout state
in-register quotient storage
dialog representations
direct division without materializing an inverse
```

Use Häner for:

```text
integrated ECDLP baseline
windowing and QROM
Montgomery arithmetic
Kaliski scheduling and workspace reuse
```

## Transfer discipline

Before implementing a paper idea, write down:

```text
source mechanism
current target interval
information that would be discarded
how that information is recovered
phase protocol
expected delta_T
expected delta_Q
break-even condition
smallest falsifying test
```

Reject a proposal early if it requires a fresh output register at the live peak, assumes polynomial-field arithmetic, relies on an unsupported dynamic-circuit inverse, or discards sign/history information without a recovery channel.

## Dynamic-circuit warning

Measurement/reset/feed-forward circuits are not inverted by reversing their gate list.

Before using measurement-assisted cleanup, establish:

- where every measurement result is retained;
- how phase correction is applied;
- the explicit reverse protocol;
- whether the evaluator counts the conditional branch as expected;
- whether forward/reverse and superposition tests observe the correction.

Start with a mutation-sensitive test that fails when one correction is removed.

## Benchmark discipline

- Edit only paths allowed by `benchmark.json`.
- Do not alter the harness, scoring, tests, seed derivation, or generated score.
- Use the evaluator's `score.json` as canonical.
- Distinguish emitted gates from average executed gates.
- Qubit cost is the maximum referenced qubit ID plus one, not an informal live-wire count.
- A candidate is valid only after all 9,024 shots pass with no value, garbage, phase, or reverse failure.

## Experiment strategy

Prefer isolated changes:

1. remove redundant gates or fuse adjacent transforms;
2. lower the actual peak ID by shortening a live interval;
3. replace a constant/controlled arithmetic primitive;
4. add phase-correct measurement cleanup;
5. interleave replay with production of its history;
6. alter the representation of history or Bézout state;
7. replace the inversion architecture.

Do not combine an allocator rewrite, a measurement protocol, and an EEA rewrite in one candidate.

## Logging

The served corpus is read-only. Append every benchmarked candidate to
`knowledge-base-notes/log.md` in the workspace rather than modifying the
source `log.md`:

```text
## [YYYY-MM-DD] experiment | title
- Base commit:
- Source mechanism:
- Target interval:
- Information-recovery argument:
- Files changed:
- Result:
- Score / executed Toffoli / qubits:
- Basis correctness:
- Phase and reverse correctness:
- Interpretation:
- Next action:
```
