---
kind: research-dossier
id: recurrence-redesign
depends_on: [history-information-channel]
---

# Dossier: change the recurrence before compressing it

## Starting point

The paper uses parity, comparison, optional swap, optional subtraction, and a
right shift. This gives a correct fixed-depth binary-Euclid walk, but it is one
factorization of a family of integer transformations.

## Algebraic search space

**[INFERENCE]** Consider fixed-depth rounds of the form:

```text
(u,v) -> (v, (u + e*v)/2)
```

or equivalent swapped/sign-normalized forms, where a small symbol `e` selects a
reachable branch. This is not asserted by the paper as a benchmark
construction. It is a prompt to search for a recurrence whose parity invariant,
history symbol, and replay matrix align.

Questions:

- Can both operands be kept odd so the low bits determine a signed choice?
- Can comparison be reduced, delayed, or replaced by sign normalization?
- Can a swap be absorbed into naming or replay orientation?
- Can one symbol encode both subtraction direction and coefficient action?
- Does the recurrence converge in sufficiently few fixed rounds?

## What must be preserved

```text
termination with high probability under a fixed bound
bounded intermediate signed width
reversible predecessor recovery
linear action suitable for multiplication and division
clean restoration of the original denominator
```

## Avoid a false local win

A recurrence with half the history bits can still lose if it:

- needs two controlled full-width additions per round;
- doubles the fixed iteration count;
- requires a new sign register that remains live at replay peak;
- creates difficult terminal normalization.

## Decisive experiment

Before quantum implementation, search small integer states for candidate
recurrences. For each one measure:

```text
maximum rounds at 8, 12, and 16 bits
maximum signed width
symbol entropy and raw symbol width
inverse uniqueness
number of add/subtract/compare operations
```

Only then derive the modular replay matrix and test multiply/divide round trips.
