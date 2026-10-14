---
id: "KB-HAN-03"
title: "Producer/consumer and workspace-reuse examples"
paper: "IACR ePrint 2020/077"
paper_slug: "haner-improved-ecdlp-circuits"
evidence: "PAPER"
knowledge_type: "lifetime-optimization"
source_pages: "PDF pp. 7–10; Secs. 4.1–4.2; Figs. 5 and 8"
tags:
  - "Kaliski inversion"
  - "binary EEA"
  - "pseudo-inverse"
  - "Montgomery inverse"
  - "workspace reuse"
  - "lifetime-optimization"
related:
  - "KB-HAN-02"
  - "KB-GID-01"
  - "KB-KSS-03"
---

# KB-HAN-03 — Producer/consumer and workspace-reuse examples

> Consume a producer’s result before reversing its garbage, and reuse registers that temporarily hold known constants.

**Producer/consumer fusion.** To compute \(xy+z\), the paper keeps the multiplication's auxiliary state alive, replaces Bennett's result-copy CNOT layer by the addition into \(z\), and only then reverses the multiplier. The cost becomes one multiplication plus one addition, rather than two multiplications plus one addition. Applied to squaring followed by subtraction in point addition, this saves almost half the squaring cost and depth and removes an auxiliary register. (Sec. 4.1, p. 7; Fig. 5.)

**Workspace reuse.** After modular inversion, three registers contain known values \(0\), \(1\), and \(p\). The circuit clears them with at most \(3n\) parallel X gates and reuses their qubits as the workspace for modular multiplication before completing inversion uncomputation. (Sec. 4.2, pp. 8-10; Fig. 8.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-HAN-02 — Fixed rounds and integrated pseudo-inverse correction](fixed-rounds-and-pseudoinverse-correction.md)
- [KB-GID-01 — Principal workspace/Toffoli tradeoffs](workspace-toffoli-tradeoffs.md)
- [KB-KSS-03 — Memory that remains live](live-classical-memory.md)

## Source

- [Thomas Häner, Samuel Jaques, Michael Naehrig, Martin Roetteler, and Mathias Soeken, “Improved quantum circuits for elliptic curve discrete logarithms,” IACR ePrint 2020/077 (2020).](../sources/2020-077.md)
- Location: PDF pp. 7–10; Secs. 4.1–4.2; Figs. 5 and 8
