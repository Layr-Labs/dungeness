# Decision dossier: arithmetic control structure

Controlled arithmetic is often expensive because an outer condition is
propagated into every gate. The papers expose several ways to change the
logical structure before paying that cost.

## Four control patterns

### 1. Control only operations that actually depend on the branch

Luongo's controlled modular adder controls the initial addition and final
cleanup comparison, while middle reduction logic follows from the value and
its reduction flag. Häner gives related controlled modular structures.

Question:

```text
Which internal operations are data-dependent consequences of the controlled
input, and which truly need the external control?
```

### 2. Replace no-op with a cheap alternative and correct globally

Litinski's controlled add-subtract chooses addition on one branch and
subtraction on the other. This is cheaper per shifted operation, but the
unwanted zero-branch work accumulates into an algebraic expression that must be
corrected once.

Question:

```text
Can a sequence of expensive controlled no-ops be replaced by two cheap actions
whose aggregate difference has a low-cost closed form?
```

### 3. Curry classical offset bits into the circuit

Gidney's constant-offset adder uses offset bits only to invert controls and
control bit flips. Replacing literal one bits with an external control gives a
controlled version without extra Toffolis in its model. Häner also distinguishes
loading a constant from currying it into an adder.

Question:

```text
Is this operand compile-time constant, runtime classical, lookup-selected, or
fully quantum, and what gate interface supports that distinction?
```

### 4. Control location rather than the whole arithmetic

Luo applies arithmetic to coherent active windows selected by length metadata.
This avoids operating on provably inactive bits, but pays for location control
and unary iteration.

Question:

```text
Is the expensive condition about whether to execute, or where the active
subregister begins and ends?
```

## Control taxonomy for the benchmark

Label every operand and condition:

| Class | Example | Potential optimization |
|---|---|---|
| compile-time constant | modulus `p`, `2^32+977` | curried constant circuit |
| runtime classical bitstring | offset coordinates | classically conditioned gates or lookup |
| quantum Boolean | overflow, comparison, branch | MBU, algebraic cleanup |
| quantum word | target coordinate, numerator | general quantum arithmetic |
| phase/classical record | measurement outcome | Pauli feed-forward |

Do not call all five “controls.” Their compilation and cleanup costs differ.

## Prime-field modular wrapper

A non-modular adder is useful only after accounting for:

```text
input range
carry or overflow flag
comparison with p
conditional correction
equality boundary
flag cleanup
outer control
reverse circuit
```

Schrottenloher's pseudo-Mersenne wrapper shortens corrections but uses truncated
comparisons and a special exact-equality path. Luongo's VBE wrapper is more
generic and exposes cleanup cost. Gidney improves the constant-offset body.
These pieces can be combined only after deriving one consistent flag identity.

## Experiment queue

1. Count controlled quantum-quantum, controlled constant, and uncontrolled
   arithmetic separately in the current T owner.
2. For the most repeated controlled constant operation, compare:

```text
current controlled adder
Gidney constant-workspace adder
Gidney dirty-workspace adder
boundary-controlled modular architecture
```

3. For a shifted multiplication loop, derive Litinski's signed aggregate
   identity under the current register width and field representation.
4. Test a single complete modular operation, including flag cleanup.
5. Profile the caller. A lower local T count that extends a dirty-register
   lifetime into the Q peak can lose.

## Common false transfers

- Applying a classically controlled adder to a quantum addend.
- Counting an add-subtract step without its global corrections.
- Controlling every modular-adder gate after the reduction flag already
  contains the needed dependence.
- Treating a truncated comparison as exact.
- Ignoring control cleanup on the inverse path.
- Assuming a compile-time literal circuit can accept 256 runtime classical
  bits with the same implementation.

## Cross-paper hypotheses

- Gidney constant-offset addition inside Schrottenloher's pseudo-Mersenne
  correction.
- Luongo MBU for the final reduction flag of a Gidney-based modular wrapper.
- Litinski add-subtract for a fresh-output multiplication phase, followed by
  Häner multiply-then-consume pebbling.
- Luo active-window bounds applied only to the shrinking EEA arithmetic, while
  retaining the current recurrence.

Measure each as a complete reversible shell.
