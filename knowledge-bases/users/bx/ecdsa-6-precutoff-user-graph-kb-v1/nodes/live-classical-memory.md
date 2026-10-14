---
id: "KB-KSS-03"
title: "Memory that remains live"
paper: "arXiv:2110.08973v3"
paper_slug: "kornerup-spooky-pebble-game"
evidence: "PAPER"
knowledge_type: "transfer-boundary"
source_pages: "PDF pp. 2 and 5–6"
tags:
  - "spooky pebble game"
  - "ghosting"
  - "measurement record"
  - "time-space tradeoff"
  - "binomial bound"
  - "transfer-boundary"
related:
  - "KB-KSS-01"
  - "KB-KSS-02"
  - "KB-LUO-01"
  - "KB-GID-02"
---

# KB-KSS-03 — Memory that remains live

> Recycled qubits leave behind a live classical measurement record and an unresolved phase obligation.

The recycled qubits do not eliminate the full memory obligation. The measurement bitstring \(b\) must remain in **classical ancillary memory** from ghosting until the original value can be recomputed and the phase can be removed. Correspondingly, the paper reduces quantum memory but not total memory measured as classical bits plus qubits. (pp. 2, 5-6.)

Operationally, a ghosted register has two pieces of outstanding state:

1. a reusable standard-basis qubit register;
2. a classical record describing the phase correction that must eventually be discharged.

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-KSS-01 — Ghosting transformation and precondition](ghosting-transformation.md)
- [KB-KSS-02 — Binomial line-length relation](spooky-pebble-binomial-bound.md)
- [KB-LUO-01 — The two branches of the one-bit MBU lemma](one-bit-mbu-branches.md)
- [KB-GID-02 — Carry identity used for venting](carry-venting-identity.md)

## Source

- [Niels Kornerup, Jonathan Sadun, and David Soloveichik, “Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements,” arXiv:2110.08973v3.](../sources/2110.08973v3.md)
- Location: PDF pp. 2 and 5–6
