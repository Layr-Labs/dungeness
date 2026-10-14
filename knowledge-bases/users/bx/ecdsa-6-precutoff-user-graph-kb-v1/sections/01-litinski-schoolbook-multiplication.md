---
paper: "arXiv:2410.00899v1"
title: "Quantum schoolbook multiplication with fewer Toffoli gates"
node_ids:
  - "KB-LIT-01"
  - "KB-LIT-02"
  - "KB-LIT-03"
---

# 1. Quantum schoolbook multiplication with fewer Toffoli gates

Replace shifted controlled additions by controlled add-subtract operations and repair the aggregate affine offset globally.

## Fast facts

- **Representation:** binary integers; Montgomery residues for the prime-modulus construction
- **Cost model:** exact Toffoli count
- **Headline:** Non-modular multiplier: \(n^2+4n+3\) Toffolis.
- **Import warning:** The prime-modulus construction is out-of-place, uses Montgomery representation, and produces garbage.

## Atomic nodes

| ID | Question or mechanism | Retrieval summary |
|---|---|---|
| [KB-LIT-01](../nodes/controlled-add-subtract.md) | Replacement for shifted controlled addition | A controlled add-subtract adds the shifted multiplicand for control 1 and subtracts it for control 0 at the cost of an uncontrolled adder. |
| [KB-LIT-02](../nodes/intermediate-expression-and-cost.md) | Exact intermediate expression and non-modular cost | The affine intermediate value is globally corrected and shifted to obtain multiplication in \(n^2+4n+3\) Toffolis. |
| [KB-LIT-03](../nodes/prime-field-interface-limit.md) | Prime-field interface limitation | The prime multiplier is not a drop-in in-place canonical-field operation because it is out-of-place, Montgomery-form, and garbage-producing. |

## Suggested reading path

Read the three nodes in order when reconstructing the paper argument. When evaluating transfer into a different arithmetic stack, read [representation and interface contracts](../concepts/representation-and-interface-contracts.md) and [the circuit-import checklist](../concepts/import-checklist.md).

## Source

[Daniel Litinski, “Quantum schoolbook multiplication with fewer Toffoli gates,” arXiv:2410.00899v1 (2024).](../sources/2410.00899v1.md)

[Back to index](../index.md) · [Next paper](02-luongo-measurement-based-uncomputation.md)
