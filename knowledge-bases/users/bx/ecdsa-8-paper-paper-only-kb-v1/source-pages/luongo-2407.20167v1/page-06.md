---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 6
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 6

The text below is a page-delimited extraction of the unchanged source PDF.

rotation between the j-th qubit in the register X and targets the i-th qubits in the register Y . We
define the function 1[condition] to be 1 if condition is true, otherwise is 0. In the case of a QFT
based adder by a constant, we use PCQFTa,n to denote a classically controlled set of rotation gates
that need to be applied in order to perform the required addition in the phase.
k
=
k
= C i-Rj (2π/2k) =


1 0 0 0
0 1 0 0
0 0 1 0
0 0 0 e
2πi
2k


Figure 3: Quantum Controlled Rotation Gate. We show both the circuit representation and the corresponding unitary
matrix of the controlled rotation. The i and j correspond to the two qubits involved in the controlled rotation.
Let y ∈ {0, 1}n. The state obtained after applying the quantum Fourier transform (see e.g. [NC11])
QFT to the state |y⟩ is given by
|ϕ(y)⟩n := QFTn |y⟩n = 1
2n/2
X
x
e2πixy/2n
|x⟩n .
We denote by QFTn the quantum Fourier transform acting on a n qubits register and by IQFTn its
inverse.
Let Q be a quantum circuit composed of m gates Qj from a gateset G = {G1, G2, . . . ,GK}. Define
the gate count ci := |{j ∈ [m] | Qj = Gi}| for i ∈ [K]. We represent the gate counts of Q as
count(Q) = {(Gi, ci) | i ∈ [K]}.
Remark 1.1 (Circuit size of QFT [NC11]) . A QFTm has a circuit size of
count(QFTm) = {(H, m)} ∪ {(C-R(θi), m+ 1 − i) | i ∈ [1, m+ 1]}.
Boolean arithmetic. In this paragraph, we will review some basic definitions of bit string
arithmetic. Denote by x = xn−1 . . . x0 ∈ {0, 1}n a n-bit string i.e. a string of n binary numbers.
Further facts about the bit string representation of integers are reported in appendix A. We consider
the following four operations on the set of n-bits string.
Definition 1.2 (Bit string addition). We call bit string addition the binary operator
+ : {0, 1}n × {0, 1}n → {0, 1}n+1 , (x, y) 7→ s
defined bit-wise by si = xi ⊕ yi ⊕ ci, where the bit ci, called i-th carry, is defined recursively by
c0 = 0
ci = maj(xi−1, yi−1, ci−1) = xi−1yi−1 ⊕ xi−1ci−1 ⊕ yi−1ci−1 . (5)
The function maj is a logic gate called majority, which gives 1 whenever at least two of the three
entries are different than 0.
Definition 1.3 (Bit string 1’s complement) . We call 1’s complement the operator defined bit-wise
by (x)i = xi ⊕ 1 as
· : {0, 1}n → {0, 1}n , x 7→ x.
Definition 1.4 (Bit string 2’s complement) . We call 2’s complement the operator defined as
x = x + 1, where 1 denotes the n bits string 0 . . .0 1 as
· : {0, 1}n → {0, 1}n , x 7→ x.
6
