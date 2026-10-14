---
kind: node
id: gidney-dirty-half-borrowing
source: arXiv:2507.23079
depends_on: [gidney-carry-xor-repair]
---

# Dirty-half borrowing

Split an `n`-bit target into upper and lower halves. While updating one half, use the other half as the dirty target of carry-xor. After finishing and restoring it, reverse roles.

This supplies the `n-2` dirty qubits required by the `3n ± O(1)` design without a separate workspace register.

Borrowed data need not be zero, but must be restored exactly.
