# EEA representations and inversion schedules

Khattar et al. and Häner et al. offer complementary ways to reason about reversible Euclidean algorithms.

## Executable history

[KB-KHA-01](../nodes/explicit-vs-implicit-bezout.md) separates materialized Bézout coefficients from an implicit sequence of elementary transition matrices. [KB-KHA-02](../nodes/direct-division-by-dialog-replay.md) shows that a consumer can replay that sequence on \([0,A]^T\) to compute division directly.

## Fixed reversible schedule

[KB-HAN-01](../nodes/normalized-kaliski-round.md) orients four binary-EEA cases into one shared round body using swaps. [KB-HAN-02](../nodes/fixed-rounds-and-pseudoinverse-correction.md) pads execution to \(2n\) rounds and merges the variable power-of-two correction with inverse cleanup.

## Transfer hypothesis

Combining “implicit executable history” with a fixed-round integer EEA is a research direction, not a result established by either paper. A valid prime-field design must rebuild:

- the transition alphabet for carry-based integer operations;
- the fixed-round proof;
- the history encoding;
- cleanup and scaling semantics;
- primitive Toffoli and workspace costs.

Do not transfer the \(\mathrm{GF}(2^b)\) totals from [KB-KHA-03](../nodes/dialog-and-prime-field-transfer-limit.md).
