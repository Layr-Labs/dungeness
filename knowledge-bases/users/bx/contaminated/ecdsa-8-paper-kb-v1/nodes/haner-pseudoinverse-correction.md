---
kind: node
id: haner-pseudoinverse-correction
source: IACR ePrint 2020/077
depends_on: [haner-swap-normalized-kaliski]
---

# Pseudo-inverse correction

A fixed `2n`-round Kaliski run produces a power-of-two-scaled pseudo-inverse. The paper performs the required doubling correction in parallel with inverse uncomputation, using the round history to decide whether to correct or execute another reverse round.

The key idea is scheduling correction work inside an already necessary reverse traversal.
