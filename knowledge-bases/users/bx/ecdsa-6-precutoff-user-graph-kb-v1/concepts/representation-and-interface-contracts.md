# Representation and interface contracts

Arithmetic gate counts are meaningful only after the surrounding representation and map shape are fixed.

## Representations in this corpus

| Representation | Relevant nodes | Import question |
|---|---|---|
| Ordinary binary integers | [KB-LIT-01](../nodes/controlled-add-subtract.md), [KB-GID-01](../nodes/workspace-toffoli-tradeoffs.md) | Is the operation modulo \(2^n\), full-width, or reduced modulo a prime? |
| Montgomery residues | [KB-LIT-03](../nodes/prime-field-interface-limit.md), [KB-HAN-02](../nodes/fixed-rounds-and-pseudoinverse-correction.md) | Who converts into and out of Montgomery form, and who owns scaling corrections? |
| Polynomial residues over \(\mathrm{GF}(2^b)\) | [KB-KHA-03](../nodes/dialog-and-prime-field-transfer-limit.md) | Which operations are linear/CNOT-only only because the characteristic is two? |
| Implicit EEA transition traces | [KB-KHA-01](../nodes/explicit-vs-implicit-bezout.md), [KB-KHA-02](../nodes/direct-division-by-dialog-replay.md) | Can every consumer be rewritten to replay the trace instead of reading coefficients? |

## Map-shape checklist

Before importing a component, record:

1. in-place or out-of-place;
2. canonical output or scaled/pseudo-inverse output;
3. clean output or garbage-producing output;
4. unitary-only or measurement-assisted;
5. exact cost or expected branch-weighted cost;
6. clean, dirty, quantum, and classical workspace separately.

The main failure mode is to compare an isolated low-cost primitive with an end-to-end API that also requires representation conversion, result copying, garbage cleanup, or phase repair.
