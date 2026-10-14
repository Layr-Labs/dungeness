---
kind: research-dossier
id: space-time-schedule
depends_on: [information-location, output-placement-and-affine-dataflow]
---

# Dossier: peak space is a weighted schedule

Qubit cost is not the sum of paper headline registers. It is the largest
physical index touched by one concrete schedule.

## Scheduling mechanisms

**[PAPER: Schrottenloher]** Euclid operands shrink while the coherent history
grows, allowing cleared high wires to store later symbols. Replay consumes that
history while two field values and arithmetic scratch are live.

**[PAPER: Luo]** Remainders, coefficients, and partial quotient state share two
work registers. Step-dependent active windows bound where location-controlled
operations can occur.

**[PAPER: Häner]** Intermediates are consumed before uncomputation, multiplication
is fused with its next addition, and inversion workspace is reused for
multiplication.

**[PAPER: Spooky Pebbling]** Hadamard-measured ghosts give tight time/qubit
frontiers for abstract line computations. The theorem assumes a unit-like step;
an arithmetic walk/replay has nonuniform state widths and costs.

## Build the actual dependency graph

For each event or round, annotate:

```text
forward Toffoli weight
recompute and phase-repair weight
state width
scratch width
history or transcript width
earliest production
last consumer
whether wires can be physically reused below the current hard ID
```

Treat walk, replay, fold, comparison, and affine operations as different
weights.

## Cross-paper schedule hypotheses

- Use Schrottenloher-style shrinkage for storage but Luo-style active-window
  bounds for arithmetic scratch.
- Begin consuming a history prefix before all history is produced, if reverse
  recovery dependencies permit it.
- Use a low-space adder only during the global peak and a lower-T adder outside
  it.
- Demolish or ghost an obsolete field value only across the interval where its
  release changes the hard ID.
- Apply Häner-style consumer fusion before solving the pebble schedule, because
  fusion changes the DAG itself.

All are **[INFERENCE]** until represented as a valid event graph.

## Product break-even

For current `(T,Q)`, saving `dQ > 0` qubits permits at most:

```text
added_T < T*dQ/(Q-dQ)
```

Use the complete-circuit values, not an abstract step count.

## Decisive experiment

Create an allocator-only simulator for the event graph. Sweep:

```text
production/consumption overlap
checkpoint or ghost positions
active-window bounds
adder workspace class by phase
physical register placement
```

Then validate only the Pareto candidates in the real circuit. Reject a
conceptual liveness saving if stale allocation still touches the same hard
maximum ID, or if recomputation exceeds the product break-even.
