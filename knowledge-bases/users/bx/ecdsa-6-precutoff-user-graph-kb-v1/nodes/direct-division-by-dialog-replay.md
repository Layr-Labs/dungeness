---
id: "KB-KHA-02"
title: "Direct division without materializing \\(B^{-1}\\)"
paper: "arXiv:2510.10967v1"
paper_slug: "khattar-dialog-eea"
evidence: "PAPER"
knowledge_type: "mechanism"
source_pages: "PDF p. 9; Table IV"
tags:
  - "reversible EEA"
  - "Bezout coefficients"
  - "Dialog representation"
  - "direct modular division"
  - "GF(2^b)"
  - "mechanism"
related:
  - "KB-KHA-01"
  - "KB-KHA-03"
  - "KB-HAN-01"
---

# KB-KHA-02 — Direct division without materializing \(B^{-1}\)

> Applying the EEA transition product to \([0,A]^T\) emits \(AB^{-1}\) directly without storing \(B^{-1}\).

Assume \(P\) is irreducible and \(\gcd(P,B)=1\). First execute the EEA on \((P,B)\) to obtain the ordered transition sequence \(\tau_1,\ldots,\tau_m\). Instead of extracting the Bézout polynomial \(B^{-1}\), apply

\[
\tau_{\mathrm{total}}
\]

to the different input vector

\[
\begin{bmatrix}0\\A\end{bmatrix}.
\]

Linearity gives

\[
\boxed{
\tau_{\mathrm{total}}
\begin{bmatrix}0\\A\end{bmatrix}
=
\begin{bmatrix}AB^{-1}\\0\end{bmatrix}
\pmod P
}.
\]

The quotient is produced directly by replaying the EEA transformations; no register ever holds the full inverse \(B^{-1}\). The paper reports a leading gate cost of \(4n^2\) underlying field multiplications for this implicit direct-division route, versus \(7n^2\) for its explicit invert-then-multiply route. (p. 9, Table IV.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-KHA-01 — Explicit versus implicit Bézout access](explicit-vs-implicit-bezout.md)
- [KB-KHA-03 — What the Dialog encodes and transfer limitation](dialog-and-prime-field-transfer-limit.md)
- [KB-HAN-01 — Normalizing the four Kaliski cases](normalized-kaliski-round.md)

## Source

- [Tanuj Khattar et al., “Verifiable Quantum Advantage via Optimized DQI Circuits,” arXiv:2510.10967v1 (2025).](../sources/2510.10967v1.md)
- Location: PDF p. 9; Table IV
