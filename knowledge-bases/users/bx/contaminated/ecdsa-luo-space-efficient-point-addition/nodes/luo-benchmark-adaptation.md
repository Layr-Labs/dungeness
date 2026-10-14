---
kind: node
id: luo-benchmark-adaptation
source: arXiv:2607.13816v2 mapped to the ecdsa.fail benchmark contract
depends_on: [luo-resource-estimates, luo-hadamard-register-recycling]
related: [luo-hybridization-opportunities]
---

# Adapting Luo et al. to ecdsa.fail

**[BENCHMARK]** The relevant ABI has quantum target coordinates and runtime classical offset coordinates. The score is:

```text
average executed Toffoli * peak qubits
```

Likely transferable:

- whole-field Hadamard measurement and phase repair;
- proof-driven register lifetime sharing;
- dirty borrowing from inactive field slices;
- step-specific active spans;
- exact fixed-schedule reasoning;
- in-place division/multiplication dataflow.

Not directly transferable:

- signed-window and table-lookup wrapper;
- compile-time constant point-coordinate arithmetic;
- paper gate totals as benchmark scores;
- automatic inverse of a measurement/reset circuit;
- Qiskit block-counting assumptions.

Direct-port warning:

```text
70.10M * 835 ≈ 58.5B
```

This rough product is far above the existing several-billion-score regime even before adaptation.

First compatibility test:

```text
demolish one small reversible register with H-measure-reset,
repair its phase by recomputation,
then pass the benchmark's forward/reverse and phase checks
```

Only after that test should field-sized recycling be attempted.
