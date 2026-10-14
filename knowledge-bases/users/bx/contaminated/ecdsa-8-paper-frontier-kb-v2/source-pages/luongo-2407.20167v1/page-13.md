---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 13
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 13

The text below is a page-delimited extraction of the unchanged source PDF.

Corollary 2.7 (Draper’s QFT-adder) . Let x ∈ {0, 1}n, y∈ {0, 1}n be two bit strings stored in
register X and Y of size n and n + 1 respectively (the most significant bit of register Y is set to 0).
There is a circuit implementing a quantum adder as per definition 2.1 using n ancilla qubits. The
circuit gate cost is bounded above by the cost of 3QFTn+1 circuits.
2.1 Controlled addition
Definition 2.8 (Controlled addition). We define a controlled quantum adder as any unitary gate
implementing the n strings addition controlled on a qubit |c⟩ according to the following circuit
|c⟩1 |c⟩1
|x⟩n
ADD
|x⟩n
|0⟩1 |y⟩n |c ·x + y⟩n+1
Procedure Tof Count Ancillas CNOT Ref.
CDKPM 3 n 1 4 n + 1 thm. 2.12
Gidney 2 n n + 1 7 n − 1 prop. 2.11
Tof Count Ancillas QFTn+1 Ref.
Draper n 1 3 thm. 2.14
Table 3: Controlled addition by a constant
The theorem below gives a general recipe to perform a controlled addition given any adder.
Theorem 2.9 (Controlled adder - with n extra ancillas and 2 n extra Tof gate). Let QADD be a
quantum circuit that performs an n-bit quantum addition as per definition 2.1 using s ancillas, and
r Tof gates. Then, there is a circuit implementing a controlled quantum adder as per definition 2.8
using n + s ancilla qubits and r + 2n Tof gates.
Proof. We first initialize a circuit in the state
|c⟩1 |x⟩n |y⟩n |0⟩s+n+1 .
Now, we use a sequence of n Tof gates to load a controlled version of the addend x i.e.
|c⟩1 |x⟩n |y⟩n |0⟩s+n+1
Load7− − − → |c⟩1 |x⟩n |y⟩n |c · x⟩n |0⟩s+1 .
We can now perform the required addition using c · x as our addend
|c⟩1 |x⟩n |y⟩n |c · x⟩n |s + 1⟩
QADD
7− − − → |c⟩1 |x⟩n |y + c · x⟩n+1 |c · x⟩n |0⟩s .
We finally unload c · x using n Tof gates
|c⟩1 |x⟩n |y + c · x⟩n+1 |c · x⟩n |0⟩s+1
Unload7− − − − → |c⟩1 |x⟩n |y + c · x⟩n |0⟩n+s .
The loading of c · x is performed in a register initially in the |0⟩n state. This can be executed
with just a temporary logical- AND, and therefore can be uncomputed using measurements as in the
case of the Gidney plain adder (proposition 2.4). This leads to the following corollary.
13
