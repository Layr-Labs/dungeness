# Location-controlled arithmetic

Luo et al. store several logical values in two physical work registers. Their
boundaries depend coherently on the input, so an operation must select a
location from a quantum length register.

## Two-level selection

1. The classical step number determines a possible interval `[k(T),K(T)]`.
2. A quantum length value selects the actual position within that interval.

Unary iteration realizes one selected swap, addition, subtraction, or length
update with cost linear in the interval span and logarithmic clean workspace.

## Tradeoff

```text
less persistent storage
+ moving logical boundaries
+ selection gates
+ length maintenance
+ circular-alignment logic
```

The liveness proof and the literal moving-value gate construction are separate
objects and can be studied independently.

## Nodes

- [`../nodes/luo-active-windows.md`](../nodes/luo-active-windows.md)
- [`../nodes/luo-unary-iteration.md`](../nodes/luo-unary-iteration.md)
- [`../nodes/luo-location-controlled-add-sub.md`](../nodes/luo-location-controlled-add-sub.md)
- [`../nodes/luo-dirty-length-update.md`](../nodes/luo-dirty-length-update.md)
