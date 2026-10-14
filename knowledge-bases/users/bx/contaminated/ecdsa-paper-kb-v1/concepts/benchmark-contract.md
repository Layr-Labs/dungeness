# Benchmark contract

## Objective

**[BENCHMARK]** The score is lower-is-better:

```text
score = round_or_canonicalize(average executed Toffoli) * peak qubit width
```

Use the evaluator's `score.json` as canonical. Do not reconstruct the score from emitted gate counts unless checking arithmetic.

## ABI

The circuit declares four 256-element registers in this order:

1. `target_x`: qubits
2. `target_y`: qubits
3. `offset_x`: classical bits
4. `offset_y`: classical bits

It must map the affine target point to `target + offset` on secp256k1. The offset is runtime classical data, not a compile-time point and not a small lookup index.

## Required correctness

The evaluator checks:

- all 9,024 deterministic Fiat-Shamir-derived shots;
- affine output coordinates;
- every freed ancilla is zero;
- every non-output qubit is zero after the forward circuit;
- zero residual phase;
- forward followed by reversed gates restores the input.

Any failure rejects the candidate.

## Allowed changes

Read `benchmark.json`. In the public challenge repository, the editable path is normally:

```text
src/point_add/
```

Treat every other file as harness-owned unless the manifest says otherwise.

## Scoring consequences

An optimization is useful only if:

```text
(T + delta_T) * (Q + delta_Q) < T * Q
```

For a small qubit increase `dQ`, the maximum tolerable Toffoli increase is approximately:

```text
dT / T < -dQ / Q
```

Likewise, saving one qubit at `Q ~= 2700` is worth only about `T/Q` Toffolis in product terms. Compute the exchange rate at the actual base point.

## Difference from the paper

| Paper setting | Benchmark setting |
|---|---|
| selected built-in point from a window | runtime classical 256-bit offset coordinates |
| rare random-input failures allowed | zero failures on the fixed 9,024-shot validation |
| CCX/CCZ/AND logical count | average executed Toffoli under the harness semantics |
| paper/Qarton allocation model | max referenced benchmark qubit id / harness peak model |
| three lookup calls | no lookup table in the ABI |
| point at infinity controlled by window index | ordinary affine random inputs; follow harness preconditions |

The in-place multiplier and arithmetic ideas transfer. The lookup schedule and reported resource totals do not transfer unchanged.

## Validation ladder

Use the cheapest applicable checks first, but finish with the full benchmark:

1. compile;
2. focused unit/classical model tests;
3. reduced or diagnostic run, if supported;
4. inspect emitted/peak metrics;
5. untouched `./benchmark.sh` or `ecdsafail run`;
6. read `score.json`;
7. inspect git diff and ensure only editable paths changed.

Passing a reduced test is not evidence of benchmark validity.
