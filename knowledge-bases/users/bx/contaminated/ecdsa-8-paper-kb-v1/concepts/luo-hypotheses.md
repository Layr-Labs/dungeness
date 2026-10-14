# Luo-derived benchmark hypotheses

All entries are **[INFERENCE]** and require measurement.

## H1 — whole-register MBU can lower the global peak

Hypothesis:

```text
an obsolete 256-bit operand can be H-measured,
reset, reused through inversion cleanup,
then phase-corrected by recomputation
```

Gate risk: recomputation may exceed the score benefit.

First test: a tiny phase-sensitive demolition primitive, then one isolated field call site.

## H2 — liveness metadata is more valuable than literal dynamic arithmetic

Hypothesis:

```text
paper-derived active ranges let the allocator overlap storage
without changing the existing adder topology
```

This has a lower correctness and Toffoli risk than coherent position selection.

## H3 — inactive field slices are a dirty-ancilla pool

Hypothesis:

```text
known-inactive high or low slices can replace clean helper qubits
if each borrowed bit is restored
```

Measure whether peak allocation falls; borrowing bits that were already live does not reduce the peak.

## H4 — selected unary control beats repeated equality tests

Hypothesis:

```text
one interval selector plus indexed operations
costs less than many independent multi-controlled equalities
```

The crossover depends on interval width, native MCX decomposition, and whether clean selector ancillas increase peak.

## H5 — exact fixed schedule may replace failure-margin padding

Hypothesis:

```text
an exact worst-case schedule can remove empirical padding,
failure checks, or fallback state from another EEA implementation
```

Counter-risk: Luo's exact four-phase step is much more expensive than the approximate binary-history step.

## H6 — full Luo EEA is a width fallback, not a first score experiment

Use the full architecture only if a hard qubit ceiling matters more than gate count. Establish a projected score before implementation:

```text
projected score = projected executed Toffoli * projected peak
```

## Experiment log template

```text
Hypothesis:
Base commit:
Peak owner before:
Semantic primitive tested:
Toffoli before/after:
Peak qubits before/after:
Full score before/after:
Basis correctness:
Superposition/phase correctness:
Forward/reverse correctness:
Interpretation:
```

