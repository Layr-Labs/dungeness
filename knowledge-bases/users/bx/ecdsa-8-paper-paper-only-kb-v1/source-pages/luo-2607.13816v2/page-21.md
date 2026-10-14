---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 21
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 21

The text below is a page-delimited extraction of the unchanged source PDF.

|Phase1⟩ /1 • • • • • •
|Phase2⟩ /1 • •
|0⟩ /1
|Sign⟩ /1 • •
Add
▶
▶
•
|Work1⟩ /n+3
SWAP Len
|Work2⟩ /n+3
Sub
▶ Shift1 Shift−2
|ℓs⟩ /ℓ+1 +1 −2
|ℓt⟩ /ℓ+1 Sub Add Len ▶
|ℓq⟩ /ℓ+1
|ℓr′ ⟩ /ℓ+1 • • • Len ▶
|Iter⟩ /1
Figure 6: Overall circuit implementation (second half) of a single iteration of our space-efficient EEA,
continued from Figure 5. The four dashed boxes, from left to right, represent: (1) location-controlled
addition ont’s; (2) post-shift operations; (3) phase update; (4) swappingWork1andWork2, together with
the corresponding length updates at the end of one EEA iteration.
operations to qubits in theWork1register with indices outside the interval [k, K] is unnecessary. We refer
to this interval as theactive window.
We next specify the step-dependent active windows for each type of location-controlled operation.
All bounds are taken over allpossible inputsx, namely, those inputsxfor which the location-controlled
circuits are activated by the outer control qubits. We defer the proofs to Appendix A.2. Here the
constants are set to be
λ:= (2 +
√
3)1/3, c:= 1/log 2 λ= 3/log 2(2 +
√
3), δ:= log λ

4
√
3−3
13 λ2
!
= 0.726208. . . .
•Location-controlled addition/subtraction onr’s.These operations act on qubits indexed
from (ℓ t +ℓ q + 2) to (n+ 3−ℓ s). The upper boundK 1 =K 1(T) =n+ 3; the lower bound
k1 =k 1(T) is defined by
ℓt +ℓ q + 2≥k 1(T) := max
T−n−1−4δ
4c−1

,1

+ 2.
•Location-controlled swap.These operations act on the (ℓ t +ℓ q + 1)-th qubit. The two-sided
bounds are defined by
ℓt +ℓ q + 1≥k 2(T) := max
T−3(n+ 1)−4δ
4c−3

,1

+ 1,
ℓt +ℓ q + 1≤K 2(T) := min{⌊T/2⌋+ 2, n+ 2}.
•Location-controlled addition/subtraction ont’s.These operations act on the first (ℓ t + 1)
qubits. This is a one-sided controlled operation, the upper boundK 3(T) is defined by
ℓt + 1≤K 3(T) := min{⌈T/4⌉+ 1, n+ 1}.
21
