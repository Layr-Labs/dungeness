---
kind: node
id: gidney-z-redundant-carries
source: arXiv:2507.23079, equation 8
---

# Z-redundant carries

For classical offset `d` and carry-in `c0`, the carry pattern of:

```text
x' = x + d + c0
```

can be reconstructed from the final sum using a complemented-input identity:

```text
carry(~x', d, c0) = carry(x, d, c0)
```

Therefore each carry is a Z-basis function of surviving data and may be measured before its phase obligation is repaired.
