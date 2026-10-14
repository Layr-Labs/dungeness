---
id: "KB-GID-03"
title: "Why an outer control adds no Toffolis"
paper: "arXiv:2507.23079v1"
paper_slug: "gidney-classical-quantum-adder"
evidence: "PAPER"
knowledge_type: "control-locality"
source_pages: "PDF p. 7; Sec. 2.4; Fig. 6"
tags:
  - "constant workspace"
  - "classical-quantum adder"
  - "venting"
  - "carry identity"
  - "free outer control"
  - "control-locality"
related:
  - "KB-GID-01"
  - "KB-LUO-03"
  - "KB-LIT-01"
---

# KB-GID-03 — Why an outer control adds no Toffolis

> The outer control substitutes for hardwired one-bits of the classical offset, adding no nonlinear gates in the paper’s accounting.

The classical offset enters the circuit through its bits \(d_k\). To control the whole addition:

- replace every hardwired \(d_k=0\) by 0;
- replace every hardwired \(d_k=1\) by the outer control qubit.

The \(d_k\) values are used only to invert controls or to control bit flips. Substituting the outer control into those positions does not promote any existing operation into a higher-controlled nonlinear gate, so the paper counts **no additional workspace and no additional Toffolis**. (Sec. 2.4, p. 7; Fig. 6.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-GID-01 — Principal workspace/Toffoli tradeoffs](workspace-toffoli-tradeoffs.md)
- [KB-LUO-03 — Where the external control is actually required](external-control-scope.md)
- [KB-LIT-01 — Replacement for shifted controlled addition](controlled-add-subtract.md)

## Source

- [Craig Gidney, “A Classical-Quantum Adder with Constant Workspace and Linear Gates,” arXiv:2507.23079v1 (2025).](../sources/2507.23079v1.md)
- Location: PDF p. 7; Sec. 2.4; Fig. 6
