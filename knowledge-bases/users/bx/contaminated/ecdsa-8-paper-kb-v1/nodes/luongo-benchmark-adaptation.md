---
kind: node
id: luongo-benchmark-adaptation
source: cross-paper inference
depends_on: [luongo-single-qubit-mbu, luongo-expected-cost-semantics]
---

# Luongo benchmark adaptation

**[INFERENCE]** First build a one-bit conformance circuit:

```text
compute g
MBU-delete g
retain measurement
repair phase
run explicit inverse
```

Test basis states, superpositions, and a mutation with one repair removed. If the mutation still passes, the test is not phase-sensitive enough.

Only after conformance should MBU target replay comparison, carry, or fold flags.
