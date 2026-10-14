---
kind: node
id: luo-unary-iteration
source: arXiv:2607.13816v2 section 4.1
depends_on: [luo-active-windows]
related: [luo-location-controlled-swap, luo-location-controlled-add-sub]
---

# Unary iteration over a promised interval

**[PAPER]** Suppose an index register is promised to lie in:

```text
[k,K]
```

Unary iteration computes and uncomputes a sequence of temporary predicates so that exactly the operation associated with the encoded index is activated.

Resource shape:

```text
Toffoli count = O(K-k)
clean ancillas = O(log(K-k))
```

This avoids performing a separate full equality test for every possible location. The interval promise comes from the step-dependent active-window proof.

The paper's gate counts assume its stated unary-iteration construction.
Alternative selectors require separate accounting.
