---
id: "KB-LUO-01"
title: "The two branches of the one-bit MBU lemma"
paper: "arXiv:2407.20167v1"
paper_slug: "luongo-measurement-based-uncomputation"
evidence: "PAPER"
knowledge_type: "mechanism"
source_pages: "PDF p. 35; Lemma 4.1"
tags:
  - "MBU lemma"
  - "modular addition"
  - "Gidney adder"
  - "controlled modular addition"
  - "expected Toffoli"
  - "mechanism"
related:
  - "KB-LUO-02"
  - "KB-GID-02"
  - "KB-KSS-01"
  - "KB-KSS-03"
---

# KB-LUO-01 — The two branches of the one-bit MBU lemma

> Outcome 0 erases the predicate for free; outcome 1 leaves phase kickback and invokes a self-adjoint XOR-oracle repair.

The lemma starts with

\[
\sum_x\alpha_x|x\rangle_A|g(x)\rangle_G
\]

and requires a self-adjoint oracle

\[
U_g|x\rangle_A|b\rangle_G
=|x\rangle_A|b\oplus g(x)\rangle_G.
\]

Apply \(H\) to \(G\) and measure \(G\) in the computational basis:

- **Outcome 0, probability \(1/2\):** the register is already uncomputed, leaving
  \[
  \sum_x\alpha_x|x\rangle_A|0\rangle_G.
  \]

- **Outcome 1, probability \(1/2\):** the data register carries the phase
  \[
  \sum_x\alpha_x(-1)^{g(x)}|x\rangle_A|1\rangle_G.
  \]
  The repair applies \(H\) to \(G\), then \(U_g\), then another \(H\) and a NOT on \(G\). Phase kickback cancels \((-1)^{g(x)}\) and resets \(G\) to \(|0\rangle\).

**Repair condition.** The plug-and-play statement depends on \(U_g\) being the self-adjoint XOR oracle above. The expected nonlinear cost is half the cost of invoking that repair oracle, because only the outcome-1 branch uses it. (Lemma 4.1, p. 35.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-LUO-02 — Gidney modular-adder costs after MBU](gidney-modular-adder-costs.md)
- [KB-GID-02 — Carry identity used for venting](carry-venting-identity.md)
- [KB-KSS-01 — Ghosting transformation and precondition](ghosting-transformation.md)
- [KB-KSS-03 — Memory that remains live](live-classical-memory.md)

## Source

- [Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar, and Adithya Sireesh, “Measurement-based uncomputation of quantum circuits for modular arithmetic,” arXiv:2407.20167v1 (2024).](../sources/2407.20167v1.md)
- Location: PDF p. 35; Lemma 4.1
