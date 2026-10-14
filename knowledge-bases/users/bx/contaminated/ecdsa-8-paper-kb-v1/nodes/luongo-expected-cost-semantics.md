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

**[INFERENCE]** This matches `ecdsa.fail` only if the evaluator:

- preserves the measurement outcome;
- executes and charges the conditional branch per shot;
- handles phase correction exactly;
- uses an explicit reverse protocol.

An emitted gate list can therefore misrepresent the canonical executed cost.
