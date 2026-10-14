---
paper: "arXiv:2407.20167v1"
title: "Measurement-based uncomputation of quantum circuits for modular arithmetic"
node_ids:
  - "KB-LUO-01"
  - "KB-LUO-02"
  - "KB-LUO-03"
---

# 2. Measurement-based uncomputation of quantum circuits for modular arithmetic

Measure a one-bit predicate, accept the free branch, and invoke a self-adjoint repair computation only on the phase-error branch.

## Fast facts

- **Representation:** binary modular arithmetic with measurement and classical feed-forward
- **Cost model:** expected Toffoli count
- **Headline:** Expected costs: \(3.5n\) for Gidney modular addition and \(4.5n+0.5\) for its controlled form.
- **Import warning:** The repair must implement the one-bit self-adjoint XOR-oracle contract; expected cost assumes equiprobable measurement branches.

## Atomic nodes

| ID | Question or mechanism | Retrieval summary |
|---|---|---|
| [KB-LUO-01](../nodes/one-bit-mbu-branches.md) | The two branches of the one-bit MBU lemma | Outcome 0 erases the predicate for free; outcome 1 leaves phase kickback and invokes a self-adjoint XOR-oracle repair. |
| [KB-LUO-02](../nodes/gidney-modular-adder-costs.md) | Gidney modular-adder costs after MBU | MBU lowers the expected costs to \(3.5n\) and \(4.5n+0.5\) Toffolis for uncontrolled and controlled modular addition. |
| [KB-LUO-03](../nodes/external-control-scope.md) | Where the external control is actually required | Only the initial addition and final flag-erasing comparison require the caller’s control. |

## Suggested reading path

Read the three nodes in order when reconstructing the paper argument. When evaluating transfer into a different arithmetic stack, read [representation and interface contracts](../concepts/representation-and-interface-contracts.md) and [the circuit-import checklist](../concepts/import-checklist.md).

## Source

[Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar, and Adithya Sireesh, “Measurement-based uncomputation of quantum circuits for modular arithmetic,” arXiv:2407.20167v1 (2024).](../sources/2407.20167v1.md)

[Back to index](../index.md) · [Previous paper](01-litinski-schoolbook-multiplication.md) · [Next paper](03-gidney-classical-quantum-adder.md)
