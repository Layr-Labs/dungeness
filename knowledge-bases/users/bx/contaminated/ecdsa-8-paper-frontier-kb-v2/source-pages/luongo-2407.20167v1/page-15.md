---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 15
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 15

The text below is a page-delimited extraction of the unchanged source PDF.

control control
ci
M
A
J
ci ⊕ xi c
U
M
A
ci
yi yi ⊕ xi yi ⊕ control · (xi ⊕ ci)
xi ci+1 xi
Figure 17: The combination of MAJ (majority) and c − UMA (controlled unmajority) gates.
The symmetries in the circuit can be exploited to avoid controls on every gate in the controlled
Draper. Only the central ΦADD gate would need to be controlled, while the the quantum Fourier
transforms at the beginning and the end of the circuit remain uncontrolled.
Theorem 2.13 (Controlled adder - Draper) . Let x ∈ {0, 1}n, y∈ {0, 1}n be two bit strings, and
c ∈ {0, 1} be a control. Also, let QQFT-ADD be the Draper adder circuit described in corollary 2.7,
performing the operation
|x⟩n |y⟩n
QQFT-ADD
7− − − − − − → |x⟩n |x + y⟩n+1 .
We can perform a controlled Draper adder C-QFTADD using a QFTn+1, a single controlled ΦADD
(performing |c⟩1 |x⟩n |ϕ(y)⟩n+1
C-ΦADD
7− − − − → |c⟩1 |x⟩n |ϕ(y + c · x)⟩n+1), and an IQFTn+1
Proof. Start with a quantum Fourier transform
|0⟩s+1 |c⟩1 |x⟩n |y⟩n
QFTn+1
7− − − − − → |0⟩s |c⟩1 |x⟩n |ϕ(y)⟩n+1 .
Then, one performs a C-ΦADD
|0⟩s |c⟩1 |x⟩n |ϕ(y)⟩n+1
C-ΦADD
7− − − − → |0⟩s |c⟩1 |x⟩n |ϕ(c · x + y)⟩n+1 ,
followed by a IQFTn+1 gate to return the required state back to the computation basis
|0⟩s |c⟩1 |x⟩n |ϕ(c · x + y)⟩n+1
IQFTn+1
7− − − − − → |0⟩s |c⟩1 |x⟩n |c · x + y⟩n+1 .
Below, we show a way to execute the C-ΦADD (as introduced in theorem 2.13) using a single
ancilla and n extra Tof gates.
Theorem 2.14 (Controlled adder - Draper - with 1 ancilla) . Let x ∈ {0, 1}n, y∈ {0, 1}n be two bit
strings, and c ∈ {0, 1} be a control. Also, let
QQFT-ADD = (In ⊗ IQFTn+1)ΦADD(In ⊗ QFTn+1)
be the circuit described in corollary 2.7 (Draper’s adder), performing a quantum addition as per
definition 2.1. We can perform a controlled Draper adder C-QQFT-ADD using a circuit of cost bounded
by 2QFTn+1, and a C-ΦADD gate. The circuit requires only a single ancilla.
Proof. Following up from the above theorem 2.13, we find a construction for C-ΦADD, requiring
only a single ancilla. We first notice that all gates in ΦADD commute. Therefore, the order in which
they are performed is irrelevant. Secondly, the main difference between ΦADD and C-ΦADD is that
15
