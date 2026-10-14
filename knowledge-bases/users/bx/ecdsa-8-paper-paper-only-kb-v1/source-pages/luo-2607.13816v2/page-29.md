---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 29
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 29

The text below is a page-delimited extraction of the unchanged source PDF.

|Ctrl⟩
|ℓr′,>1⟩
|ℓr′,1⟩
|ℓr′,0⟩
|b= 0⟩
|u7⟩
|u6⟩
|u5⟩
|g7⟩
|g6⟩
|g5⟩
n+ 3−ℓr′ n+ 3−ℓr′
|Ctrl⟩
|ℓr′,>1⟩
|ℓr′,1⟩
|ℓr′,0⟩
|0⟩
|u7⟩
|u6⟩
|u5⟩
|g7 ⊕z7⟩
|g6 ⊕z6⟩
|g5 ⊕z5⟩
Figure 13: Computingg j ←g j ⊕z j fork= 5 andK= 7.
•The forward and reverse applications ofg j ←g j ⊕(¬a j)gj+1 contribute 2(K−k) Toffoli gates in
total, while the update atj=Kcontributes one CNOT gate.
•The temporary bita j =b j ∧u j is computed once in each direction and uncomputed immediately
after use. Over both directions, this uses 2(K−k) +O(1) Toffoli gates and 2(K−k) +O(1) CNOT
gates.
Thus one application ofg j ←g j ⊕z j uses 6(K−k) +O(log 2 n) Toffoli gates and 6(K−k) +O(log 2 n)
CNOT gates.
To XOR eitherL old orL new intoℓ t, the transformationg j ←g j ⊕z j is first applied between the
two sets of controlled constant XORs and is then applied again to restore the qubitsg j. These two
applications use 12(K−k) +O(log 2 n) Toffoli gates and 12(K−k) +O(log 2 n) CNOT gates. Each set
of controlled constant XORs uses 2(K−k) +O(log 2 n) CNOT gates and no Toffoli gates. Therefore,
XORing one of the two lengths intoℓ t uses 12(K−k) +O(log 2 n) Toffoli gates and 16(K−k) +O(log 2 n)
CNOT gates.
The complete length update performs this procedure once forL old and once forL new. Its total cost
is 24(K−k) +O(log 2 n) Toffoli gates and 32(K−k) +O(log 2 n) CNOT gates.
The construction uses exactlyK−k+1 dirty auxiliary qubits, all of which are restored to their initial
states. The same clean auxiliary qubits can be reused throughout the circuit: one storesa j, one stores
bj, and unary iteration requires at most⌈log 2(K−k)⌉+ 1 additional clean qubits forK−k≥1. Thus
the construction uses at most⌈log 2(K−k)⌉+ 3 clean auxiliary qubits.
5 Affine Point Addition with Mid-Circuit Measurement
In the previous sections, we constructed a space-efficient modular inversion circuit based on the extended
Euclidean algorithm. The inversion circuit uses twon-qubit field registers together withO(log 2 n) auxil-
iary qubits. In this section, we explain how to incorporate this component into an affine point-addition
circuit. By allowing mid-circuit measurements and classical feed-forward operations, the affine point-
addition block can be implemented using only threen-qubit field registers, plus theO(log 2 n) auxiliary
29
