---
kind: section
source: IACR ePrint 2020/077
title: Inversion and point addition
---

# Häner et al. — inversion and affine point addition

The Kaliski round is reformulated with controlled swaps. The pseudo-inverse correction is overlapped with inverse uncomputation. Division clears inversion auxiliaries and reuses them for multiplication.

Affine point addition uses:

```text
2 divisions + 2 multiplications + 1 square + 9 additions
```

## Nodes

- [`../nodes/haner-swap-normalized-kaliski.md`](../nodes/haner-swap-normalized-kaliski.md)
- [`../nodes/haner-pseudoinverse-correction.md`](../nodes/haner-pseudoinverse-correction.md)
- [`../nodes/haner-division-workspace-reuse.md`](../nodes/haner-division-workspace-reuse.md)
- [`../nodes/haner-affine-point-add-shell.md`](../nodes/haner-affine-point-add-shell.md)
