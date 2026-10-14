---
kind: node
id: luo-in-place-division
source: arXiv:2607.13816v2 section 5 and Figure 15
depends_on: [luo-space-efficient-modular-inversion, luo-hadamard-register-recycling, luo-horner-modular-multiplication]
related: [luo-in-place-multiplication, affine-point-addition]
---

# Luo in-place division

Interface:

```text
|x>_X |y>_Y |0>_A |0>_S
  -> |x>_X |y/x>_Y |0>_A |0>_S
```

for `x != 0`.

**[PAPER]** Sequence:

```text
forward EEA on X using A:
  X=x^-1, A=0, S=Gamma(x)

multiply:
  A=y/x

H-measure-reset Y:
  record b, free Y, induce phase (-1)^(b dot y)

inverse EEA using Y as workspace:
  X=x, Y=0, S=0

recompute:
  Y=x*(y/x)=y

phase repair:
  apply Z^b to Y

uncompute recomputed y:
  Y=0

swap Y,A:
  Y=y/x, A=0
```

The construction uses three field registers rather than a fourth clean EEA workspace.

Benchmark caveat: this dynamic protocol must have a purpose-built inverse; generic reverse traversal of the emitted operations is insufficient.

