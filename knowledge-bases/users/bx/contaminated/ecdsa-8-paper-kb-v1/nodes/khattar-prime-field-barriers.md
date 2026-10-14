---
kind: node
id: khattar-prime-field-barriers
source: cross-paper analysis
depends_on: [khattar-dialog-representation, khattar-direct-division]
---

# Prime-field Dialog barriers

The paper's EEA acts on polynomials over `GF(2^b)`. Secp256k1 requires integer prime-field arithmetic.

Missing pieces:

- a compact integer transition alphabet;
- reversible quotient/sign extraction;
- bounded coefficient representation;
- prime-field replay arithmetic;
- proof that the current branch signs are encoded elsewhere.

**[BENCHMARK]** In the present ping-pong recurrence, both sign preimages are valid, so post-step values do not reveal the discarded sign.
