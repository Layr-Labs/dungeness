---
kind: node
id: khattar-in-register-quotient
source: arXiv:2510.10967, section II.B.2
---

# In-register quotient storage

As polynomial remainders shrink, their freed coefficient slots hold the next Euclidean quotient.

**[PAPER]** This removes a separate `nb`-scale quotient register and deterministically reaches:

```text
2nb + O(log^2 n) qubits
```

without relying on a probabilistic bound on quotient size.
