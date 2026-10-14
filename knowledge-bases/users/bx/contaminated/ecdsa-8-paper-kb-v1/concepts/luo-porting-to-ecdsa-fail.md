# Porting Luo et al. to ecdsa.fail

## Executive conclusion

**[INFERENCE]** Treat the paper as a source of peak-width techniques, not as a wholesale replacement architecture. A direct port is likely too gate-heavy for the benchmark score.

## Semantic mapping

**[BENCHMARK]**

```text
target_x, target_y: 256 quantum bits each
offset_x, offset_y: 256 runtime classical bits each
```

The paper's Shor wrapper selects precomputed points through table lookups and uses constant-coordinate arithmetic. Reuse the benchmark's existing top-level affine/classical-offset schedule.

Transfer candidates:

```text
H-measure-reset field-register demolition
phase repair by exact recomputation
shared-lifetime proofs
active-window bounds
dirty borrowing
selected-index unary iteration
```

## Phase 0 — establish the current peak

Record:

```text
peak owner and live registers
average executed Toffoli
full score
forward/reverse and phase tests
```

No paper technique helps unless it overlaps the actual peak interval.

## Phase 1 — tiny demolition primitive

Implement a small-width map:

```text
|x>|y>|0>
  -> compute recoverable function
  -> H-measure-reset y
  -> reuse y
  -> recompute y
  -> Z^b
  -> uncompute
```

Test:

- all basis states at tiny width;
- random superpositions;
- forward followed by explicit reverse;
- mutation tests that remove or flip one correction.

If the harness cannot express the required inverse transcript, stop this branch before field-sized work.

## Phase 2 — one real call site

Find a field register that:

- is obsolete at the current peak;
- is derivable from two surviving values;
- remains obsolete until after the workspace-intensive block.

Instrument peak width before and after. Do not change the inversion architecture in the same patch.

## Phase 3 — liveness-only sharing

From the paper's method, derive static ranges:

```text
operation/step -> definitely inactive bits
```

Feed those ranges into allocation or scratch borrowing while keeping fixed-position arithmetic. This tests the value of the proof without paying location-selection gates.

## Phase 4 — selector microbenchmarks

Only where a moving boundary is unavoidable, compare:

```text
repeated equality controls
unary interval selector
fixed conservative span
```

Measure the benchmark's executed Toffoli cost, not source-level gate count.

## Phase 5 — architecture decision

Consider full shared-register EEA only if:

```text
qubit reduction is still the limiting score factor
and
the estimated Toffoli increase keeps the product competitive
```

The paper point:

```text
70.10M * 835 ≈ 58.5B
```

is a warning that a literal port is not the default route.

## Acceptance

A result is valid only after:

- all trusted benchmark shots pass;
- all freed ancillas are zero;
- relative phase is clean;
- explicit forward/reverse identity passes;
- score improves against the same base and harness.

