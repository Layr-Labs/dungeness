---
kind: node
id: litinski-schoolbook-multiplication
source: arXiv:2410.00899
depends_on: [litinski-controlled-add-subtract, litinski-global-corrections]
---

# Schoolbook multiplication

**[PAPER]**

```text
|x>|y>|0_(2n)> -> |x>|y>|xy>
Toffoli = n^2 + 4n + 3
```

For multiplication modulo `2^n`:

```text
Toffoli = 0.5n^2 + 1.5n
```

The construction is attractive at practical register sizes despite asymptotically faster multiplication algorithms.

Output placement is out of place and therefore central to any benchmark evaluation.
