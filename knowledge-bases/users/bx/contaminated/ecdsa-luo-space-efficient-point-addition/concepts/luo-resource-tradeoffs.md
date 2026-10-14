# Resource tradeoffs

## What the paper optimizes

**[PAPER]** The construction targets minimum logical width in the standard circuit model:

```text
modular inversion = 2n + 6 floor(log2 n) + 19
point addition     = 3n + 6 floor(log2 n) + 19
```

At `n=256`, this gives 579 and 835 qubits.

The width reduction comes from three mechanisms:

1. remainders and Bézout coefficients share two work registers;
2. logarithmic length registers describe moving value boundaries;
3. an obsolete field register is measured, reset, reused, and phase-corrected.

## What the paper pays

Dynamic positions require location-controlled arithmetic and length maintenance. The paper reports:

```text
modular inversion: 30.59M Toffolis at n=256
point addition:    70.10M Toffolis at n=256
```

The rough point-addition product is:

```text
70.10M * 835 ≈ 58.5B
```

This is not a benchmark prediction, but it shows why qubit count alone is an incomplete selection criterion.

## Three adoption levels

### Level 1 — reuse the proof ideas

- identify nonoverlapping register lifetimes;
- narrow live spans by global step;
- borrow inactive field slices as restored dirty workspace.

This can reduce peak space without changing arithmetic semantics.

### Level 2 — reuse measurement demolition

Recycle one exactly recomputable field value with Hadamard measurement and phase repair. This has larger potential savings but requires phase-sensitive dynamic-circuit validation.

### Level 3 — port the complete EEA

Adopt shared work registers, coherent lengths, unary selectors, and location-controlled arithmetic. This gives the paper's strongest width result and its largest gate/implementation burden.

## Decision rule

Evaluate every change by both factors:

```text
delta executed Toffoli
delta peak qubits
```

Prefer the lowest adoption level that removes the actual measured peak owner.

