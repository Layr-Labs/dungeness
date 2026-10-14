---
kind: node
id: luo-shared-work-registers
source: arXiv:2607.13816v2 section 3.2 and Figure 4
depends_on: [luo-four-phase-eea]
related: [luo-length-registers, luo-active-windows]
---

# Luo shared work registers

**[PAPER]** Remainders shrink while Bézout coefficients grow. The invariant:

```text
r_(i-1)*t_i + r_i*t_(i-1) = p
```

allows the two kinds of values to share storage.

Physical layout:

```text
Work1, n+3 qubits:
  little-endian t | big-endian partial q | big-endian r

Work2, n+3 qubits:
  little-endian t' and big-endian r'
```

`Work2` is circularly shifted during quotient processing. The low portion of `t'` may wrap to the opposite end, so logical adjacency is not always physical adjacency.

The paper improves the older two-value sharing observation by showing that `t`, partial `q`, and `r` can coexist in `Work1`, including the intermediate phase-2/phase-3 states.

**[INFERENCE]** The reusable idea is a liveness proof: if two values have complementary monotone size bounds, allocator sharing can be justified without assuming a typical input.
