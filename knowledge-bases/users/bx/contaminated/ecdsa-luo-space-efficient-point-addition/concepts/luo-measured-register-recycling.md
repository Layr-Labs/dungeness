# Measured field-register recycling

## Core identity

Hadamard-basis measurement can delete a computational-basis value while converting its dependence into a known classical phase:

```text
|y> --H^n, measure b--> (-1)^(b dot y)
```

If `y` can later be recomputed from surviving quantum data, applying `Z^b` to that recomputation cancels the phase. The recomputation can then be reversed.

## Register-lifetime effect

In the paper's in-place division:

```text
A holds y/x
Y still holds obsolete y
inverse EEA needs one clean field register
```

Measuring and resetting `Y` makes the required workspace available without adding a fourth field register. The phase is repaired after the EEA state has been uncomputed.

## Correctness obligations

A safe implementation must establish:

- the old value is exactly recoverable from surviving values;
- measurement outcomes remain available until correction;
- bit order for `b dot y` matches the recomputed register;
- conditional `Z` operations are phase-visible to the evaluator;
- resets are legal at this program point;
- no generic inverse operation silently drops the measurement transcript.

Tests should include superpositions, not only classical basis states. A basis-value test cannot detect all relative-phase failures.

## Relationship to measurement-based uncomputation

Standard measurement-based uncomputation often targets a flag or predicate. Luo et al. apply the same principle to an entire field element:

```text
one-bit MBU -> n-bit demolition -> workspace reuse -> n-bit phase repair
```

The potential qubit saving is therefore hundreds of wires, but so is the phase surface that must be tested.

Relevant nodes:

- [`luo-hadamard-register-recycling.md`](../nodes/luo-hadamard-register-recycling.md)
- [`luo-in-place-division.md`](../nodes/luo-in-place-division.md)
- [`luo-in-place-multiplication.md`](../nodes/luo-in-place-multiplication.md)
