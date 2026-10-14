---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 36
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 36

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. As seen in the modular adder - VBE architecture (proposition 3.2), the first three subroutines
perform the following mapping
|0⟩s |x⟩n |y⟩n
QADD,QCOMP(p),C-QSUB(p)
7− − − − − − − − − − − − − − − − → |0⟩s−1 |x⟩n |x + y mod p⟩n |1[x + y ≥ p]⟩1 .
The comparator qubit storing 1[x + y ≥ p] is finally supposed to be uncomputed using Q′
COMP.
We can apply the MBU lemma on the comparator qubit and the uncomputation subroutine
Q′
COMP, thus halving the cost of Q′
COMP in expectation. Therefore, we finally get a cost of r =
(rADD + rCOMP + rC-SUB + (r′
COMP/2)) Tof gates in expectation, and the same ancilla count at
proposition 3.2.
Theorem 4.3 (MBU modular adder - CDKPM) . There is a circuit, QMODADDp , performing the
n-bit modular addition operation as per definition 3.1 using n + 3 ancillas and 7n Tof gates in
expectation.
Proof. For the CDKPM modular adder described in proposition 3.4, the following subroutines are
used:
• QADD: CDKPM plain adder proposition 2.3;
• QCOMP(p): CDKPM half subtractor based constant comparator proposition 2.27;
• C-QSUB(p): CDKPM plain adder, more concretely, we use Q†
ADD in proposition 2.19.
• Q′
COMP: CDKPM half subtractor based comparator proposition 2.27.
Now, applying theorem 4.2, we find that our expected Tof gate cost is
r =

rADD + rCOMP + rC-SUB +

r′
COMP/2

= (2n + 2n + 2n + (2n/2)) = 7n
and the ancilla count is s = n + 3.
Theorem 4.4 (MBU modular adder - Gidney) . There is a circuit, QMODADDp , performing the n-bit
modular addition operation as per definition 3.1 using 2n + 3 ancillas, 3.5n Tof gates in expectation.
Proof. Assume to access the following subroutines are used:
• QADD: Gidney plain adder proposition 2.4;
• QCOMP(p): Gidney half subtractor based constant comparator proposition 2.28;
• C-QSUB(p): Gidney plain adder, more concretely, we use Q†
ADD in proposition 2.19.
• Q′
COMP: Gidney half subtractor based comparator proposition 2.28.
Now, applying theorem 4.2, we find that our expected Tof gate cost is
r =

rADD + rCOMP + rC-SUB +

r′
COMP/2

= (n + n + n + (n/2)) = 3.5n
and the ancilla count is s = 2n + 3 .
Theorem 4.5 (MBU modular adder - Gidney + CDKPM). There is a circuit, QMODADDp , performing
the n-bit modular addition operation as per definition 3.1 using n + 3 ancillas, 5.5n Tof gates in
expectation.
36
