---
paper: "arXiv:2110.08973v3"
title: "Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements"
node_ids:
  - "KB-KSS-01"
  - "KB-KSS-02"
  - "KB-KSS-03"
---

# 4. Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements

Recycle qubits by replacing a computed value with a phase ghost indexed by retained classical measurement data.

## Fast facts

- **Representation:** reversible computation graph with quantum pebbles and classical ghosts
- **Cost model:** time-space pebbling bound; quantum and classical memory distinguished
- **Headline:** A line satisfying \(n\leq\binom{m+s-2}{s-2}+1\) admits an \(s\)-pebble, \(O(mn)\)-step strategy.
- **Import warning:** Quantum space is recycled, but the classical measurement record remains live until unghosting.

## Atomic nodes

| ID | Question or mechanism | Retrieval summary |
|---|---|---|
| [KB-KSS-01](../nodes/ghosting-transformation.md) | Ghosting transformation and precondition | Ghosting resets a quantum value while retaining a classical string that indexes the resulting phase; distinct labels prevent amplitude collisions. |
| [KB-KSS-02](../nodes/spooky-pebble-binomial-bound.md) | Binomial line-length relation | Binomial relations characterize the line length reachable with a bounded number of pebbles and a time parameter. |
| [KB-KSS-03](../nodes/live-classical-memory.md) | Memory that remains live | Recycled qubits leave behind a live classical measurement record and an unresolved phase obligation. |

## Suggested reading path

Read the three nodes in order when reconstructing the paper argument. When evaluating transfer into a different arithmetic stack, read [representation and interface contracts](../concepts/representation-and-interface-contracts.md) and [the circuit-import checklist](../concepts/import-checklist.md).

## Source

[Niels Kornerup, Jonathan Sadun, and David Soloveichik, “Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements,” arXiv:2110.08973v3.](../sources/2110.08973v3.md)

[Back to index](../index.md) · [Previous paper](03-gidney-classical-quantum-adder.md) · [Next paper](05-khattar-dialog-eea.md)
