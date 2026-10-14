---
paper: "arXiv:2510.10967v1"
title: "Verifiable Quantum Advantage via Optimized DQI Circuits"
node_ids:
  - "KB-KHA-01"
  - "KB-KHA-02"
  - "KB-KHA-03"
---

# 5. Verifiable Quantum Advantage via Optimized DQI Circuits

Represent the EEA as an executable transition trace (“Dialog”) and replay it on a different vector to divide directly.

## Fast facts

- **Representation:** polynomials and transition matrices over \(\mathrm{GF}(2^b)\)
- **Cost model:** underlying field-operation counts and circuit costs specialized to binary extension fields
- **Headline:** Direct division applies the EEA transition product to \([0,A]^T\), avoiding a materialized \(B^{-1}\).
- **Import warning:** The quantitative analysis is specialized to polynomial arithmetic over \(\mathrm{GF}(2^b)\), not large-prime integer arithmetic.

## Atomic nodes

| ID | Question or mechanism | Retrieval summary |
|---|---|---|
| [KB-KHA-01](../nodes/explicit-vs-implicit-bezout.md) | Explicit versus implicit Bézout access | Explicit access materializes the total Bézout matrix; implicit access keeps the EEA transition sequence executable. |
| [KB-KHA-02](../nodes/direct-division-by-dialog-replay.md) | Direct division without materializing \(B^{-1}\) | Applying the EEA transition product to \([0,A]^T\) emits \(AB^{-1}\) directly without storing \(B^{-1}\). |
| [KB-KHA-03](../nodes/dialog-and-prime-field-transfer-limit.md) | What the Dialog encodes and transfer limitation | Dialog records elementary EEA transitions, but its \(\mathrm{GF}(2^b)\) resource counts do not transfer directly to carry-based prime-field arithmetic. |

## Suggested reading path

Read the three nodes in order when reconstructing the paper argument. When evaluating transfer into a different arithmetic stack, read [representation and interface contracts](../concepts/representation-and-interface-contracts.md) and [the circuit-import checklist](../concepts/import-checklist.md).

## Source

[Tanuj Khattar et al., “Verifiable Quantum Advantage via Optimized DQI Circuits,” arXiv:2510.10967v1 (2025).](../sources/2510.10967v1.md)

[Back to index](../index.md) · [Previous paper](04-kornerup-spooky-pebble-game.md) · [Next paper](06-haner-improved-ecdlp-circuits.md)
