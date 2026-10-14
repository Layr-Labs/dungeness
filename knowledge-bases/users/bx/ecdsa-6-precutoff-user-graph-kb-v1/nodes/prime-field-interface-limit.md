---
id: "KB-LIT-03"
title: "Prime-field interface limitation"
paper: "arXiv:2410.00899v1"
paper_slug: "litinski-schoolbook-multiplication"
evidence: "PAPER"
knowledge_type: "transfer-boundary"
source_pages: "PDF pp. 2–4; Fig. 3"
tags:
  - "schoolbook multiplication"
  - "controlled add-subtract"
  - "Montgomery multiplication"
  - "Toffoli count"
  - "out-of-place"
  - "transfer-boundary"
related:
  - "KB-LIT-02"
  - "KB-KHA-03"
  - "KB-HAN-02"
---

# KB-LIT-03 — Prime-field interface limitation

> The prime multiplier is not a drop-in in-place canonical-field operation because it is out-of-place, Montgomery-form, and garbage-producing.

**Important limitation.** The paper's prime-modulus construction is an **out-of-place Montgomery-representation multiplier**. Its inputs are assumed to be stored in Montgomery form; each `ModMultStep` also contributes garbage, and full cleanup may require copying the result to another register and reversing the multiplier. (pp. 2-4, Fig. 3.)

Therefore it is not a drop-in implementation of an API such as

\[
|a\rangle_{\mathrm{canonical}}\longmapsto |a b\bmod p\rangle_{\mathrm{canonical}}
\]

performed in place. Importing it requires, at minimum, a representation plan for entering and leaving Montgomery form and a decision about the separate result and garbage registers. If the surrounding circuit requires a canonical residue after every operation, conversion and cleanup costs must be included.

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-LIT-02 — Exact intermediate expression and non-modular cost](intermediate-expression-and-cost.md)
- [KB-KHA-03 — What the Dialog encodes and transfer limitation](dialog-and-prime-field-transfer-limit.md)
- [KB-HAN-02 — Fixed rounds and integrated pseudo-inverse correction](fixed-rounds-and-pseudoinverse-correction.md)

## Source

- [Daniel Litinski, “Quantum schoolbook multiplication with fewer Toffoli gates,” arXiv:2410.00899v1 (2024).](../sources/2410.00899v1.md)
- Location: PDF pp. 2–4; Fig. 3
