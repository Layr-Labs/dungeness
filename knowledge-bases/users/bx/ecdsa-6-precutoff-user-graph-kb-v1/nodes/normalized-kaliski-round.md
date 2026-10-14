---
id: "KB-HAN-01"
title: "Normalizing the four Kaliski cases"
paper: "IACR ePrint 2020/077"
paper_slug: "haner-improved-ecdlp-circuits"
evidence: "PAPER"
knowledge_type: "mechanism"
source_pages: "PDF pp. 8–9; Sec. 4.2; Figs. 6–7"
tags:
  - "Kaliski inversion"
  - "binary EEA"
  - "pseudo-inverse"
  - "Montgomery inverse"
  - "workspace reuse"
  - "mechanism"
related:
  - "KB-HAN-02"
  - "KB-KHA-01"
  - "KB-KHA-02"
---

# KB-HAN-01 — Normalizing the four Kaliski cases

> Conditional swaps orient all four Kaliski cases into a single subtract/add, halve, and double round body.

The original round has four branches depending on parity and ordering. The improved formulation uses a swap bit \(b_{\mathrm{swap}}\) to orient all cases into one shared body:

1. set \(b_{\mathrm{swap}}=0\);
2. if \(u\) is even and \(v\) is odd, **or** both are odd and \(u>v\), swap \(u\leftrightarrow v\) and \(r\leftrightarrow s\), then set \(b_{\mathrm{swap}}=1\);
3. if both oriented values are odd, perform
   \[
   v\leftarrow v-u,\qquad s\leftarrow r+s;
   \]
4. unconditionally perform
   \[
   v\leftarrow v/2,\qquad r\leftarrow 2r;
   \]
5. if \(b_{\mathrm{swap}}=1\), swap both pairs back.

Thus controlled swaps choose the register roles, while subtraction/addition, halving, and doubling appear only once in the round body. The lower auxiliary bit and the round-state bit \(m_i\) determine the swap. (Sec. 4.2, pp. 8-9; Figs. 6-7.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-HAN-02 — Fixed rounds and integrated pseudo-inverse correction](fixed-rounds-and-pseudoinverse-correction.md)
- [KB-KHA-01 — Explicit versus implicit Bézout access](explicit-vs-implicit-bezout.md)
- [KB-KHA-02 — Direct division without materializing \(B^{-1}\)](direct-division-by-dialog-replay.md)

## Source

- [Thomas Häner, Samuel Jaques, Michael Naehrig, Martin Roetteler, and Mathias Soeken, “Improved quantum circuits for elliptic curve discrete logarithms,” IACR ePrint 2020/077 (2020).](../sources/2020-077.md)
- Location: PDF pp. 8–9; Sec. 4.2; Figs. 6–7
