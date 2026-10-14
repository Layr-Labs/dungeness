---
id: "KB-LIT-01"
title: "Replacement for shifted controlled addition"
paper: "arXiv:2410.00899v1"
paper_slug: "litinski-schoolbook-multiplication"
evidence: "PAPER"
knowledge_type: "mechanism"
source_pages: "PDF pp. 1–2; Figs. 1–2"
tags:
  - "schoolbook multiplication"
  - "controlled add-subtract"
  - "Montgomery multiplication"
  - "Toffoli count"
  - "out-of-place"
  - "mechanism"
related:
  - "KB-LIT-02"
  - "KB-LUO-03"
  - "KB-GID-03"
---

# KB-LIT-01 — Replacement for shifted controlled addition

> A controlled add-subtract adds the shifted multiplicand for control 1 and subtracts it for control 0 at the cost of an uncontrolled adder.

**Answer.** Each shifted controlled addition is replaced by a **controlled add-subtract**. With control bit \(x_k\), it adds \(2^k y\) when \(x_k=1\), but subtracts \(2^k y\) when \(x_k=0\), represented in the enlarged positive-integer register as adding \(2^{n+k}-2^k y\). A controlled add-subtract has the Toffoli cost of an uncontrolled adder: \(n\) with carry-out or \(n-1\) without carry-out. (pp. 1-2, Figs. 1-2.)

For the \(k\)-th multiplication step, the amount added is

\[
(1-x_k)2^{n+k}+(2x_k-1)2^k y.
\]

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-LIT-02 — Exact intermediate expression and non-modular cost](intermediate-expression-and-cost.md)
- [KB-LUO-03 — Where the external control is actually required](external-control-scope.md)
- [KB-GID-03 — Why an outer control adds no Toffolis](outer-control-at-zero-toffoli.md)

## Source

- [Daniel Litinski, “Quantum schoolbook multiplication with fewer Toffoli gates,” arXiv:2410.00899v1 (2024).](../sources/2410.00899v1.md)
- Location: PDF pp. 1–2; Figs. 1–2
