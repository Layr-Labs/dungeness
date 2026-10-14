---
kind: node
id: benchmark-adaptation
source: ecdsa.fail benchmark contract plus paper mapping
---

# Adaptation to ecdsa.fail

> Source-specific transfer note. The active implementation now uses ping-pong walk/replay;
> see [`../concepts/current-benchmark-architecture.md`](../concepts/current-benchmark-architecture.md).

Benchmark ABI:

```text
target_x: quantum 256-bit
target_y: quantum 256-bit
offset_x: classical 256-bit
offset_y: classical 256-bit
```

Transfers directly:

- affine algebra;
- in-place multiply/divide abstraction;
- Euclid history;
- delayed Bézout replay;
- register sharing;
- history compression;
- phase-specific adders;
- secp256k1 fold by `f`;
- measurement-based cleanup.

Does not transfer directly:

- `w=16` window index;
- lookup/unlookup circuits;
- compile-time constant point;
- paper resource totals as benchmark scores;
- nonzero random failure probability as acceptance criterion.

Recommended implementation target:

```text
port the in-place multiplier and arithmetic,
reuse the benchmark's existing top-level affine/classical-offset schedule
```

Validation requirements:

- all 9,024 benchmark shots;
- zero ancilla garbage;
- zero phase garbage;
- forward/reverse identity;
- lower product of average executed Toffoli and maximum referenced qubit ID plus one.
