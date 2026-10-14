---
id: "KB-KSS-01"
title: "Ghosting transformation and precondition"
paper: "arXiv:2110.08973v3"
paper_slug: "kornerup-spooky-pebble-game"
evidence: "PAPER"
knowledge_type: "mechanism"
source_pages: "PDF pp. 4–5"
tags:
  - "spooky pebble game"
  - "ghosting"
  - "measurement record"
  - "time-space tradeoff"
  - "binomial bound"
  - "mechanism"
related:
  - "KB-KSS-02"
  - "KB-KSS-03"
  - "KB-LUO-01"
  - "KB-GID-02"
---

# KB-KSS-01 — Ghosting transformation and precondition

> Ghosting resets a quantum value while retaining a classical string that indexes the resulting phase; distinct labels prevent amplitude collisions.

A circuit \(C\) ghosts a register if it implements

\[
\boxed{
\sum_i\alpha_i|x_i\rangle|y_i\rangle
\xrightarrow{C}
\sum_i\alpha_i(-1)^{b\cdot y_i}|x_i\rangle|0\rangle
}
\]

while returning \(b\) as a classical bitstring. The logical value \(y_i\) has been erased from the qubits and replaced by a phase depending on the retained measurement record. (p. 4.)

**Precondition.** The labels \(x_i\) must be pairwise distinct. Without that condition, different basis components can collapse onto the same \(|x\rangle|0\rangle\) state and interfere, so the proposed map need not preserve the norm. The distinct-label condition prevents that collision. (pp. 4-5.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-KSS-02 — Binomial line-length relation](spooky-pebble-binomial-bound.md)
- [KB-KSS-03 — Memory that remains live](live-classical-memory.md)
- [KB-LUO-01 — The two branches of the one-bit MBU lemma](one-bit-mbu-branches.md)
- [KB-GID-02 — Carry identity used for venting](carry-venting-identity.md)

## Source

- [Niels Kornerup, Jonathan Sadun, and David Soloveichik, “Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements,” arXiv:2110.08973v3.](../sources/2110.08973v3.md)
- Location: PDF pp. 4–5
