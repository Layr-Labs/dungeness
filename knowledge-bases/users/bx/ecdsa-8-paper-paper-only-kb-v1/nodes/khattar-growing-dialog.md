---
kind: node
id: khattar-growing-dialog
source: arXiv:2510.10967
depends_on: [khattar-dialog-representation]
---

# Growing Dialog, shrinking state

**[PAPER]** For the polynomial construction:

```text
len(poly) + len(dialog) = 2n
```

Each of the fixed `2n` iterations shortens active polynomial state and appends one Dialog element. Both occupy one shared `2nb` register.

The invariant is analogous in spirit to storing history in space freed by a shrinking Euclid state.
