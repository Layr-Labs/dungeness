---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 31
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 31

The text below is a page-delimited extraction of the unchanged source PDF.

The phase in Equation (6) is removed by recomputing the measured valueyfromxandy/x. Specifically,
apply the modular multiplication
|x⟩X|0⟩Y |y/x⟩A 7−→ |x⟩X|y⟩Y |y/x⟩A,(7)
then apply the classically controlled Pauli correction
Zb =Z b0 ⊗Z b1 ⊗ ··· ⊗Zbn−1
to the registerY. This contributes another factor (−1) b·y and therefore cancels the measurement phase.
Finally, reverse the multiplication in Equation (7), obtaining
|x⟩X|0⟩Y |y/x⟩A.
SwappingYandAcompletes the in-place division:
|x⟩X|y/x⟩Y |0⟩A.
The corresponding circuit is shown in Figure 15.
|x⟩
|y⟩
|anc0= 0⟩
|anc1= 0⟩
0
n
n
n
O(logn)
n
EEA
EEA
mul H⊗n
b
0 EEA†
EEA†
mul Zb mul†
|x⟩
|y/x⟩
|0⟩
|0⟩
b
Figure 15: In-place division with mid-circuit measurement and classical feed-forward operations.
The in-place multiplication subroutine is implemented by the same mechanism. One first computes
xyinto the clean registerA, measures and resets the oldY=yregister, uses the remaining registers to
recomputeyfor theZ b phase correction, uncomputes this recomputation, and finally swapsYwithA.
Thus both IDiv and IMul require only the three field registersX, Y, A, together with theO(log 2 n) EEA
auxiliary registerS. Therefore the affine point-addition circuit in Figure 14 uses 3n+O(log 2 n) logical
qubits.
6 Resource Estimation and the ECDLP
We adopt the resource-estimation methodology introduced by Roetteler et al. [RNSL17]. In Shor’s
algorithm for the ECDLP, the dominant quantum cost arises from the sequence of controlled elliptic-
curve point additions performed in superposition. We consider the point additions in affine coordinates
over the finite fieldF p, wherepis ann-bit prime. At this level, point addition reduces to a fixed sequence
of modular additions, subtractions, multiplications, squarings, and inversions. Among these operations,
modular inversion typically dominates both the space complexity and the Toffoli gate count.
31
