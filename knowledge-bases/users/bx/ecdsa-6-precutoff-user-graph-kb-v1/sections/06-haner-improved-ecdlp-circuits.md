---
paper: "IACR ePrint 2020/077"
title: "Improved quantum circuits for elliptic curve discrete logarithms"
node_ids:
  - "KB-HAN-01"
  - "KB-HAN-02"
  - "KB-HAN-03"
---

# 6. Improved quantum circuits for elliptic curve discrete logarithms

Normalize four Kaliski branches into one swapped round body, run a fixed schedule, and fuse correction and cleanup.

## Fast facts

- **Representation:** Montgomery residues and reversible binary-GCD/Kaliski state
- **Cost model:** Toffoli/T-depth/qubit resource accounting at component and ECDLP levels
- **Headline:** Exactly \(2n\) scheduled inversion rounds; \(2n-k\) modular doublings repair the pseudo-inverse during reverse cleanup.
- **Import warning:** The inversion and multiplication stack uses Montgomery-form arithmetic and tightly coupled register lifetimes.

## Atomic nodes

| ID | Question or mechanism | Retrieval summary |
|---|---|---|
| [KB-HAN-01](../nodes/normalized-kaliski-round.md) | Normalizing the four Kaliski cases | Conditional swaps orient all four Kaliski cases into a single subtract/add, halve, and double round body. |
| [KB-HAN-02](../nodes/fixed-rounds-and-pseudoinverse-correction.md) | Fixed rounds and integrated pseudo-inverse correction | The circuit schedules \(2n\) rounds and performs the \(2n-k\) correction doublings concurrently with reverse cleanup. |
| [KB-HAN-03](../nodes/producer-consumer-and-workspace-reuse.md) | Producer/consumer and workspace-reuse examples | Consume a producer’s result before reversing its garbage, and reuse registers that temporarily hold known constants. |

## Suggested reading path

Read the three nodes in order when reconstructing the paper argument. When evaluating transfer into a different arithmetic stack, read [representation and interface contracts](../concepts/representation-and-interface-contracts.md) and [the circuit-import checklist](../concepts/import-checklist.md).

## Source

[Thomas Häner, Samuel Jaques, Michael Naehrig, Martin Roetteler, and Mathias Soeken, “Improved quantum circuits for elliptic curve discrete logarithms,” IACR ePrint 2020/077 (2020).](../sources/2020-077.md)

[Back to index](../index.md) · [Previous paper](05-khattar-dialog-eea.md)
