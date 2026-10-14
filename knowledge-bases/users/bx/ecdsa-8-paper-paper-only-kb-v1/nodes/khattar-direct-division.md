---
kind: node
id: khattar-direct-division
source: arXiv:2510.10967
depends_on: [khattar-dialog-representation]
---

# Dialog direct division

Instead of:

```text
compute inverse B^-1
multiply A by B^-1
```

construct the Dialog of `(P,B)` and replay its transition matrices on an augmented vector containing `A`. The desired modular division emerges from the implicit Bézout action.

This can avoid a separately materialized inverse, but replay work is paid whenever the implicit coefficient is used.
