---
kind: node
id: khattar-explicit-vs-implicit-bezout
source: arXiv:2510.10967, section II.B.1
---

# Explicit versus implicit Bézout access

Explicit access materializes coefficient polynomials. Implicit access stores a sequence of transformations whose product would produce those coefficients.

Tradeoff:

```text
explicit: larger/direct state, cheap repeated coefficient use
implicit: compact/shared state, replay cost per use
```

The right model depends on how many later operations need the coefficients.
