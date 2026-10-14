---
id: "KB-GID-02"
title: "Carry identity used for venting"
paper: "arXiv:2507.23079v1"
paper_slug: "gidney-classical-quantum-adder"
evidence: "PAPER"
knowledge_type: "identity"
source_pages: "PDF p. 3; Eq. 8; Sec. 2.2"
tags:
  - "constant workspace"
  - "classical-quantum adder"
  - "venting"
  - "carry identity"
  - "free outer control"
  - "identity"
related:
  - "KB-GID-01"
  - "KB-LUO-01"
  - "KB-KSS-01"
  - "KB-KSS-03"
---

# KB-GID-02 — Carry identity used for venting

> The carry string can be reconstructed after addition, allowing X-basis measurement to replace carry garbage with deferred phase work.

Define

\[
x'=x+d+c_0
\]

and

\[
\operatorname{carry}(x,d,c_0)
=x\oplus d\oplus(x+d+c_0).
\]

The identity is

\[
\boxed{\operatorname{carry}(\sim x',d,c_0)
=\operatorname{carry}(x,d,c_0)}.
\]

Thus the carries can be recomputed from values available after the addition. They are "Z-redundant": measuring a carry qubit in the \(X\) basis frees the qubit, while a minus outcome leaves a known deferred phase-flip task. The paper calls this conversion from carry garbage into phase obligations **venting**. (Eq. 8 and Sec. 2.2, p. 3.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-GID-01 — Principal workspace/Toffoli tradeoffs](workspace-toffoli-tradeoffs.md)
- [KB-LUO-01 — The two branches of the one-bit MBU lemma](one-bit-mbu-branches.md)
- [KB-KSS-01 — Ghosting transformation and precondition](ghosting-transformation.md)
- [KB-KSS-03 — Memory that remains live](live-classical-memory.md)

## Source

- [Craig Gidney, “A Classical-Quantum Adder with Constant Workspace and Linear Gates,” arXiv:2507.23079v1 (2025).](../sources/2507.23079v1.md)
- Location: PDF p. 3; Eq. 8; Sec. 2.2
