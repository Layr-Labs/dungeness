---
kind: node
id: haner-montgomery-windowed-multiplication
source: IACR ePrint 2020/077, section 4.1
---

# Montgomery windowed multiplication

**[PAPER]** The multiplier groups multiplier bits into windows, looks up a classical multiple, adds it, and performs Montgomery add-and-halve reduction. Windowing trades lookup cost and width for fewer arithmetic rounds.

This is a mature generic-prime construction, but it does not exploit the secp256k1 pseudo-Mersenne modulus as directly as the current benchmark arithmetic.
