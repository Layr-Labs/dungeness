---
kind: node
id: affine-point-addition
source: paper section 2, Algorithm 1
depends_on: [windowed-point-addition, in-place-modular-multiplication]
---

# Affine point addition

For distinct, non-opposite points:

```text
lambda = (y2-y1)/(x2-x1) mod p
x3 = lambda^2-x1-x2 mod p
y3 = lambda*(x1-x3)-y1 mod p
```

Paper schedule:

1. load/subtract the selected point;
2. inverse in-place multiplication to form `lambda`;
3. load/add `3*x1`;
4. controlled square update;
5. forward in-place multiplication;
6. controlled negation;
7. reload point and finish coordinates.

Dominant dependency: [`in-place-modular-multiplication.md`](in-place-modular-multiplication.md).
