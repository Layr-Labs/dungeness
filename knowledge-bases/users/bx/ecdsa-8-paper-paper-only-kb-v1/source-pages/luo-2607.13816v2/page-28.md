---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 28
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 28

The text below is a page-delimited extraction of the unchanged source PDF.

|ℓt⟩
|Ctrl⟩
|ℓr′⟩
|u7⟩
|u6⟩
|u5⟩
|04⟩
|g7⟩
|g6⟩
|g5⟩
⊕7 ⊕(7⊕6) ⊕(6⊕5) ⊕5
gj ⊕zj
⊕(7⊕6) ⊕(6⊕5) ⊕5
gj ⊕zj
|ℓt ⊕Lnew⟩
|Ctrl⟩
|ℓr′⟩
|u7⟩
|u6⟩
|u5⟩
|04⟩
|g7⟩
|g6⟩
|g5⟩
Figure 12: WritingL new using borrowed qubits fork= 5 andK= 7. The boxes labeledg j ⊕z j denote
the transformationg j ←g j ⊕z j for alljin the window.
We now explain how to implement the transformationg j ←g j ⊕z j for allj. The recurrence is
zK =¬a K, z j =¬a j zj+1 (j < K).
To implement this transformation, first apply, forj=k, k+ 1, . . . , K−1, the Toffoli gatesg j ←g j ⊕
(¬aj)gj+1. Then apply the base CNOT gateg K ←g K ⊕ ¬aK. Finally apply the same Toffoli gates in
reverse order, forj=K−1, K−2, . . . , k. For a fixedj < K, the two Toffoli gates acting ong j are
separated by the transformationg j+1 ←g j+1 ⊕z j+1. Therefore their combined action ong j is
gj ←g j ⊕(¬a j)gj+1 ⊕(¬a j)(gj+1 ⊕z j+1)
=g j ⊕(¬a j)zj+1 =g j ⊕z j.
The bita j is produced only locally when the corresponding gate is applied. During a scan of the window,
unary iteration on the boundary register supplies the temporary range control
bj =Ctrl∧[j≤J].
The circuit then computesa j =b j ∧u j into one clean temporary qubit, uses it as the negative control
in the corresponding Toffoli or CNOT, and immediately uncomputes it. The required range controls are
supplied by one scan in the orderk, k+ 1, . . . , Kand one scan in the reverse orderK, K−1, . . . , k.
Figure 13 shows this transformation for the examplek= 5 andK= 7. The boundary value is
computed in place on theℓ r′ register, and the temporary bitais created only when the corresponding
update gate is applied.
To updateℓ t, we invoke this subroutine twice. First we use the analogous construction withv j in
place ofu j and borrow the qubitsu j as the dirty registerg j, which XORsL old intoℓ t. Then we use the
construction described above and borrow the qubitsv j as the dirty registerg j, which XORsL new intoℓ t.
The two calls are serial, and the borrowed dirty qubits are restored after each call.
We now give the explicit resource count. First consider one application ofgj ←g j ⊕zj for allj∈[k, K].
Its gate count has three contributions:
•The forward and reverse unary iterations use 2(K−k) +O(1) Toffoli gates and 4(K−k) +O(1)
CNOT gates.
28
