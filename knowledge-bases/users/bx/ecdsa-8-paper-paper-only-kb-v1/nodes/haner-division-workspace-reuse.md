---
kind: node
id: haner-division-workspace-reuse
source: IACR ePrint 2020/077
depends_on: [haner-pseudoinverse-correction]
---

# Division workspace reuse

Rather than retain an inverse and its auxiliaries while allocating a multiplier, clear/restructure the inversion workspace and reuse those qubits for multiplication.

This reduces peak width without changing the mathematical invert-then-multiply decomposition.

It is a direct example of why lifetime diagrams matter more than summing standalone primitive widths.
