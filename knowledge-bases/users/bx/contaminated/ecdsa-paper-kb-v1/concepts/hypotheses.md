# Ranked hypotheses

## H1 — Full dialog/history in-place multiplier

**Claim:** Replacing the existing coefficient-heavy or repeated-inversion machinery with history construction plus replay can approach the paper's 4.36n-space architecture and materially reduce product score.

**Expected impact:** Very high.

**Risk:** Very high; substantial port, convention, phase, and approximation risk.

**Falsifier:** A complete ABI-compatible cost model shows tape + replay + integration exceeds the current product, or a working exact port cannot lower the peak.

## H2 — Exact history/replay microbenchmark first

**Claim:** A small-width exact port will reveal whether the benchmark IR can express the paper architecture cleanly before a 256-bit rewrite.

**Expected impact:** Enables H1; no immediate score win.

**Risk:** Low.

**Required output:** Exhaustive forward/inverse tests and measured scaling.

## H3 — Pseudo-Mersenne fold in remaining full-modulus corrections

**Claim:** Any hot path still subtracting/adding full `p` after a known 256-bit overflow can use `2^256 == 2^32+977 mod p`.

**Expected impact:** Medium if such sites remain.

**Risk:** Medium; carry propagation and flag cleanup.

**Falsifier:** Repository already uses a cheaper exact or approximate Solinas reduction at all hot sites.

## H4 — Early exceptional adder, later fast adder

**Claim:** A replay or coefficient phase may need `x+y=p` support only for an initial prefix; later iterations can use a cheaper overflow-only adder.

**Expected impact:** Medium.

**Risk:** Medium/high; prefix boundary is data-distribution dependent.

**Test:** Instrument exact classical states over all benchmark shots, find the last exceptional occurrence, then add margin.

## H5 — Phase-specific adder backend

**Claim:** Low-peak phases can use extra-ancilla Gidney/hybrid arithmetic while the global-peak replay phase uses low-space arithmetic.

**Expected impact:** Small to medium Toffoli reduction without a qubit increase if phase-local slack exists.

**Risk:** Low/medium.

**Test:** Profile phase-local peak before changing backends.

## H6 — Truncated comparator

**Claim:** Selected comparisons can use only high bits with no failures on the benchmark set.

**Expected impact:** Small to medium.

**Risk:** High for validity; low implementation effort.

**Test:** Shadow-compute exact versus truncated results in a classical diagnostic across all 9,024 states before emitting the approximate circuit.

## H7 — Compressor/consumer fusion

**Claim:** Decompressing a 5-bit block to six wires and then using its three symbols can be fused with the controlled operations, reducing Toffolis or peak ancillas.

**Expected impact:** Small individually, repeated many times.

**Risk:** Medium; partial-domain reversible synthesis.

**Test:** Exact truth-table synthesis on all reachable states plus inverse replay.

## H8 — Larger history blocks

**Claim:** Encoding more than three ternary symbols per block reduces tape qubits enough to improve product.

**Expected impact:** Potential qubit reduction.

**Risk:** High; encoder/decoder cost and random-access complexity can dominate.

**Break-even:** Compute saved peak qubits times `T/Q`, then divide by the number of encode/decode invocations.

## H9 — Reduce iteration or padding constants

**Claim:** The fixed validation set may tolerate fewer than 402 iterations or smaller register padding.

**Expected impact:** Direct Toffoli and possibly qubit reduction.

**Risk:** Very high and overfit-prone.

**Rule:** Attempt only after the architecture works with conservative exactness. Keep a safety margin beyond the maximum observed requirement.

## H10 — Paper ideas at the current frontier

**Claim:** The current leaderboard circuit already uses a jump-2 dialog tape, so the paper is more useful as an explanatory map than as a new architecture there.

**Expected impact:** Small incremental.

**Likely targets:** codec fusion, source-level invariants, controlled-add lower bounds, streaming global dialog encoding, and peak-owner reuse.

**Interpretation:** A null result at the current frontier does not refute the KB's value on a pre-paper baseline.
