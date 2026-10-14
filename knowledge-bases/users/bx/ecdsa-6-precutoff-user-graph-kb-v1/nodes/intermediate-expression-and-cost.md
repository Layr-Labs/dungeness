---
id: "KB-LIT-02"
title: "Exact intermediate expression and non-modular cost"
paper: "arXiv:2410.00899v1"
paper_slug: "litinski-schoolbook-multiplication"
evidence: "PAPER"
knowledge_type: "exact-result"
source_pages: "PDF pp. 1–2; Table 1; Fig. 2"
tags:
  - "schoolbook multiplication"
  - "controlled add-subtract"
  - "Montgomery multiplication"
  - "Toffoli count"
  - "out-of-place"
  - "exact-result"
related:
  - "KB-LIT-01"
  - "KB-LIT-03"
---

# KB-LIT-02 — Exact intermediate expression and non-modular cost

> The affine intermediate value is globally corrected and shifted to obtain multiplication in \(n^2+4n+3\) Toffolis.

After all \(n\) controlled add-subtract operations, the paper gives the intermediate value

\[
\sum_{k=0}^{n-1}\left((1-x_k)2^{n+k}+(2x_k-1)2^k y\right)
=2xy+2^{2n}-2^n(x+1+y)+y.
\]

The global corrections are:

1. add \(2^n(x+1)\);
2. subtract \(2^{2n}+y\);
3. add \(2^n y\);
4. divide by two by relabeling the qubits.

The reported total for the non-modular, \(2n\)-bit-output schoolbook multiplier is

\[
\boxed{n^2+4n+3\ \text{Toffoli gates}}.
\]

This is compared with \(2n^2+n\) for the controlled-adder construction. (pp. 1-2, Table 1 and Fig. 2.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-LIT-01 — Replacement for shifted controlled addition](controlled-add-subtract.md)
- [KB-LIT-03 — Prime-field interface limitation](prime-field-interface-limit.md)

## Source

- [Daniel Litinski, “Quantum schoolbook multiplication with fewer Toffoli gates,” arXiv:2410.00899v1 (2024).](../sources/2410.00899v1.md)
- Location: PDF pp. 1–2; Table 1; Fig. 2
