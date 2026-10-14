---
kind: node
id: spooky-dag-and-tree
source: arXiv:2110.08973v3, section 5
depends_on: [spooky-ghosting-semantics]
---

# DAG hardness and binary trees

**[PAPER]**

- Approximating the minimum spooky pebble count on arbitrary bounded-indegree DAGs is PSPACE-hard.
- A complete binary tree with `n=2^h-1` nodes can be spooky-pebbled using `h+1` pebbles and `O(n log n)` steps.

Implication: exploit known topology. Do not expect a cheap generic optimizer to discover the best replay schedule.
