# Decision dossier: cross-paper compositions

These are research hypotheses, not claims established by the papers. Each pair
is chosen because one mechanism may address a liability exposed by another.

## 1. Compact history plus denser transition alphabet

```text
base: Schrottenloher binary-Euclid tape and replay
graft: Khattar linear-transition viewpoint
promise: fewer stored symbols or fewer replay operations
barrier: derive an integer prime-field transition alphabet
smallest test: classical small-prime encoder/replay with exact inverse
```

## 2. Exact active windows for compact binary Euclid

```text
base: Schrottenloher recurrence
graft: Luo step-indexed active-range proof technique
promise: remove probabilistic register padding or reduce arithmetic width
barrier: new bounds for a different recurrence
smallest test: empirical range envelope, then prove a conservative bound
```

## 3. Vented constant arithmetic inside pseudo-Mersenne reduction

```text
base: Schrottenloher correction by f = 2^32+977
graft: Gidney constant-workspace classical-offset adder
promise: lower workspace or Toffoli in frequent constant corrections
barrier: prime-field flag/equality cleanup and runtime control
smallest test: exact modular doubling at small pseudo-Mersenne primes
```

## 4. MBU on the final reduction flag

```text
base: a complete modular adder
graft: Luongo one-bit cleanup lemma
promise: half the final comparator cost in expectation
barrier: repair computation must remain available and self-adjoint
smallest test: all measurement branches of one modular add
```

## 5. Boundary control plus no-overhead constant control

```text
base: Luongo/Häner modular-adder control structure
graft: Gidney controlled constant-offset primitive
promise: avoid outer-control overhead in both body and correction
barrier: distinguish quantum addend from classical modulus/offset
smallest test: controlled addition of a classical correction modulo p
```

## 6. Add-subtract multiplier plus caller pebbling

```text
base: Litinski fresh-output multiplication
graft: Häner multiply-then-consume schedule
promise: keep T reduction without copying the product
barrier: global correction and Montgomery representation
smallest test: fresh product consumed by one subtraction before reverse
```

## 7. Fresh multiplier plus full-register demolition

```text
base: Litinski or another cheap out-of-place multiplier
graft: Luo measure/recompute/phase-repair wrapper
promise: expose in-place interface with three field registers
barrier: several recomputations may erase T benefit
smallest test: generic multiplier ABI at small prime widths
```

## 8. Kaliski normalization with modern constant adders

```text
base: Häner swap-normalized Kaliski round
graft: Gidney constant-offset and Luongo MBU primitives
promise: retain mature exact recurrence while lowering round arithmetic
barrier: many operations remain quantum-quantum
smallest test: classify the Kaliski round's operand types and replace one owner
```

## 9. Pseudo-inverse correction during cleanup

```text
base: any fixed-round inverse producing a power-of-two-scaled result
graft: Häner's correction synchronized with reverse rounds
promise: hide correction depth/lifetime under uncomputation
barrier: benchmark counts gates even when depth overlaps
smallest test: determine whether correction reuses controls or also saves gates
```

## 10. Transcript checkpointing with spooky schedules

```text
base: compact transition tape
graft: Spooky measurement/recompute scheduling
promise: store only checkpoints and recreate local decisions
barrier: history bits may be cheaper than recomputing comparisons/subtractions
smallest test: one fixed block length with exact delta_T and delta_Q
```

## 11. Demolish a coordinate before replay peak

```text
base: Schrottenloher replay, which owns width
graft: Luo full-register phase repair
promise: remove one field register during the transcript peak
barrier: old coordinate must be uniquely reconstructible later
smallest test: value-lifetime proof and symbolic reconstruction formula
```

## 12. Redundant-range replay

```text
base: Schrottenloher linear coefficient replay
graft: deferred reduction / Montgomery ideas from Häner and Litinski
promise: reduce repeated modular corrections
barrier: replay invariant, comparison, and final canonicalization
smallest test: classical range growth over all replay transitions
```

## 13. In-register quotient storage for integers

```text
base: prime-field Euclidean state
graft: Khattar synchronized quotient-in-padding principle
promise: remove quotient/history allocation
barrier: polynomial degree invariant does not imply integer bit padding
smallest test: prove an integer size invariant for one quotient digit
```

## 14. Phase-specific primitive portfolio

```text
base: any complete inversion/multiplication
graft: Schrottenloher slack observation + Gidney's two workspace points
promise: low T outside the peak and low Q at the peak
barrier: implementation complexity and ABI consistency
smallest test: use two adders behind one verified interface and switch by phase
```

## Selection rule

Choose a composition only when:

1. its base component is a measured owner;
2. the graft attacks that owner;
3. the bridge is smaller than the possible gain;
4. the smallest test can reject it cheaply;
5. it explores an axis different from the last completed experiment.

Do not combine several entries until each individual bridge has evidence.
