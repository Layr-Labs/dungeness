# Benchmark contract

## Objective

**[BENCHMARK]**

```text
score = round(average executed Toffoli)
        × (maximum referenced qubit id + 1)
```

The evaluator's `score.json` is canonical.

## Interface

The circuit receives:

```text
target_x, target_y : quantum 256-bit coordinates
offset_x, offset_y : runtime classical 256-bit coordinates
```

It must compute affine secp256k1 addition of the target point and offset point under the harness preconditions.

## Acceptance

All 9,024 deterministic circuit-seeded shots must have:

- correct output coordinates;
- no classical mismatch;
- every released/non-output qubit restored to zero;
- zero relative-phase garbage;
- forward followed by the benchmark's reverse protocol restoring the input.

## Cost consequences

- Only executed CCX/CCZ operations are charged.
- A classically or measurement-conditioned gate contributes according to shots where its condition fires.
- Emitted Toffoli and average executed Toffoli differ.
- Releasing a wire helps only if the hard maximum qubit ID falls.
- A measurement-based circuit needs an explicit inverse; gate-list reversal is insufficient.

## Product break-even

For base `(T,Q)` and candidate deltas `(dT,dQ)`:

```text
(T+dT)(Q+dQ) < TQ
```

Exact threshold:

```text
dT < -T·dQ/(Q+dQ)
```

Calculate it at the current trusted base before every experiment.

## Validation ladder

1. confirm the active build path;
2. compile and run focused primitive tests;
3. run basis and superposition/phase tests;
4. inspect emitted stream and maximum ID;
5. run the untouched trusted 9,024-shot evaluator;
6. read `score.json`;
7. verify only allowed files changed.

Reduced tests and projections are not benchmark proof.
