---
kind: node
id: luo-hadamard-register-recycling
source: arXiv:2607.13816v2 section 5 and Figure 15
depends_on: [measurement-based-uncomputation]
related: [luo-in-place-division, luo-in-place-multiplication]
---

# Hadamard-basis field-register recycling

Suppose an old `n`-bit value `y` has become logically redundant, while enough surviving data remains to recompute it.

**[PAPER]** Recycling protocol:

```text
1. apply H to every qubit of |y>
2. measure outcome b and reset the register to |0>
3. continue using the clean register as workspace
4. later recompute |y> from surviving quantum data
5. apply Z on bit i when b_i=1
6. uncompute the recomputed y
```

The Hadamard measurement induces:

```text
(-1)^(b dot y)
```

The classically controlled `Z^b` on the recomputed value contributes the same factor, so the phase cancels.

Requirements:

- `y` must be exactly recomputable;
- every outcome bit must remain available until correction;
- the circuit IR must preserve classically controlled phase semantics;
- the inverse API must explicitly account for measurements and resets.

This generalizes one-bit measurement-based uncomputation to demolition and recycling of a complete field register.

