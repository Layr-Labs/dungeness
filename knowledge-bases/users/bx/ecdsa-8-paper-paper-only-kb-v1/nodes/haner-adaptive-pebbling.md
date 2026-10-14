---
kind: node
id: haner-adaptive-pebbling
source: IACR ePrint 2020/077
---

# Adaptive pebbling

The paper treats higher-level use sites, not arithmetic blocks, as the unit of uncomputation design.

Pattern:

```text
compute intermediate
consume it in the next operation
uncompute only after its final use
```

This can eliminate a copied result register and one full recomputation. It is the concrete integrated counterpart to abstract pebble-game scheduling.
