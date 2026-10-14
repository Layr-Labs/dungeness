---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 38
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 38

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. As seen in the controlled modular adder - VBE architecture (proposition 3.9), the first three
subroutines perform the following mapping
|0⟩s |c⟩1 |x⟩n |y⟩n
C-QADD,QCOMP(p),C-QSUB(p)
7− − − − − − − − − − − − − − − − − → |0⟩s−1 |c⟩1 |x⟩n |c · x + y mod p⟩n |1[c · x + y ≥ p]⟩1 .
The comparator qubit storing 1[c · x + y ≥ p] is finally supposed to be uncomputed using C-Q′
COMP.
We can apply the MBU lemma here on the comparator qubit and the uncomputation subroutine
C-Q′
COMP, thus halving the cost of C-Q′
COMP in expectation. Therefore, we finally get a cost of
r = (rC-ADD + rCOMP + rC-SUB + (r′
C-COMP/2)) Tof gates in expectation, and the same ancilla count
as proposition 3.9.
Theorem 4.8 (MBU controlled modular adder - CDKPM) . There is a circuit C-QMODADDp
implementing an n-bit controlled quantum modular addition as per definition 3.8 using n + 3 ancillas
and 8n + 0.5 Tof gates in expectation.
Proof. For the controlled CDKPM modular adder described in proposition 3.10, the following
subroutines are used:
• C-QADD be a quantum circuit that performs a quantum (controlled) using a CDKPM adder
with a single extra ancilla (theorem 2.12) requiring sC-ADD = 2 ancillas, and rC-ADD = 3n Tof
gates;
• QCOMP(p) be a quantum comparator by a constant p using Controlled comparator - using
half a CDKPM subtractor (theorem 2.38), requiring sCOMP = n + 1 ancillas, rCOMP = 2n Tof
gates;
• C-QSUB(p) be a quantum circuit that performs a quantum subtraction by a constant p using
the CDKPM adder in proposition 2.16, requiring sC-SUB = n + 1 ancillas, and rC-SUB = 2n
Tof gates;
• C-Q′
COMP be the controlled quantum comparator described in proposition 2.30: Controlled
comparator - using half a CDKPM subtractor. This subroutine requires s′
C-COMP = 1 ancilla,
r′
C-COMP = 2n + 1 Tof gates.
Now, applying theorem 4.2, we find that our expected Tof gate cost is
r =

rC-ADD + rCOMP + rC-SUB +

r′
C-COMP/2

= (3n + 2n + 2n + (2n + 1)/2) = 8n + 0.5
and the ancilla count is s = n + 3.
Theorem 4.9 (MBU controlled modular adder - Gidney) . There is a circuit C-QMODADDp imple-
menting an n-bit controlled quantum modular addition as per definition 3.8 using 2n + 3 ancillas,
4.5n + 0.5 Tof gates in expectation.
Proof. For the Gidney controlled modular adder described in proposition 3.11, the following
subroutines are used:
• C-QADD be a quantum circuit that performs a quantum (controlled) using a Gidney adder with
a single extra ancilla (proposition 2.11) requiring sC-ADD = n + 1 ancillas, and rC-ADD = 2n
Tof gates;
• QCOMP(p) be a quantum comparator by a constant p using Controlled comparator - using half
a Gidney subtractor (proposition 2.31), requiring sCOMP = 2n + 1 ancillas, rCOMP = n Tof
gates;
38
