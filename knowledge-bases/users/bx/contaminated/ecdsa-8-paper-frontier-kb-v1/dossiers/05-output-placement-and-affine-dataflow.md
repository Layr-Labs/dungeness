---
kind: research-dossier
id: output-placement-and-affine-dataflow
depends_on: [arithmetic-control-structure, field-representation-and-reduction]
---

# Dossier: output placement is part of the algorithm

Two circuits that compute the same field expression can have very different
reversible cost depending on where the result lands and which old value remains
recoverable.

## Paper contracts

### In-place linear replay

**[PAPER: Schrottenloher]** Binary-Euclid history is replayed on two coefficient
registers so multiplication or division is obtained as an in-place linear
transformation. The history is later consumed to restore the denominator.

### Fresh product accumulation

**[PAPER: Litinski]**

```text
|x>|y>|0> -> |x>|y>|xy>
```

This output shape enables low-Toffoli schoolbook multiplication but adds a
field-sized accumulator. Turning it into an in-place result can require a copy,
swap, inverse transformation, or cleanup as expensive as the operation being
optimized.

### Direct implicit division

**[PAPER: Khattar]** A Dialog for `(P,B)` can be replayed on an augmented value
containing `A`, producing `A/B` without materializing `B^-1`. This is a
polynomial-field construction; a prime-field Dialog remains a research bridge.

### Register demolition and reuse

**[PAPER: Luo]** Once an old field value is exactly recomputable, the paper
Hadamard-measures and resets its register, uses it as workspace, later
recomputes the old value, corrects the measurement phase, and uncomputes it.

### Consumer-aware integration

**[PAPER: Häner]** A product that is immediately added into another register is
fused with that consumer. Division workspace is restructured and reused for
multiplication instead of allocating widths for both black boxes.

## Affine shell questions

For:

```text
lambda = (y2-y1)/(x2-x1)
x3     = lambda^2-x1-x2
y3     = lambda*(x1-x3)-y1
```

write down:

```text
where each difference lands
whether lambda is explicit
which original coordinate remains recoverable
when the denominator and slope die
whether square and multiply results have one consumer
which field register is live at the global peak
```

The algebraic formula does not fix these choices.

## Bridge hypotheses

- A fresh accumulator may be acceptable outside the peak if its result is
  consumed and the register is released before replay reaches maximum width.
- A direct division representation may avoid explicit slope storage if the
  affine consumer can act through the same implicit transform.
- A field register may be demolished only when its exact phase predicate is
  cheaply reconstructible from the final dataflow.
- Multiplication, addition, and modular correction may be synthesized as one
  consumer-specific map instead of three reversible APIs.

These are **[INFERENCE]**, not supplied end-to-end by any paper.

## Decisive experiment

Build a lifetime table for every field-sized value in the complete point-add
shell. Compare candidate dataflows by:

```text
maximum simultaneous field registers
hard maximum qubit ID
number of inversion-grade traversals
number of copied products
complete cleanup and inverse cost
```

Reject an isolated multiplier improvement if output conversion recreates its
cost or if the new accumulator overlaps the existing hard-ID peak.
