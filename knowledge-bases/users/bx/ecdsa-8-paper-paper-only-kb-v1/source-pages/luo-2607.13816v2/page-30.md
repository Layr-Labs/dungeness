---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 30
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 30

The text below is a page-delimited extraction of the unchanged source PDF.

qubits required by the EEA inversion subroutine.
The overall circuit is shown in Figure 14. The three main quantum registers are denoted byX,Y, and
A, each storing an element ofF p. The remainingO(log 2 n) EEA ancilla qubits are not shown explicitly
in the figure.
|ctrl⟩
|x1⟩
|y1⟩
|anc= 0⟩
n
n
n
−x2
−y2 inplace
div squ
−
− squ†
+3x2
inplace
mul
neg +x2
−y2
|ctrl⟩
|x3⟩
|y3⟩
|0⟩
Figure 14: Affine point-addition circuit with mid-circuit measurements using threen-qubit field registers.
The constant additions, subtractions, negations, and squarings in Figure 14 are standard in-place
modular operations. The only non-standard components are the in-place division and multiplication
subroutines. They have the following abstract interfaces:
IDiv :|x⟩ X|y⟩Y |0⟩A 7−→ |x⟩X|y/x⟩Y |0⟩A, x̸= 0,(4)
IMul :|x⟩ X|y⟩Y |0⟩A 7−→ |x⟩X|xy⟩Y |0⟩A, x̸= 0.(5)
It remains to explain how the in-place maps in Equations (4) and (5) can be implemented with only
three field registers. The constructions are similar, so we describe the in-place division subroutine in
detail. LetSdenote theO(log 2 n) auxiliary register used by the EEA inversion circuit. The goal is to
implement
|x⟩X|y⟩Y |0⟩A|0⟩S 7−→ |x⟩X|y/x⟩Y |0⟩A|0⟩S, x̸= 0.
First, run the forward EEA inversion circuit onX, usingAas the large clean workspace andSas the
small auxiliary register:
|x⟩X|y⟩Y |0⟩A|0⟩S 7−→ |x−1⟩X|y⟩Y |0⟩A|Γ(x)⟩S.
Here|Γ(x)⟩ S denotes the intermediate EEA state that is kept until the inverse EEA circuit is applied.
Next, use a standard modular multiplication to write the quotient intoA:
|x−1⟩X|y⟩Y |0⟩A 7−→ |x−1⟩X|y⟩Y |y/x⟩A.
At this pointAis no longer clean, and therefore cannot be used as the large workspace for the inverse
EEA circuit. Instead, we recycle the registerYby measurement. ApplyH ⊗n toYand measure it in the
computational basis. If the classical outcome isb∈ {0,1} n, the remaining quantum state acquires the
phase (−1)b·y, where the dot product is overF 2. The measured registerYis then reset to|0⟩.
NowYis a cleann-qubit register, so it can be used as the large workspace for the inverse EEA circuit.
Applying the inverse EEA circuit gives
(−1)b·y|x−1⟩X|0⟩Y |y/x⟩A|Γ(x)⟩S 7−→(−1)b·y|x⟩X|0⟩Y |y/x⟩A|0⟩S.(6)
30
