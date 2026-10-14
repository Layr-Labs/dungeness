---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 20
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 20

The text below is a page-delimited extraction of the unchanged source PDF.

Definition 2.24 (Quantum comparison). We define a quantum comparator as any unitary gate
implementing the n strings comparison according to the following circuit
|x⟩n
·> ·
|x⟩n
|y⟩n |y⟩n
|t⟩1 |t ⊕1[x > y]⟩1
where 1[x > y] coincides with the most significant bit of y − x, i.e. is 1 when x > yand 0 otherwise.
Procedure Tof Count Ancillas CNOT Ref.
CDKPM 2 n 1 4 n + 1 prop. 2.27
Gidney n n 6n + 1 prop. 2.28
QFTn+1 Ancillas − Ref.
Draper 6 1 − prop. 2.26
Table 6: Comparators
Due to the close link between the string subtraction and the string comparison algorithm, it is
possible to implement a quantum comparator by adapting the implementations of quantum adder
proposed in the previous section.
Proposition 2.25 (Comparator - using an adder and a subtractor [VBE96]) . Let QADD be a
quantum circuit that performs an n-bit quantum addition as per definition 2.1 using sADD ancillas,
and rADD Tof gates. Additionally, let QSUB be a quantum circuit that performs an n-bit quantum
subtraction as per definition 2.21 using sSUB ancillas, and rSUB Tof gates. Then, there is a circuit
implementing an n-bit quantum comparator as per definition 2.24 using s = 1 + max(sADD, sSUB)
ancilla qubits and r = rADD + rSUB Tof gates as well as an additional CNOT
Proof. This circuit can be obtained first by performing the mapping
|0⟩s |x⟩n |y⟩n |t⟩1
QSUB
7− − − → |0⟩s−1 |x⟩n |y − x⟩n+1 |t⟩1
Here, the value most significant bit of ( y − x) i.e. ( y − x)n gives us the required comparator output
(y − x)n = 1[x > y]. Therefore, applying a CNOT on the target register T with the most significant
qubit of |y − x⟩ as the control, we get
|0⟩s−1 |x⟩n |y − x⟩n+1 |t⟩1
CNOT7− − − − → |0⟩s−1 |x⟩n |y − x⟩n+1 |t ⊕ 1[x > y]⟩1 .
We can now apply QADD to return back to the required state
|0⟩s−1 |x⟩n |y − x⟩n+1 |t ⊕ 1[x > y]⟩1
QADD
7− − − → |0⟩s |x⟩n |y⟩n |t ⊕ 1[x > y]⟩1 .
The circuit described below is a component of the QFT modular addition circuit described by
Beauregard [Bea02], which is based on the Draper QFT adder circuit (proposition 2.5).
Proposition 2.26 (Comparator - Draper/Beauregard [Bea02]) . Let x ∈ {0, 1}n, y∈ {0, 1}n be
two bit strings stored in register X and Y of size n and n + 1 respectively (the most significant
bit of register Y is set to 0). There is a circuit QCOMP performing a quantum comparison as per
definition 2.24 using 1 CNOT, 2 QFTn+1, 2 IQFTn+1, 1 ΦSUB and 1 ΦADD gates, and a single ancilla
qubit.
20
