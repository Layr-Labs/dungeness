---
id: "KB-LUO-02"
title: "Gidney modular-adder costs after MBU"
paper: "arXiv:2407.20167v1"
paper_slug: "luongo-measurement-based-uncomputation"
evidence: "PAPER"
knowledge_type: "exact-result"
source_pages: "PDF pp. 36, 38–39; Theorems 4.4 and 4.9"
tags:
  - "MBU lemma"
  - "modular addition"
  - "Gidney adder"
  - "controlled modular addition"
  - "expected Toffoli"
  - "exact-result"
related:
  - "KB-LUO-01"
  - "KB-LUO-03"
  - "KB-GID-01"
---

# KB-LUO-02 — Gidney modular-adder costs after MBU

> MBU lowers the expected costs to \(3.5n\) and \(4.5n+0.5\) Toffolis for uncontrolled and controlled modular addition.

The reported expected costs are:

| Construction | Expected Toffoli cost | Ancillas |
|---|---:|---:|
| Gidney modular adder | \(\boxed{3.5n}\) | \(2n+3\) |
| Gidney controlled modular adder | \(\boxed{4.5n+0.5}\) | \(2n+3\) |

For the uncontrolled circuit the decomposition is

\[
n+n+n+\frac{n}{2}=3.5n.
\]

For the controlled circuit it is

\[
2n+n+n+\frac{n+1}{2}=4.5n+0.5.
\]

The halved term is the final comparator used to erase the reduction flag. (Theorems 4.4 and 4.9, pp. 36 and 38-39.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-LUO-01 — The two branches of the one-bit MBU lemma](one-bit-mbu-branches.md)
- [KB-LUO-03 — Where the external control is actually required](external-control-scope.md)
- [KB-GID-01 — Principal workspace/Toffoli tradeoffs](workspace-toffoli-tradeoffs.md)

## Source

- [Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar, and Adithya Sireesh, “Measurement-based uncomputation of quantum circuits for modular arithmetic,” arXiv:2407.20167v1 (2024).](../sources/2407.20167v1.md)
- Location: PDF pp. 36, 38–39; Theorems 4.4 and 4.9
