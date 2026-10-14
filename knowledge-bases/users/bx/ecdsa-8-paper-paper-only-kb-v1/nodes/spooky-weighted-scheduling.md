---
kind: node
id: spooky-weighted-scheduling
source: cross-paper synthesis from arXiv:2110.08973v3
depends_on: [spooky-line-frontier, spooky-general-computation]
---

# Weighted scheduling interpretation

The spooky pebble game counts abstract pebbles and steps. Arithmetic
applications can refine this by attaching:

```text
state width
recomputation cost
measurement eligibility
phase-repair cost
dependency order
```

This weighted model is a synthesis layer; the paper's theorems apply directly
to the unweighted game.
