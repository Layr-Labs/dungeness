---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 37
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 37

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. For the Gidney+CDKPM modular adder described in theorem 4.5, the following subroutines
are used:
• QADD: Gidney plain adder proposition 2.4;
• QCOMP(p): CDKPM half subtractor based constant comparator proposition 2.27;
• C-QSUB(p): CDKPM plain adder, more concretely, we use Q†
ADD in proposition 2.19.
• Q′
COMP: Gidney half subtractor based comparator proposition 2.28.
Now, applying theorem 4.2, we find that our expected Tof gate cost is
r =

rADD + rCOMP + rC-SUB +

r′
COMP/2

= (n + 2n + 2n + (n/2)) = 5.5n
and the ancilla count is s = n + 3 .
Theorem 4.6 (MBU modular adder - Draper/Beauregard) . Let x ∈ {0, 1}n, y∈ {0, 1}n be two
bit strings, and p ∈ {0, 1}n classically known with 0 ≤ x, y < p. There is a circuit, QMODADDp ,
performing the modular addition operation as per definition 3.1 with an expected gate count of 2.5
QFT’s, 2.5 IQFT’s, 1.5 CNOT’s, 1.5 ΦADD’s, 0.5 ΦSUB’s, 1 C-ΦSUB(p), 1 ΦADD(p), 1 ΦSUB(p) and
2 ancillas.
Proof. We leverage proposition 3.2, with the following subroutines:
• QADD: Draper plain adder corollary 2.7;
• QCOMP(p): Draper’s comparator by a classical constant proposition 2.36;
• C-QSUB(p): Draper adder, more concretely, we use Q†
ADD in proposition 2.20 and 2.13 for
controlled constant addition/subtraction;
• Q′
COMP: Draper/Beauregard comparator proposition 2.26.
The IQFT of QADD cancels with the QFT of QCOMP(p). We also find similar reductions for pairs
the IQFT’s/QFT’s of QCOMP(p)/C-QSUB(p) and C-QSUB(p)/Q′
COMP. The expected gate count is
therefore, 2.5 QFT’s, 2.5 IQFT’s, 1.5 CNOT’s, 1.5 ΦADD’s, 0.5 ΦSUB’s, 1 C-ΦSUB(p), 1 ΦADD(p) and
1 ΦSUB(p). The number of ancillas required is s = 2.
4.2 Controlled modular addition
Theorem 4.7 (MBU controlled modular adder - VBE architecture) . Let
• C-QADD be a quantum circuit that performs a quantum (controlled) addition using sC-ADD
ancillas, and rC-ADD Tof gates;
• QCOMP(p) be a quantum comparator by a constant p, using sCOMP ancillas, rCOMP Tof gates;
• C-QSUB(p) be a quantum circuit that performs a quantum subtraction by a constant p, using
sC-SUB ancillas, and rC-SUB Tof gates;
• C-Q′
COMP: be a controlled quantum comparator using ( s′
C-COMP ancillas and r′
C-COMP Tof
gates).
There is a circuit C-QMODADDp implementing an n-bit controlled quantum modular addition as per
definition 3.8 using r = (rC-ADD + rCOMP + rC-SUB + (r′
C-COMP/ 2)) Tof gates in expectation and
s = 2 + max(sC-ADD, sCOMP, sC-SUB, s′
C-COMP) ancillas.
37
