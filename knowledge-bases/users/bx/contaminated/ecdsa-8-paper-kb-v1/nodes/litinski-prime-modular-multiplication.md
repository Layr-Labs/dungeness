---
kind: node
id: litinski-prime-modular-multiplication
source: arXiv:2410.00899
depends_on: [litinski-schoolbook-multiplication]
---

# Prime-modulus schoolbook multiplication

**[PAPER]** In Montgomery representation:

```text
T = n^2 + 6n
    + (n/w)(2^w + 3·2^(w/2) + 3n - 3)
```

The windowed steps combine controlled add-subtract, lookup, addition, and lookup uncomputation. A garbage register stores per-window information.

The result is not specialized to `p = 2^256 - 2^32 - 977`; a Solinas-style benchmark shell may have different correction economics.
