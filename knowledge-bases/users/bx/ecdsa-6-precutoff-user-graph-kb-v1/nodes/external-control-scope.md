---
id: "KB-LUO-03"
title: "Where the external control is actually required"
paper: "arXiv:2407.20167v1"
paper_slug: "luongo-measurement-based-uncomputation"
evidence: "PAPER"
knowledge_type: "control-locality"
source_pages: "PDF p. 28; Proposition 3.9"
tags:
  - "MBU lemma"
  - "modular addition"
  - "Gidney adder"
  - "controlled modular addition"
  - "expected Toffoli"
  - "control-locality"
related:
  - "KB-LUO-02"
  - "KB-LIT-01"
  - "KB-GID-03"
---

# KB-LUO-03 — Where the external control is actually required

> Only the initial addition and final flag-erasing comparison require the caller’s control.

Only two of the four high-level subroutines need the **external** control \(c\):

1. the first addition, producing \(c x+y\);
2. the final comparison used to uncompute the reduction flag.

The middle comparison against \(p\) is unconditional. The subtraction of \(p\) is controlled by the internally computed comparison/reduction flag, not directly by \(c\). This is why controlling every gate or every modular-adder subroutine would over-control the circuit. (Proposition 3.9, p. 28.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-LUO-02 — Gidney modular-adder costs after MBU](gidney-modular-adder-costs.md)
- [KB-LIT-01 — Replacement for shifted controlled addition](controlled-add-subtract.md)
- [KB-GID-03 — Why an outer control adds no Toffolis](outer-control-at-zero-toffoli.md)

## Source

- [Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar, and Adithya Sireesh, “Measurement-based uncomputation of quantum circuits for modular arithmetic,” arXiv:2407.20167v1 (2024).](../sources/2407.20167v1.md)
- Location: PDF p. 28; Proposition 3.9
