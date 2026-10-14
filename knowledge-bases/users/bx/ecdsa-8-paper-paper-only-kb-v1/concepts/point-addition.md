# Reversible affine point addition

For distinct non-opposite affine points:

```text
lambda = (y2-y1)/(x2-x1) mod p
x3     = lambda^2-x1-x2 mod p
y3     = lambda*(x1-x3)-y1 mod p.
```

The reversible difficulty is not the formula alone. It is placing the slope
and arithmetic intermediates so they can be consumed and erased without
retaining a large inverse or product register.

## Paper approaches

- Schrottenloher uses an in-place multiplication/division primitive based on
  compact Euclid history.
- Luo et al. use exact shared-register EEA and measured field-register
  recycling.
- Häner et al. integrate Montgomery arithmetic, Kaliski inversion, workspace
  reuse, and caller-aware uncomputation.

## Boundary

Special points, coordinate representation, selected-point lookup, and scalar
windowing belong to each paper's surrounding wrapper and validity assumptions.
