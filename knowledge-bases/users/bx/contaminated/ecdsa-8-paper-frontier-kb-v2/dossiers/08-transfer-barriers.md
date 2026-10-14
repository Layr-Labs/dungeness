# Decision dossier: transfer barriers

A paper mechanism is useful only after its hidden interface has been translated
to the benchmark. This dossier is a type checker for cross-paper composition.

## Mechanism type

Assign every candidate a type:

```text
field:
  prime integer | binary polynomial | power-of-two ring

representation:
  canonical | Montgomery | redundant | pseudo-inverse | transition sequence

operands:
  quantum word | runtime classical word | compile-time constant | Boolean flag

output:
  in-place | fresh | implicit action | measured/ghosted

workspace:
  clean | dirty/borrowed | classical record | variable/fixed history

correctness:
  exact | bounded failure | expected cost | heuristic distribution

cleanup:
  explicit inverse | algebraic flag erase | MBU | phase repair | copy/uncompute

metric:
  Toffoli | T | T-depth | width | expected executed gates
```

Do not compose mechanisms whose types disagree without an explicit bridge.

## Common barriers in this corpus

### Prime field versus polynomial field

Khattar's Dialog uses polynomial degree, shifts by `z`, and multiplication by
small base-field coefficients. A secp256k1 transfer needs integer bit-length,
sign/quotient, and prime reduction proofs.

### Canonical versus Montgomery

Litinski and Häner's prime multipliers assume Montgomery residues.
Schrottenloher's pseudo-Mersenne arithmetic uses canonical-like residues.
Conversion must be global or explicitly paid.

### Fresh versus in-place output

Litinski produces a fresh product. Schrottenloher replays into an existing
target. Luo converts fresh output to in-place behavior through measurement and
recomputation. Register placement and cleanup dominate the bridge.

### Quantum versus classical operand

Gidney's new adder adds a classical offset. Its count cannot replace a
quantum-quantum adder. Runtime classical bits must also be supported by the
compiler and reverse protocol.

### Exact versus approximate

Schrottenloher truncates comparisons and sizes fixed buffers statistically.
Luo's EEA bound is exact. Mixing them changes failure semantics.

### Static versus expected count

Luongo halves one cleanup computation in expectation. The benchmark counts
average executed Toffoli, making this potentially relevant, but all branches
must be implemented and sampled correctly.

### Logical width versus hard ID

Paper width counts coexistence. The benchmark uses highest referenced qubit ID.
Allocation order and reuse are part of the transfer.

## Bridge cost worksheet

```text
source local cost:

input conversion:
output conversion:
outer-control synthesis:
fresh-output register:
garbage cleanup:
measurement repair:
exceptional-case wrapper:
reverse calls:
complete-shell multiplicity:

translated delta_T:
translated delta_Q_hard:
```

If any line is unknown, the paper's headline count is not yet a prediction.

## Compatibility proof

Before implementation, answer:

1. Are all inputs within the source primitive's range?
2. Does output representation match the next consumer?
3. Is every borrowed register restored?
4. Where is each branch or quotient decision stored?
5. Is the inverse circuit defined for the exact output state?
6. Are measurement phases repaired before interference?
7. Are equality and zero represented uniquely?
8. Are runtime classical controls available in reverse?
9. Does cleanup occur before the benchmark checks ancillas?
10. Does the translated primitive still change an owner?

## Minimal bridge tests

- arithmetic identity in a classical model;
- exhaustive small-width forward map;
- exhaustive small-width reverse map;
- superposition/phase test for measurement;
- boundary values `0`, `1`, `p-1`, exact overflow, and equality;
- caller integration with resource trace;
- complete-shell benchmark.

## How to use a failed transfer

Record the exact barrier:

```text
idea valid in source type
bridge attempted
measured or proved failure
which assumption caused it
context where assumption might hold
```

This preserves generalizable technique without repeatedly importing the same
incompatible headline result.
