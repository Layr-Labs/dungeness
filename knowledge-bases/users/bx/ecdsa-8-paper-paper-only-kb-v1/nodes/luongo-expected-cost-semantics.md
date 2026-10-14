---
kind: node
id: luongo-expected-cost-semantics
source: arXiv:2407.20167
depends_on: [luongo-single-qubit-mbu]
---

# Expected-cost semantics

MBU resource formulas average a Bernoulli branch:

```text
E[cost] = fixed cost + 0.5 × repair-oracle cost
```

**[SYNTHESIS]** A faithful execution model must:

- preserves the measurement outcome;
- executes and charges the conditional branch per shot;
- handles phase correction exactly;
- uses an explicit reverse protocol.

A static emitted-gate total can therefore differ from the expected executed
cost claimed by the paper.
