---
kind: node
id: gidney-constant-workspace-adder
source: arXiv:2507.23079
depends_on: [gidney-carry-venting, gidney-carry-xor-repair, gidney-dirty-half-borrowing]
---

# Constant-workspace classical adder

**[PAPER]**

```text
3 clean ancillas, 0 dirty:   4n ± O(1) Toffoli
2 clean ancillas, n-2 dirty: 3n ± O(1) Toffoli
```

Both add a known classical offset modulo `2^n` into a quantum target and have linear depth.

This closes the long-standing asymptotic gap between quantum-quantum and classical-quantum constant-workspace addition.
