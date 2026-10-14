---
kind: node
id: gidney-carry-venting
source: arXiv:2507.23079
depends_on: [gidney-z-redundant-carries]
---

# Carry venting

As the ripple moves upward, an old carry becomes garbage. Measure it in the X basis:

```text
|+> outcome -> value removed
|-> outcome -> value removed plus a carry-dependent phase
```

The measurement outcome is stored classically as a deferred phase task. This lets a streaming adder use only two clean qubits before phase repair.
