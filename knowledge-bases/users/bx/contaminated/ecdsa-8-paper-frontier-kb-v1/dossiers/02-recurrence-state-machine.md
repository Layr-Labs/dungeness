---
kind: research-dossier
id: recurrence-state-machine
depends_on: [information-location]
---

# Dossier: choose the recurrence before compressing its state

A history format inherits the branch entropy, convergence rate, signs, and
coefficient action of its recurrence. Compressing first can optimize the wrong
state machine.

## Competing EEA organizations

### Compact binary branch walk

**[PAPER: Schrottenloher]**

```text
test parity and order
optional swap
optional subtract
right shift
record one of three reachable symbols
```

It has about `1.413n` expected iterations plus statistical slack and directly
drives a linear replay. Its advantages are low arithmetic complexity and a
small symbol; its liabilities are a coherent tape and an approximate
fixed-depth failure model.

### Explicit four-phase quotient processing

**[PAPER: Luo]**

```text
align remainders
build quotient by shift/subtract
consume quotient while updating coefficients
restore alignment and swap roles
```

The paper proves an input-independent bound `4 ceil(c n)` with
`c = 3/log2(2+sqrt(3))`. It uses explicit phase and length state, allowing
aggressive register sharing but many arithmetic steps.

### Synchronized or Dialog EEA

**[PAPER: Khattar]** A polynomial EEA stores quotient information in shared
state or as a fixed sequence of transition matrices. The Dialog can provide
implicit multiplication or division without materializing coefficients.

The unresolved issue is an integer prime-field transition system with
reversible quotient/sign extraction and bounded coefficient representation.

### Fixed-round Kaliski-style inversion

**[PAPER: Häner]** A swap-normalized binary Kaliski schedule supplies a mature
fixed-round prime-field alternative. Its value here is a control architecture
and cleanup schedule, not evidence that the older full stack is cheapest.

## Research question

Can one recurrence make the same small symbol serve all three jobs?

```text
recover predecessor
select coefficient/replay matrix
select cheap modular arithmetic branch
```

**[INFERENCE]** Candidate rounds may use signed, swapped, quotient-digit, or
role-normalized forms. A smaller tape is useful only if total walk plus replay
and normalization cost falls.

## Required properties

```text
fixed or safely bounded schedule
unique reversible predecessor
bounded signed intermediate width
well-defined terminal state
linear or otherwise cheap coefficient action
prime-field correctness
clean inverse and history disposal
```

## Decisive experiment

Build exact classical state explorers at 4, 8, 12, and 16 bits. For every
candidate recurrence measure:

```text
maximum and mean rounds
reachable branch alphabet
raw and entropy-coded state bits
comparison/add/subtract/shift work
maximum signed width
inverse collisions
coefficient matrix complexity
terminal correction complexity
```

Then synthesize one complete small-width walk-and-replay cell. Reject a
recurrence whose tape saving is consumed by extra full-width arithmetic or a
new live sign/quotient register.
