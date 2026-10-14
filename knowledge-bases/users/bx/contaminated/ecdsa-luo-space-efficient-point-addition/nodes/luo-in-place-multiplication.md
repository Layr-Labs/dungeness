---
kind: node
id: luo-in-place-multiplication
source: arXiv:2607.13816v2 section 5
depends_on: [luo-hadamard-register-recycling, luo-space-efficient-modular-inversion, luo-horner-modular-multiplication]
related: [luo-in-place-division, luo-hadamard-register-recycling]
---

# Luo in-place multiplication

Interface:

```text
|x>_X |y>_Y |0>_A
  -> |x>_X |x*y>_Y |0>_A
```

for `x != 0`.

**[PAPER]** The structure mirrors in-place division:

```text
compute x*y into A
H-measure-reset old Y=y
use the freed field register during the inverse/recovery path
recompute y from x and x*y
apply Z corrections from the measurement outcome
uncompute y
swap product from A into Y
```

The exact Figure-15 companion builder makes the recovery path explicit using modular multiplication, inverse multiplication, and the EEA wrapper.

The defining feature is not the out-of-place multiplier itself, but the demolition and phase-safe recovery of the obsolete input register. Any alternative multiplication backend must preserve that recovery identity and the explicit inverse convention.
