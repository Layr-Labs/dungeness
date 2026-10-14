---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 22
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 22

The text below is a page-delimited extraction of the unchanged source PDF.

•Length-update circuit for updatingℓ t.We execute the length-update circuit only at step
indicesTthat are multiples of four. This circuit acts on qubits indexed fromℓ t to (n+ 3−ℓ r′),
and the corresponding two-sided active window is defined by
ℓt ≥k 4(T) := max
T−4(n+ 1)−4δ
4c−4

,1

,
n+ 3−ℓ r′ ≤K 4(T) := min{T/4 + 3, n+ 3}.
•Length-update circuit for updatingℓ r′.Letℓ ∗
t , ℓ∗
r′ denote the updated value ofℓ t, ℓr′ after the
length update. This circuit acts on qubits indexed fromℓ ∗
t +2 to (n+4−ℓ ∗
r′), and the corresponding
two-sided active window is defined by
ℓ∗
t + 2≥k 5(T) := max
T−4δ
4c

,1

,
n+ 4−ℓ ∗
r′ ≤K 5(T) := min{T/4 + 4, n+ 3}.
4.3 Unary iteration
We will use unary iteration [BBG +18] to implement location-controlled operations on a known interval
of the twoWorkregisters. LetLbe aLengthregister promised to store a valuea∈ {k, k+ 1, . . . , K}, let
Wbe aWorkregister, and letcbe an optional external control qubit. The operation has the form
U[k,K] =|0⟩⟨0|c ⊗I+|1⟩⟨1| c ⊗
KX
j=k
|j⟩⟨j|L ⊗U j,
whereU j is a unitary operation onWselected by the valuej. Equivalently, the operation performs
|c⟩|a⟩|ψ⟩ 7→ |c⟩|a⟩Uc
a |ψ⟩for alla∈[k, K].
The main primitive used by unary iteration is a reversible AND. The compute and uncompute forms
of this gate are shown in Figure 7. In the Toffoli/CNOT counting convention used here, computing an
AND costs one Toffoli gate, while uncomputing an AND using measurement costs one CNOT gate with
no Toffoli gates.
• • •
• = • = • •
|0⟩ |T⟩ T† T T† H S†
• • •
• = • = Z
|0⟩ H •
Figure 7: Compute and uncompute forms of the reversible AND primitive, reproduced from [BBG +18].
For a general interval, unary iteration can be viewed as a binary tree whose leaves are the labels
k, k+ 1, . . . , K. Each internal node stores a subset of labels. If the current node has control bitg, we
22
