---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 18
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 18

The text below is a page-delimited extraction of the unchanged source PDF.

2.3 Controlled addition by a constant
Definition 2.18 (Controlled addition by a constant). We define a controlled quantum adder as
any unitary gate implementing the n strings addition, by a classically known constant a ∈ {0, 1}n
and controlled on a qubit |c⟩, according to the following circuit
|c⟩1 |c⟩1
|0⟩1 |x⟩n ADD(a) |x + c ·a⟩n+1
Procedure Tof Count Ancillas CNOT Ref.
CDKPM 2 n n + 1 4 n + 1 + 2|a| prop. 2.19
Gidney n 2n 6n − 1 + 2|a| prop. 2.19
QFTn+1 Ancillas C-ΦADD(a) Ref.
Draper 2 0 1 prop. 2.20
Table 5: Controlled addition by a constant ’ a’
We now present a known construction that works with any adder to perform a controlled addition
by a constant as per definition 2.18
Proposition 2.19 (Controlled adder by a constant [VBE96]) . Let QADD be a quantum circuit that
performs an n-bit quantum addition as per definition 2.1 using s ancillas, and r Tof gates. There is
a circuit performing an n-bit controlled addition by a constant as per definition 2.18, using n + s
ancillas, r Tof gates and an additional 2|a| CNOTs.
Proof. This circuit can be obtained first by performing the mapping
|c⟩1 |0⟩n+s+1 |x⟩n
Load7− − − → |c⟩1 |ca⟩n |0⟩s+1 |x⟩n ,
using |a| CNOT gates. Then, we use the adder circuit, leaving the registers in the state
|c⟩1 |ca⟩n |0⟩s+1 |x⟩n
QADD
7− − − → |c⟩1 |ca⟩n |0⟩s |x + ca⟩n+1 .
Finally, one has to uncompute the register storing a, applying the previous sequence of CNOT gates
again. The corresponding circuit is depicted in figure 20 keeping implied the s ancillary qubits
required by QADD.
|c⟩1 |c⟩1
|0⟩n LOAD(a)
ADD
LOAD(a) |0⟩n
|x⟩n |x + c ·a⟩n+1
C-ADD(a)
Figure 20: Controlled addition by a constant value a. The controlled unitary gate Load(a) is a self-adjoint implemen-
tation of the mapping which loads and unloads the value c · a.
Similarly to the previous section, one can adapt Draper’s implementation to suitably implement
the gate of definition 2.18.
Proposition 2.20 (Controlled adder by a constant - Draper [Bea02]) . There is a circuit performing
an n-bit controlled addition by a constant as per definition 2.18 with zero ancilla qubits.
18
