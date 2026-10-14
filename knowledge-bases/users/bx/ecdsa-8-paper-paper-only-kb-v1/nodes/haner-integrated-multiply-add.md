---
kind: node
id: haner-integrated-multiply-add
source: IACR ePrint 2020/077
depends_on: [haner-montgomery-windowed-multiplication]
---

# Integrated multiply-then-add

If a product is immediately added into a third register, do not copy the product and then uncompute a black-box multiplier.

**[PAPER]** Fuse multiplication and addition so the cost is approximately:

```text
one multiplication + one addition
```

instead of compute/copy/uncompute. The same principle lets a square feed its one subtraction before cleanup.
