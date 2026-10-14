---
kind: node
id: spooky-line-frontier
source: arXiv:2110.08973v3, Theorems 3.6 and 4.13
depends_on: [spooky-ghosting-semantics]
---

# Tight line frontier

**[PAPER]** For line length `n`, pebble bound `s`, and integer `m` satisfying:

```text
n <= binomial(m+s-2, s-2) + 1
```

there is an `s`-pebble spooky strategy using `O(mn)` steps. The paper proves an asymptotically matching lower bound.

This is the central schedule tradeoff used to compare qubit budgets.
