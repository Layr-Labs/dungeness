# Knowledge graph

## Main dependency path

```text
luo-four-phase-eea
  -> luo-uniform-step-bound
  -> luo-shared-work-registers

luo-shared-work-registers
  -> luo-length-registers
  -> luo-optimized-eea-step

luo-uniform-step-bound + luo-length-registers
  -> luo-active-windows
  -> luo-unary-iteration

luo-unary-iteration
  -> luo-location-controlled-swap
  -> luo-location-controlled-add-sub
  -> luo-dirty-length-update

luo-optimized-eea-step
  -> luo-space-efficient-modular-inversion

luo-horner-modular-multiplication
  -> luo-in-place-division
  -> luo-in-place-multiplication

luo-hadamard-register-recycling
  -> luo-in-place-division
  -> luo-in-place-multiplication

luo-space-efficient-modular-inversion
  -> luo-in-place-division

luo-in-place-division + luo-in-place-multiplication
  -> luo-resource-estimates
  -> luo-benchmark-adaptation
  -> luo-hybridization-opportunities
```

## Architecture flow

```text
exact fixed EEA schedule
          |
shared work registers + coherent lengths
          |
active-window location-controlled arithmetic
          |
forward inversion with retained Gamma(x)
          |
Hadamard-measure-reset obsolete field register
          |
inverse EEA + recomputation + Z phase repair
          |
three-field-register affine point addition
```

## Node catalog

### Algorithm and layout

- [`nodes/luo-four-phase-eea.md`](nodes/luo-four-phase-eea.md)
- [`nodes/luo-uniform-step-bound.md`](nodes/luo-uniform-step-bound.md)
- [`nodes/luo-shared-work-registers.md`](nodes/luo-shared-work-registers.md)
- [`nodes/luo-length-registers.md`](nodes/luo-length-registers.md)
- [`nodes/luo-optimized-eea-step.md`](nodes/luo-optimized-eea-step.md)
- [`nodes/luo-space-efficient-modular-inversion.md`](nodes/luo-space-efficient-modular-inversion.md)

### Dynamic primitives

- [`nodes/luo-active-windows.md`](nodes/luo-active-windows.md)
- [`nodes/luo-unary-iteration.md`](nodes/luo-unary-iteration.md)
- [`nodes/luo-location-controlled-swap.md`](nodes/luo-location-controlled-swap.md)
- [`nodes/luo-location-controlled-add-sub.md`](nodes/luo-location-controlled-add-sub.md)
- [`nodes/luo-dirty-length-update.md`](nodes/luo-dirty-length-update.md)

### Measured arithmetic and use

- [`nodes/luo-hadamard-register-recycling.md`](nodes/luo-hadamard-register-recycling.md)
- [`nodes/luo-in-place-division.md`](nodes/luo-in-place-division.md)
- [`nodes/luo-in-place-multiplication.md`](nodes/luo-in-place-multiplication.md)
- [`nodes/luo-horner-modular-multiplication.md`](nodes/luo-horner-modular-multiplication.md)
- [`nodes/luo-resource-estimates.md`](nodes/luo-resource-estimates.md)
- [`nodes/luo-benchmark-adaptation.md`](nodes/luo-benchmark-adaptation.md)
- [`nodes/luo-hybridization-opportunities.md`](nodes/luo-hybridization-opportunities.md)

