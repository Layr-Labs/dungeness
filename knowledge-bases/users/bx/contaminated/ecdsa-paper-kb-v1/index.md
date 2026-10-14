# Index

## Fast path

- [`agent-pack.md`](agent-pack.md) — self-contained implementation brief for a one-shot coding agent.
- [`graph.md`](graph.md) — dependency graph connecting the paper sections and atomic nodes.
- [`concepts/porting-to-ecdsa-fail.md`](concepts/porting-to-ecdsa-fail.md) — the crucial translation from the paper's setting to the benchmark.

## Paper sections

1. [`sections/01-introduction.md`](sections/01-introduction.md) — problem setting, prior work, and the paper's contributions.
2. [`sections/02-high-level-structure.md`](sections/02-high-level-structure.md) — Shor point multiplication, windowing, and reversible affine addition.
3. [`sections/03-modular-in-place-multiplication.md`](sections/03-modular-in-place-multiplication.md) — fixed-step binary Euclid, compressed history, Bézout replay, and in-place multiplication.
4. [`sections/04-approximate-and-modular-arithmetic.md`](sections/04-approximate-and-modular-arithmetic.md) — approximate comparison and generic versus pseudo-Mersenne modular primitives.
5. [`sections/05-discussion.md`](sections/05-discussion.md) — resource estimates, cost centers, limitations, and implications.

## Atomic nodes

### Problem and point-addition layer

- [`nodes/secp256k1-prime.md`](nodes/secp256k1-prime.md)
- [`nodes/shor-point-multiplication.md`](nodes/shor-point-multiplication.md)
- [`nodes/windowed-point-addition.md`](nodes/windowed-point-addition.md)
- [`nodes/affine-point-addition.md`](nodes/affine-point-addition.md)

### In-place multiplication layer

- [`nodes/euclid-history.md`](nodes/euclid-history.md)
- [`nodes/register-sharing.md`](nodes/register-sharing.md)
- [`nodes/history-compression.md`](nodes/history-compression.md)
- [`nodes/bezout-replay.md`](nodes/bezout-replay.md)
- [`nodes/in-place-modular-multiplication.md`](nodes/in-place-modular-multiplication.md)

### Arithmetic layer

- [`nodes/adder-tradeoffs.md`](nodes/adder-tradeoffs.md)
- [`nodes/approximate-comparison.md`](nodes/approximate-comparison.md)
- [`nodes/generic-modular-doubling.md`](nodes/generic-modular-doubling.md)
- [`nodes/pseudo-mersenne-doubling.md`](nodes/pseudo-mersenne-doubling.md)
- [`nodes/generic-controlled-modular-addition.md`](nodes/generic-controlled-modular-addition.md)
- [`nodes/pseudo-mersenne-controlled-addition.md`](nodes/pseudo-mersenne-controlled-addition.md)
- [`nodes/x-plus-y-equals-p.md`](nodes/x-plus-y-equals-p.md)
- [`nodes/measurement-based-uncomputation.md`](nodes/measurement-based-uncomputation.md)

### Parameters, resources, and transfer

- [`nodes/implementation-parameters.md`](nodes/implementation-parameters.md)
- [`nodes/failure-model.md`](nodes/failure-model.md)
- [`nodes/resource-estimates.md`](nodes/resource-estimates.md)
- [`nodes/cost-hotspots.md`](nodes/cost-hotspots.md)
- [`nodes/benchmark-adaptation.md`](nodes/benchmark-adaptation.md)

## Source layer

- [`sources/2606.02235.md`](sources/2606.02235.md) — paper-level summary, exact reported resources, and provenance.
- [`sources/companion-code-map.md`](sources/companion-code-map.md) — paper concepts mapped to the released Qarton files, classes, and parameters.

## Integrated concept notes

- [`concepts/benchmark-contract.md`](concepts/benchmark-contract.md) — ABI, validation, score, and non-negotiable constraints.
- [`concepts/point-addition.md`](concepts/point-addition.md) — affine formulas and the high-level reversible schedule.
- [`concepts/dialog-in-place-multiplication.md`](concepts/dialog-in-place-multiplication.md) — the paper's central architectural idea.
- [`concepts/garbage-tape.md`](concepts/garbage-tape.md) — fixed-step Euclid schedule, register sharing, and 3-symbol compression.
- [`concepts/approximate-arithmetic.md`](concepts/approximate-arithmetic.md) — truncated comparisons and pseudo-Mersenne modular arithmetic.
- [`concepts/resource-model.md`](concepts/resource-model.md) — qubit and Toffoli accounting, hot spots, and tradeoffs.
- [`concepts/porting-to-ecdsa-fail.md`](concepts/porting-to-ecdsa-fail.md) — what transfers directly, what does not, and an implementation sequence.
- [`concepts/hypotheses.md`](concepts/hypotheses.md) — prioritized benchmark experiments.

## Provenance

- [`log.md`](log.md) — source-ingest and reconstruction notes.
