---
id: "KB-KHA-03"
title: "What the Dialog encodes and transfer limitation"
paper: "arXiv:2510.10967v1"
paper_slug: "khattar-dialog-eea"
evidence: "PAPER"
knowledge_type: "transfer-boundary"
source_pages: "PDF pp. 10–13 and 39–41; Sec. II.C; Appendix C"
tags:
  - "reversible EEA"
  - "Bezout coefficients"
  - "Dialog representation"
  - "direct modular division"
  - "GF(2^b)"
  - "transfer-boundary"
related:
  - "KB-KHA-01"
  - "KB-KHA-02"
  - "KB-LIT-03"
  - "KB-HAN-02"
---

# KB-KHA-03 — What the Dialog encodes and transfer limitation

> Dialog records elementary EEA transitions, but its \(\mathrm{GF}(2^b)\) resource counts do not transfer directly to carry-based prime-field arithmetic.

The **Dialog** is the EEA execution trace represented as the ordered sequence of small invertible transition matrices. For the constant-time division-free construction, it is concretely the list of update coefficients \(c_i\) and conditional swap decisions. The name is also a mnemonic for the elementary operations:

- **D**oubling or shifting;
- **I**nversion or swapping;
- **A**ddition/subtraction;
- with the representation behaving somewhat like a **log** because multiplication and division are easy to express while addition is not.

For degree-\((n-1)\) polynomial inputs, the paper's Dialog has \(2n\) field elements. (pp. 10-13.)

**Why the numerical results do not directly transfer to large-prime integer arithmetic.** The resource analysis is for polynomial EEA and Reed-Solomon decoding over binary extension fields \(\mathrm{GF}(2^b)\). In characteristic two:

- addition is bitwise XOR;
- quantum-classical multiplication and squaring can be CNOT-only linear maps;
- the quoted multiplication, inversion, and MBU costs use specially optimized \(\mathrm{GF}(2^b)\) circuits.

Integer arithmetic modulo a large prime has carry propagation, integer comparison and reduction, different shift/division semantics, and different primitive costs. The **implicit-transition representation idea** is portable, but the paper's Toffoli and qubit totals are not portable without rebuilding the transition matrices, fixed-round schedule, and cost model for the integer domain. (Sec. II.C and Appendix C, pp. 13 and 39-41.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-KHA-01 — Explicit versus implicit Bézout access](explicit-vs-implicit-bezout.md)
- [KB-KHA-02 — Direct division without materializing \(B^{-1}\)](direct-division-by-dialog-replay.md)
- [KB-LIT-03 — Prime-field interface limitation](prime-field-interface-limit.md)
- [KB-HAN-02 — Fixed rounds and integrated pseudo-inverse correction](fixed-rounds-and-pseudoinverse-correction.md)

## Source

- [Tanuj Khattar et al., “Verifiable Quantum Advantage via Optimized DQI Circuits,” arXiv:2510.10967v1 (2025).](../sources/2510.10967v1.md)
- Location: PDF pp. 10–13 and 39–41; Sec. II.C; Appendix C
