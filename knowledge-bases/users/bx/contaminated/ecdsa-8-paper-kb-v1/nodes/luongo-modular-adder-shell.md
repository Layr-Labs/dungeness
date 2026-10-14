---
kind: node
id: luongo-modular-adder-shell
source: arXiv:2407.20167, sections 3-4
depends_on: [luongo-single-qubit-mbu]
---

# MBU modular-adder shell

The standard shell computes a sum, detects overflow relative to `p`, conditionally corrects by `p`, and uncomputes the comparison predicate.

**[PAPER]** MBU replaces the final coherent uncomputation of that one-bit predicate:

```text
CDKPM: 8n -> 7n expected
Gidney: 4n -> 3.5n expected
mixed:  6n -> 5.5n expected
```

The logical-qubit counts depend on the chosen underlying adder.
