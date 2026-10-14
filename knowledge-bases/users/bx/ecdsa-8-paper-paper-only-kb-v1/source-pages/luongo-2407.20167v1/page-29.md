---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 29
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 29

The text below is a page-delimited extraction of the unchanged source PDF.

We will now explore some costs of controlled modular adders for a few specific combinations of
subroutines.
Proposition 3.10 (Controlled modular adder - CDKPM) . There is a circuit C-QMODADDp , per-
forming the n-bit controlled modular addition operation as per definition 3.8, using n + 3 ancillas
and 9n + 1 Tof gates.
Proof. We implement a controlled modular adder by using proposition 3.9 in conjunction with the
following subroutines:
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
COMP be the quantum comparator described in proposition 2.30: Controlled comparator -
using half a CDKPM subtractor. This subroutine requires s′
C-COMP = 1 ancilla, r′
C-COMP =
2n + 1 Tof gates.
There is a circuit C-QMODADDp, performing the controlled modular addition operation as per
definition 3.8, using r = (rC-ADD + rCOMP + rC-SUB + r′
C-COMP) = (3n + 2n + 2n + (2n + 1)) = 9n + 1
Tof gates and s = 2+ max(sC-ADD, n+sCOMP, n+sC-SUB, s′
C-COMP) = 2+ max(2, n+1, n+1, 1) = n+3
ancillas.
Proposition 3.11 (Controlled modular adder - Gidney). There is a circuit C-QMODADDp , performing
the n-bit controlled modular addition operation as per definition 3.8, using 2n + 3 ancillas and 5n + 1
Tof gates.
Proof. We implement a controlled modular adder by using proposition 3.9 in conjunction with the
following subroutines:
• C-QADD be a quantum circuit that performs a quantum (controlled) using a Gidney adder with
a single extra ancilla (proposition 2.11) requiring sC-ADD = n + 1 ancillas, and rC-ADD = 2n
Tof gates;
• QCOMP(p) be a quantum comparator by a constant p using Controlled comparator - using half
a Gidney subtractor (proposition 2.31), requiring sCOMP = 2n + 1 ancillas, rCOMP = n Tof
gates;
• C-QSUB(p) be a quantum circuit that performs a controlled quantum subtraction by a constant
p using the Gidney adder in proposition 2.16, requiring sC-SUB = 2n+1 ancillas, and rC-SUB = n
Tof gates;
• C-Q′
COMP be the controlled quantum comparator described in proposition 2.31: controlled
comparator - using half a Gidney subtractor. This subroutine requires s′
C-COMP = n + 1
ancillas, r′
C-COMP = n + 1 Tof gates.
29
