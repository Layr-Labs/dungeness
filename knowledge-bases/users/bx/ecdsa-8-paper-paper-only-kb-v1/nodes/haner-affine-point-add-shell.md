---
kind: node
id: haner-affine-point-add-shell
source: IACR ePrint 2020/077
depends_on: [haner-division-workspace-reuse, haner-integrated-multiply-add]
---

# Häner affine point-add shell

**[PAPER]** The integrated affine Weierstrass circuit uses:

```text
2 divisions
2 multiplications
1 squaring
9 additions/subtractions
```

Its schedule fuses the square with its consumer, reuses division workspace, and selects arithmetic variants according to width, T count, or depth.

Use it as a dependency baseline for reconstructing where an optimization belongs.
