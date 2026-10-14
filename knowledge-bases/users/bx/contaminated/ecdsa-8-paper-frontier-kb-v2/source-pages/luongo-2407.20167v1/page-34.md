---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 34
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 34

The text below is a page-delimited extraction of the unchanged source PDF.

Proposition 3.19 (Controlled modular adder by a constant - Beauregard [Bea02]) . There is a
circuit C-QMODADDp (a) implementing an n-bit controlled quantum modular addition by a constant
as per definition 3.16 with a gate count of 3 QFT’s, 3 IQFT’s, 2 CNOT’s, 1 C-ΦADD(a), 1 ΦADD(a),
1 ΦSUB(a), 1 C-ΦSUB(p), 1 ΦADD(p), 1 ΦSUB(p) and 2 ancillas.
Proof. We use the following subroutines. Let
• C-QADD(a) be Draper’s controlled adder by a constant (proposition 2.20), using 0 ancillas;
• QCOMP(p) be a quantum comparator based on proposition 2.36, using 1 ancilla;
• C-QSUB(p) be a quantum circuit that performs a controlled subtraction by a constant based
on proposition 2.20 using 0 ancillas;
• C-Q′
COMP(a): be a controlled quantum comparator by a constant as derived in theorem 2.38
using 1 ancilla.
Note that adjacent QFTs and IQFTs can cancel out. The total gate count is therefore, 3 QFT’s,
3 IQFT’s, 2 CNOT’s, 1 C-ΦADD(a), 1 ΦADD(a), 1 ΦSUB(a), 1 C-ΦSUB(p), 1 ΦADD(p) and 1 ΦSUB(p).
The number of ancillas required is s = 2
In proposition 3.19, the modular addition circuit is based on a single controlled QFT adder.
For completeness, we also share Beauregard’s [Bea02] original circuit in figure 23 which uses two
controls, and also uses a slightly different set of gates..
|c1⟩1 |c1⟩1
|c2⟩1 |c2⟩1
ϕ(x)
Φ ADD (a)
Φ ADD†(p)
Φ ADD (p)
Φ ADD†(a)
Φ ADD (a)
ϕ(x+ c1c2a mod p)
QFT-1 QFT QFT-1 QFT
|0⟩1 |0⟩1
Figure 23: Quantum Fourier Transform modular adder by a constant. Here |ϕ(x)⟩ is made of n + 1 qubits instead of
n qubits, in order to account for the initial overflow from adding a.
4 Measurement-based uncomputation speed-ups
We are now prepared to present the proof of the MBU lemma and its applications to modular
arithmetic. The MBU algorithm for uncomputing a single qubit is the circuit that can be found in
figure 24. Recall that MBU has already been introduced in [Gid18] (for the special case of Tof gates)
but here we formalize this method for the single-qubit uncomputation of any unitary. Attempts
at generalization of MBU to perform multi-qubit computation has been already treated in the
literature, see e.g. [Gid19c].
|x⟩n Ug
|x⟩n
|g(x)⟩1 H H H |0⟩1
Figure 24: A circuit for measurement-based uncomputing the unitary Ug.
34
