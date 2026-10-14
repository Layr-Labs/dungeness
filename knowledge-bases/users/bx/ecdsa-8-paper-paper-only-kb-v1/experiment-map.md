# Source-only experiment map

These experiments are generated from unresolved interfaces in the eight
papers. Their ordering does not encode any previous implementation outcome.

## 1. Transcript codec frontier

Question: can a larger reversible block encode the three-symbol Euclid
alphabet more densely than five bits per three steps?

Measure:

```text
reachable states
encoded bits
encoder and decoder gates
temporary workspace
reverse-streaming order
```

Sources:

- [`nodes/history-compression.md`](nodes/history-compression.md)
- [`concepts/garbage-tape.md`](concepts/garbage-tape.md)

## 2. Integer transition alphabet

Question: can an integer Euclidean recurrence be represented as a compact list
of invertible transitions with direct action on arbitrary coefficient values?

Required proof:

```text
transition matrix
sign and quotient encoding
fixed schedule
coefficient bounds
forward and inverse replay
```

Sources:

- [`nodes/khattar-dialog-representation.md`](nodes/khattar-dialog-representation.md)
- [`nodes/khattar-prime-field-barriers.md`](nodes/khattar-prime-field-barriers.md)
- [`nodes/bezout-replay.md`](nodes/bezout-replay.md)

## 3. Transcript replay plus field demolition

Question: can a field register be measured, reused, and phase-repaired around
a transcript-based multiplier?

First test a small exact field and prove that the deleted value is
reconstructible from surviving state.

Sources:

- [`nodes/luo-hadamard-register-recycling.md`](nodes/luo-hadamard-register-recycling.md)
- [`nodes/in-place-modular-multiplication.md`](nodes/in-place-modular-multiplication.md)

## 4. Liveness-only shared storage

Question: which parts of Luo's exact active-window proof can justify shared
allocation without adopting location-controlled arithmetic?

Output:

```text
step-indexed live ranges
zero or inactive ranges
borrowed dirty ranges
proof of restoration
```

Sources:

- [`nodes/luo-active-windows.md`](nodes/luo-active-windows.md)
- [`nodes/luo-shared-work-registers.md`](nodes/luo-shared-work-registers.md)

## 5. Vented pseudo-Mersenne correction

Question: can carry venting implement additions of a short
pseudo-Mersenne correction constant with low clean workspace?

Include the complete comparison, correction, and canonicalization shell.

Sources:

- [`nodes/gidney-carry-venting.md`](nodes/gidney-carry-venting.md)
- [`nodes/pseudo-mersenne-doubling.md`](nodes/pseudo-mersenne-doubling.md)
- [`nodes/pseudo-mersenne-controlled-addition.md`](nodes/pseudo-mersenne-controlled-addition.md)

## 6. Fresh product consumed before cleanup

Question: can a sole consumer absorb Litinski's fresh product before reverse
cleanup, following Häner's producer-consumer pattern?

Sources:

- [`nodes/litinski-schoolbook-multiplication.md`](nodes/litinski-schoolbook-multiplication.md)
- [`nodes/haner-integrated-multiply-add.md`](nodes/haner-integrated-multiply-add.md)

## Experiment record

```text
Hypothesis:
Source mechanisms:
State transformation:
Representation:
Forward correctness:
Inverse correctness:
Garbage and phase state:
Logical width:
Gate count and convention:
Observed incompatibility:
Conclusion:
```
