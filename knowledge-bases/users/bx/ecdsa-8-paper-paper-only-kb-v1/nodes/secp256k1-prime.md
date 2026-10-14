---
kind: node
id: secp256k1-prime
source: paper sections 2 and 4
---

# secp256k1 prime

```text
p = 2^256 - 2^32 - 977
f = 2^32 + 977
a = 0
b = 7
```

Key congruence:

```text
2^256 == f mod p
```

This lets a 256-bit overflow be folded into the low end by adding `f`, replacing full-width correction by `p`.

Connected nodes:

- [`pseudo-mersenne-doubling.md`](pseudo-mersenne-doubling.md)
- [`pseudo-mersenne-controlled-addition.md`](pseudo-mersenne-controlled-addition.md)
- [`resource-estimates.md`](resource-estimates.md)
