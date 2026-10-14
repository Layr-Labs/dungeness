---
kind: node
id: measurement-based-uncomputation
source: paper sections 2 and 4; companion util.py
---

# Measurement-based uncomputation

Used to erase AND/comparator outputs at reduced expected non-Clifford cost.

Pattern:

```text
Hadamard output
measure output
conditionally apply correction circuit
restore/release output
```

The expensive correction runs with probability about one half.

Benefits:

- lower average Toffoli count;
- especially useful for Gidney adders and comparison outputs.

Requirements:

- exact phase correction;
- supported measurement semantics;
- output wire physically clean before release.

Incorrect MBU can preserve classical outputs while leaving phase garbage.
