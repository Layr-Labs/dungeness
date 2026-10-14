---
kind: node
id: in-place-modular-multiplication
source: paper section 3.2, Algorithm 4
depends_on: [euclid-history, bezout-replay]
---

# In-place modular multiplication

Goal:

```text
|x,y> -> |x,xy mod p>
```

Composition:

```text
1. convert x to Euclid history d
2. replay d on (y,0), yielding (0,xy)
3. swap result into y and release zero register
4. reverse history conversion to restore x
```

The inverse circuit maps `y` to `yx^-1`.

Space:

```text
tape ~= 2.355n + O(sqrt(n))
pair = 2n
peak ~= 4.355n + O(sqrt(n))
```

This node is the paper's primary architectural contribution and the main dependency of [`affine-point-addition.md`](affine-point-addition.md).
