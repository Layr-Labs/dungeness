---
kind: section
paper_section: 2
title: High-level structure
---

# Section 2 — High-level structure

## Reduction chain

```text
ECDLP
  -> Shor point multiplication
  -> windowed point additions
  -> affine point addition
  -> modular in-place multiplication/division
```

## Shor layer

The quantum state computes:

```text
|u,v>|0> -> |u,v>|[u]P + [v]Q>
```

A semiclassical Fourier transform recycles control qubits, so the point register dominates logical space.

## Windowing

Split each scalar into `w`-bit chunks and precompute point windows. For `w=16`, the paper uses 28 point additions after:

- replacing the first addition by a lookup;
- removing the final three additions with classical post-processing.

## Point-add schedule

The selected point is accessed three times:

1. full `(x,y)` coordinates;
2. `3x`;
3. full `(x,y)` coordinates again.

Between accesses, the circuit performs subtraction, in-place division, controlled squaring, in-place multiplication, and final coordinate cleanup.

## Important boundary

The high-level wrapper is mostly inherited from earlier work. The paper's novel optimization effort is concentrated below it, in the in-place multiplier and arithmetic.

## Nodes

- [`../nodes/shor-point-multiplication.md`](../nodes/shor-point-multiplication.md)
- [`../nodes/windowed-point-addition.md`](../nodes/windowed-point-addition.md)
- [`../nodes/affine-point-addition.md`](../nodes/affine-point-addition.md)
- [`../nodes/in-place-modular-multiplication.md`](../nodes/in-place-modular-multiplication.md)
- [`../nodes/benchmark-adaptation.md`](../nodes/benchmark-adaptation.md)

## Next section

[`03-modular-in-place-multiplication.md`](03-modular-in-place-multiplication.md)
