---
paper: "arXiv:2507.23079v1"
title: "A Classical-Quantum Adder with Constant Workspace and Linear Gates"
node_ids:
  - "KB-GID-01"
  - "KB-GID-02"
  - "KB-GID-03"
---

# 3. A Classical-Quantum Adder with Constant Workspace and Linear Gates

Vent carry garbage into deferred phase corrections and trade clean workspace for dirty borrowing.

## Fast facts

- **Representation:** quantum binary target plus classical addend
- **Cost model:** asymptotic Toffoli count with clean/dirty workspace split
- **Headline:** \(4n\pm O(1)\) with three clean ancillas, or \(3n\pm O(1)\) with two clean and \(n-2\) dirty ancillas.
- **Import warning:** The construction is a classical-offset adder; the measurement outcomes create phase-correction obligations.

## Atomic nodes

| ID | Question or mechanism | Retrieval summary |
|---|---|---|
| [KB-GID-01](../nodes/workspace-toffoli-tradeoffs.md) | Principal workspace/Toffoli tradeoffs | The principal operating points trade three clean ancillas for \(4n\) Toffolis or use \(n-2\) dirty ancillas to reach \(3n\). |
| [KB-GID-02](../nodes/carry-venting-identity.md) | Carry identity used for venting | The carry string can be reconstructed after addition, allowing X-basis measurement to replace carry garbage with deferred phase work. |
| [KB-GID-03](../nodes/outer-control-at-zero-toffoli.md) | Why an outer control adds no Toffolis | The outer control substitutes for hardwired one-bits of the classical offset, adding no nonlinear gates in the paper’s accounting. |

## Suggested reading path

Read the three nodes in order when reconstructing the paper argument. When evaluating transfer into a different arithmetic stack, read [representation and interface contracts](../concepts/representation-and-interface-contracts.md) and [the circuit-import checklist](../concepts/import-checklist.md).

## Source

[Craig Gidney, “A Classical-Quantum Adder with Constant Workspace and Linear Gates,” arXiv:2507.23079v1 (2025).](../sources/2507.23079v1.md)

[Back to index](../index.md) · [Previous paper](02-luongo-measurement-based-uncomputation.md) · [Next paper](04-kornerup-spooky-pebble-game.md)
