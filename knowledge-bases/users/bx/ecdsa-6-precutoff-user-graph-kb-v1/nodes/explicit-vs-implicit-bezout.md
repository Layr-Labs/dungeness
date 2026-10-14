---
id: "KB-KHA-01"
title: "Explicit versus implicit Bézout access"
paper: "arXiv:2510.10967v1"
paper_slug: "khattar-dialog-eea"
evidence: "PAPER"
knowledge_type: "representation"
source_pages: "PDF pp. 8–13; Secs. II.B.1–3"
tags:
  - "reversible EEA"
  - "Bezout coefficients"
  - "Dialog representation"
  - "direct modular division"
  - "GF(2^b)"
  - "representation"
related:
  - "KB-KHA-02"
  - "KB-KHA-03"
  - "KB-HAN-01"
---

# KB-KHA-01 — Explicit versus implicit Bézout access

> Explicit access materializes the total Bézout matrix; implicit access keeps the EEA transition sequence executable.

Write each EEA step as a small transition matrix \(\tau_i\), with

\[
\tau_{\mathrm{total}}=\tau_m\tau_{m-1}\cdots\tau_1.
\]

- **Explicit access:** compute and store the full product \(\tau_{\mathrm{total}}\), including the coefficient arrays of the final Bézout polynomials. This is required when later logic needs the polynomial coefficients as ordinary data.

- **Implicit access:** store a compact representation of each \(\tau_i\), without multiplying the sequence into full Bézout polynomials. A consumer is rewritten to replay the transformations on an appropriate vector. The Bézout object exists as an executable transformation sequence, not as a materialized coefficient register.

Both approaches target leading-order space \(2nb+O(\log_2 n)\), but the implicit construction uses the cheaper constant-time, division-free EEA structure. (Secs. II.B.1-3, pp. 8-13.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-KHA-02 — Direct division without materializing \(B^{-1}\)](direct-division-by-dialog-replay.md)
- [KB-KHA-03 — What the Dialog encodes and transfer limitation](dialog-and-prime-field-transfer-limit.md)
- [KB-HAN-01 — Normalizing the four Kaliski cases](normalized-kaliski-round.md)

## Source

- [Tanuj Khattar et al., “Verifiable Quantum Advantage via Optimized DQI Circuits,” arXiv:2510.10967v1 (2025).](../sources/2510.10967v1.md)
- Location: PDF pp. 8–13; Secs. II.B.1–3
