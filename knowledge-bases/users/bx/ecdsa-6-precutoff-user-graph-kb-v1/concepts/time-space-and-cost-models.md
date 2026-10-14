# Time-space and cost models

The corpus reports incompatible resource currencies.

| Node | Primary resource statement |
|---|---|
| [KB-LIT-02](../nodes/intermediate-expression-and-cost.md) | Exact Toffoli count |
| [KB-LUO-02](../nodes/gidney-modular-adder-costs.md) | Expected Toffoli count |
| [KB-GID-01](../nodes/workspace-toffoli-tradeoffs.md) | Toffolis versus clean/dirty ancillas |
| [KB-KSS-02](../nodes/spooky-pebble-binomial-bound.md) | Pebbles versus recomputation time |
| [KB-KHA-03](../nodes/dialog-and-prime-field-transfer-limit.md) | Field-specific operation counts |
| [KB-HAN-03](../nodes/producer-consumer-and-workspace-reuse.md) | End-to-end savings from changed lifetimes |

## Normalization procedure

1. Choose a primitive gate library and measurement model.
2. Separate exact from expected costs.
3. Split clean, dirty, quantum, and classical memory.
4. Include representation conversion and garbage cleanup.
5. Preserve circuit lifetime effects instead of summing only black-box routine costs.
6. State whether counts are worst-case, average-case, or asymptotic.

Without this translation, a lower number may simply be denominated in a cheaper primitive or omit an interface obligation.
