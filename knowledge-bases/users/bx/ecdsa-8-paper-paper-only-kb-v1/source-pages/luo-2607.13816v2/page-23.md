---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 23
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 23

The text below is a page-delimited extraction of the unchanged source PDF.

choose the most significant bit positionbthat is not constant on its labels, thereby separating them into
two nonempty subsets according to the value ofA b. For an increasing-order traversal, we first compute
h=g(1−A b) with one reversible AND, usehas the control for theA b = 0 child, then switch the same
temporary bit by a CNOT,h←h⊕g, so thath=gA b controls theA b = 1 child. After the second child
is processed,his uncomputed. At a leafj, the current control bit is exactly
ej =c[a=j],
and the circuit appliesU j controlled one j. For a decreasing-order traversal, the two children are visited
in the opposite order. Figure 8 illustrates this construction for the interval{5,6,7,8}.
|c⟩
|L3⟩
|L2⟩
|L1⟩
|L0⟩
|W⟩ U5 U6 U7 U8
Figure 8: Pruned unary iteration on the promised intervalA∈ {5,6,7,8}. The labels are split by the
bits ofAonly when the split separates the remaining candidates. The temporary control is reused to
visit the two children of each split, and the leaves applyU 5, U6, U7, U8 in increasing order.
IfM=K−k+1, the tree hasMleaves andM−1 internal nodes. Thus the selection logic contributes
M−1 =K−kToffoli gates, while the leaf operations contribute the cost of the controlledU j gates
themselves. ForM≥2, the recursion depth, and hence the number of temporary control qubits, is at
most⌈log 2(M−1)⌉+ 1. For the trivial caseM= 1, no temporary control qubit is needed. This replaces
independent equality tests for allj, which would costO(Mlog 2 n) Toffoli gates for anO(log 2 n)-bit index
register, by a linear-size selection circuit using onlyO(log 2 M) temporary control qubits.
4.4 Location-controlled operations
In this subsection, the twoWorkregisters are indexed, from left to right, byu1, u2, . . . , un+3 andv 1, v2, . . . , vn+3,
respectively.
Location-controlledSwapcircuit.We first consider the location-controlled swap operation appearing
in Figure 5. The goal is to swap theSignqubit with the (ℓ t +ℓ q + 1)-th qubit ofWork1, while the whole
operation is controlled by an external qubitCtrl. LetJ=ℓ t +ℓq +1, wherekandKare known constants
such thatk≤J≤K. After temporarily storingJin theℓ q register, the location-controlled swap can be
written as
Swap[k,K] =|0⟩⟨0|Ctrl ⊗I+|1⟩⟨1| Ctrl ⊗
KX
j=k
|j⟩⟨j|ℓq ⊗SWAP(Sign, uj),
23
