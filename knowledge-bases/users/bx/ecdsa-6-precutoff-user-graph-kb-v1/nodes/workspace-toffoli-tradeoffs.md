---
id: "KB-GID-01"
title: "Principal workspace/Toffoli tradeoffs"
paper: "arXiv:2507.23079v1"
paper_slug: "gidney-classical-quantum-adder"
evidence: "PAPER"
knowledge_type: "tradeoff"
source_pages: "PDF pp. 1, 3, 7; Figs. 4–5"
tags:
  - "constant workspace"
  - "classical-quantum adder"
  - "venting"
  - "carry identity"
  - "free outer control"
  - "tradeoff"
related:
  - "KB-GID-02"
  - "KB-GID-03"
  - "KB-LUO-02"
  - "KB-HAN-03"
---

# KB-GID-01 — Principal workspace/Toffoli tradeoffs

> The principal operating points trade three clean ancillas for \(4n\) Toffolis or use \(n-2\) dirty ancillas to reach \(3n\).

The paper's two headline operating points are:

| Clean ancillas | Dirty ancillas | Toffoli cost |
|---:|---:|---:|
| 3 | 0 | \(\boxed{4n\pm O(1)}\) |
| 2 | \(n-2\) | \(\boxed{3n\pm O(1)}\) |

The second construction uses a dirty secondary register for carry-xor operations. The first obtains constant total workspace by splitting the target into two halves and letting each half borrow the other as dirty workspace at different stages. (pp. 1, 3, and 7; Figs. 4-5.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-GID-02 — Carry identity used for venting](carry-venting-identity.md)
- [KB-GID-03 — Why an outer control adds no Toffolis](outer-control-at-zero-toffoli.md)
- [KB-LUO-02 — Gidney modular-adder costs after MBU](gidney-modular-adder-costs.md)
- [KB-HAN-03 — Producer/consumer and workspace-reuse examples](producer-consumer-and-workspace-reuse.md)

## Source

- [Craig Gidney, “A Classical-Quantum Adder with Constant Workspace and Linear Gates,” arXiv:2507.23079v1 (2025).](../sources/2507.23079v1.md)
- Location: PDF pp. 1, 3, 7; Figs. 4–5
