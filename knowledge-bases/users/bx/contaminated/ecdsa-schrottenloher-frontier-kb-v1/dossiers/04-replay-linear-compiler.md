---
kind: research-dossier
id: replay-linear-compiler
depends_on: [history-information-channel, recurrence-redesign]
---

# Dossier: compile a replay round as one linear cell

## Paper replay

**[PAPER]** Reading history in reverse updates two modular values using a
combination of:

```text
double one value
conditionally add the other
conditionally swap the pair
```

Initialized appropriately, the accumulated linear transformation implements
multiplication or division by the denominator.

## The decomposition is not sacred

Each history symbol chooses a small matrix over the field. The implementation
can be synthesized from the matrix rather than from the paper's prose-level
primitive sequence.

**[INFERENCE]** For each reachable symbol:

1. Write its exact 2x2 linear transformation.
2. Normalize signs and swaps symbolically.
3. Look for a shared sequence whose branches differ only by a correction.
4. Fuse doubling, add/subtract, and pseudo-Mersenne reduction before allocating
   separate carry or comparison flags.

Possible targets:

```text
double-then-add
add-then-half in inverse replay
signed add-or-subtract with one global correction
swap absorbed into register role for the next round
correction flag reused as the history control
```

## Cost the complete cell

Count:

- executed controlled arithmetic;
- fold additions;
- comparison or overflow cleanup;
- scratch lifetime;
- inverse protocol;
- whether the cell fits under the current maximum qubit ID.

Do not compare only the central ripple adder.

## Decisive experiment

Generate exact truth tables for 3- to 8-bit versions of the reachable replay
cells. Verify forward and inverse behavior, then compare emitted operation
counts for:

```text
literal primitive composition
symbol-specialized cell
shared cell plus branch correction
```

The goal is a repeated-cell saving, not merely a prettier identity.
