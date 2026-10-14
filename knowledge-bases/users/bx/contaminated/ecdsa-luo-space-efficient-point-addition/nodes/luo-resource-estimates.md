---
kind: node
id: luo-resource-estimates
source: arXiv:2607.13816v2 section 6
depends_on: [luo-space-efficient-modular-inversion, luo-in-place-division, luo-in-place-multiplication]
related: [luo-benchmark-adaptation, luo-hybridization-opportunities]
---

# Luo et al. resource estimates

**[PAPER]**

```text
inversion width:
  2n + 6 floor(log2 n) + 19

point-add width:
  3n + 6 floor(log2 n) + 19

forward inversion:
  <216.636n^2 + O(n log n) Toffoli
  <273.795n^2 + O(n log n) CNOT

point addition:
  <1003n^2 + O(n log n) Toffoli
```

At `n=256`:

```text
inversion: 579 q, 30.59M Toffoli, 43.39M CNOT
point add: 835 q, 70.10M Toffoli, 108.09M CNOT
```

Full signed-window ECDLP:

```text
1008n^3/log2(n) + O(n^2)
```

Concrete secp256k1 estimate:

```text
28*(5*2^16 + 70.10M) ≈ 2^30.88
```

Source correction: one Section-6.4 sentence gives `2^30.63`, but the formula, abstract, and comparison table imply `2^30.88`.

Interpretation: this is a qubit-minimizing point. It should not be compared with a low-gate design on qubits alone.
