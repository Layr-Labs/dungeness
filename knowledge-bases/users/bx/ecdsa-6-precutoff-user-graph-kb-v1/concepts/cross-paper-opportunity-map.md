# Cross-paper opportunity map

This page separates directly supported combinations from research hypotheses.

| Combination | Status | Rationale |
|---|---|---|
| Localize an external modular-addition control, then use a controlled classical-offset adder for fixed corrections | Strongly supported composition | [KB-LUO-03](../nodes/external-control-scope.md) identifies where caller control is semantically needed; [KB-GID-03](../nodes/outer-control-at-zero-toffoli.md) makes fixed-offset control cheap. |
| Track MBU, venting, and ghosting with one phase-debt scheduler | Architecture synthesis | The mechanisms differ, but all emit reusable qubits plus classical correction state. See [measurement synthesis](measurement-uncomputation-and-phase-debt.md). |
| Use controlled add-subtract inside a canonical in-place prime-field multiplier | Requires redesign | [KB-LIT-01](../nodes/controlled-add-subtract.md) supplies the primitive, but [KB-LIT-03](../nodes/prime-field-interface-limit.md) blocks direct import. |
| Replay an implicit EEA Dialog inside fixed-round prime-field inversion | Research hypothesis | [KB-KHA-02](../nodes/direct-division-by-dialog-replay.md) and [KB-HAN-02](../nodes/fixed-rounds-and-pseudoinverse-correction.md) are conceptually complementary but use different arithmetic domains and histories. |
| Fuse multiplication output into its consumer before cleanup | Direct architectural opportunity | [KB-HAN-03](../nodes/producer-consumer-and-workspace-reuse.md) gives an explicit construction; applicability depends on the caller’s map shape. |
| Use spooky pebbling to reduce arithmetic workspace without counting classical records | Invalid accounting | [KB-KSS-03](../nodes/live-classical-memory.md) requires the record to remain live. |

The word “supported” means the component claims are established by their papers. It does not prove that a combined circuit preserves the same headline cost.
