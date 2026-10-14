---
id: "KB-HAN-02"
title: "Fixed rounds and integrated pseudo-inverse correction"
paper: "IACR ePrint 2020/077"
paper_slug: "haner-improved-ecdlp-circuits"
evidence: "PAPER"
knowledge_type: "schedule"
source_pages: "PDF p. 8; Sec. 4.2"
tags:
  - "Kaliski inversion"
  - "binary EEA"
  - "pseudo-inverse"
  - "Montgomery inverse"
  - "workspace reuse"
  - "schedule"
related:
  - "KB-HAN-01"
  - "KB-HAN-03"
  - "KB-LIT-03"
  - "KB-KHA-03"
---

# KB-HAN-02 — Fixed rounds and integrated pseudo-inverse correction

> The circuit schedules \(2n\) rounds and performs the \(2n-k\) correction doublings concurrently with reverse cleanup.

For \(n\)-bit inputs, the classical Kaliski execution uses some \(k\) with

\[
n\leq k\leq 2n.
\]

The reversible circuit always executes \(\boxed{2n}\) scheduled rounds; only \(k\) rounds modify the EEA state. A counter records \(2n-k\), and the initial output is the pseudo-inverse

\[
x^{-1}2^{-n+k}\pmod p.
\]

The desired Montgomery inverse is

\[
x^{-1}2^n\pmod p,
\]

so the copied output needs exactly \(2n-k\) modular doublings.

The paper folds these doublings into inverse-circuit cleanup. During reversal of the \(2n\) rounds, the same round control selects either:

- uncomputing an active division round; or
- doubling the copied output for an inactive round.

These operations can run in parallel, so the variable correction is completed during cleanup without a separate correction pass or an increase in total gate count. (Sec. 4.2, p. 8.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-HAN-01 — Normalizing the four Kaliski cases](normalized-kaliski-round.md)
- [KB-HAN-03 — Producer/consumer and workspace-reuse examples](producer-consumer-and-workspace-reuse.md)
- [KB-LIT-03 — Prime-field interface limitation](prime-field-interface-limit.md)
- [KB-KHA-03 — What the Dialog encodes and transfer limitation](dialog-and-prime-field-transfer-limit.md)

## Source

- [Thomas Häner, Samuel Jaques, Michael Naehrig, Martin Roetteler, and Mathias Soeken, “Improved quantum circuits for elliptic curve discrete logarithms,” IACR ePrint 2020/077 (2020).](../sources/2020-077.md)
- Location: PDF p. 8; Sec. 4.2
