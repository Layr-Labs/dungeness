---
kind: node
id: luo-uniform-step-bound
source: arXiv:2607.13816v2 section 3.1 and appendix A.1
depends_on: [luo-four-phase-eea]
related: [luo-active-windows, luo-space-efficient-modular-inversion]
---

# Uniform EEA step bound

**[PAPER]** Every nonzero input modulo an `n`-bit prime reaches the terminal EEA state within:

```text
T_max = 4 ceil(c n)
c = 3/log2(2+sqrt(3))
  ≈ 1.5789734406
```

Thus:

```text
T_max < 6.316n + 4
T_max(256) = 1620
```

The proof encodes quotient sequences as weighted products of `2x2` matrices. A computer-checkable finite polyhedral antinorm lower-bounds the growth of every admissible product; the critical normalized rate is:

```text
lambda = (2+sqrt(3))^(1/3)
```

This corrects the earlier `4.5n` claim associated with Proos–Zalka.

Why it matters: a quantum implementation cannot stop at an input-dependent time without retaining that stopping information. Repeating a fixed step circuit to `T_max` gives an exact coherent schedule and avoids a random-failure approximation.

