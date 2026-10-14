# Measurement uncomputation and phase debt

Three papers use the same broad move: recycle quantum storage now and postpone a classically indexed phase correction.

| Mechanism | What is measured/recycled | What remains live |
|---|---|---|
| One-bit MBU | A Boolean predicate qubit | A branch bit and, on one branch, a repair call |
| Carry venting | Carry qubits | Minus-outcome records and reconstructible carry-phase tasks |
| Ghosting | A multi-bit computed value | A classical bitstring indexing a phase |

Entry nodes:

- [KB-LUO-01](../nodes/one-bit-mbu-branches.md)
- [KB-GID-02](../nodes/carry-venting-identity.md)
- [KB-KSS-01](../nodes/ghosting-transformation.md)
- [KB-KSS-03](../nodes/live-classical-memory.md)

## Shared scheduling rule

Treat a measurement-assisted erasure as producing two outputs:

1. reusable qubits;
2. a phase-debt record.

The record must name the measured function, the classical outcome, the recomputation needed for repair, and the deadline before the affected state is used in a basis where the phase matters.

## Important distinction

These methods reduce live quantum workspace. They do not necessarily reduce total memory or eliminate work. MBU can lower expected nonlinear cost; venting and ghosting can relocate uncomputation into later recomputation and classical tracking.
