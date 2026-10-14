---
kind: node
id: gidney-carry-xor-repair
source: arXiv:2507.23079
depends_on: [gidney-carry-venting]
---

# Carry-xor phase repair

A carry-xor circuit computes:

```text
g -> g xor carry(x,d,c0)
```

Interleaving Z gates with the controlled flips transfers phase from `g` onto the carry predicate. A second carry-xor restores dirty workspace.

This converts the classical measurement record from venting into the exact coherent phase correction.
