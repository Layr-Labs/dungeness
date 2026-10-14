---
kind: node
id: khattar-benchmark-adaptation
source: cross-paper inference
depends_on: [khattar-explicit-vs-implicit-bezout, khattar-prime-field-barriers]
---

# Khattar benchmark adaptation

**[INFERENCE]** Begin with a paper study, not a full circuit:

1. write the current walk as invertible matrices conditioned on sign;
2. prove what side information determines each matrix;
3. estimate compressed side-channel entropy;
4. price prime-field Dialog replay;
5. compare with the current tape plus interleaving.

A coding attempt without step 2 will reproduce the known non-recomputability barrier.
