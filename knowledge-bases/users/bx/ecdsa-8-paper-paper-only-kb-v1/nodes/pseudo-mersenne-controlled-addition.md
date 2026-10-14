---
kind: node
id: pseudo-mersenne-controlled-addition
source: paper section 4, Algorithm 10
depends_on: [secp256k1-prime, approximate-comparison]
---

# Pseudo-Mersenne controlled modular addition

Fast structure:

```text
controlled ordinary add into 257-bit extended y
if carry:
    add f to low bits of y
erase carry using a truncated comparison y<x
```

This replaces subtraction of the 256-bit modulus by low-width addition of `f`.

Limitation: the fast form does not handle `x+y=p` correctly.

Exceptional variant: [`x-plus-y-equals-p.md`](x-plus-y-equals-p.md).
