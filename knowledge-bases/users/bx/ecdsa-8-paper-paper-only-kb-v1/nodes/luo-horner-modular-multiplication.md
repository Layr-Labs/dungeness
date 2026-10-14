---
kind: node
id: luo-horner-modular-multiplication
source: arXiv:2607.13816v2 appendix B
depends_on: []
related: [adder-tradeoffs, luo-resource-estimates]
---

# Improved Horner modular multiplication

**[PAPER]** The out-of-place primitive:

```text
|x>|y>|0> -> |x>|y>|x*y mod p>
```

uses a standard Horner scan:

```text
n controlled modular additions
n-1 modular doublings
```

Controlled modular addition cost:

```text
controlled quantum-quantum add: 3n + O(1)
fixed-modulus comparison:        3n + O(1)
conditional fixed subtraction:  3n + O(1)
flag cleanup comparison:         2n + O(1)
total:                          11n + O(1)
```

The comparison/subtraction borrows the non-target input register as dirty workspace.

Modular doubling costs:

```text
6n + O(1) Toffolis
```

Therefore:

```text
n*(11n) + (n-1)*(6n)
= 17n^2 + O(n)
```

The squaring circuit uses the same construction with the addend equal to the input and has the same upper bound.

This is generic-prime arithmetic, not the secp256k1-specific pseudo-Mersenne path in the earlier KB.
