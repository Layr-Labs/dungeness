---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 27
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 27

The text below is a page-delimited extraction of the unchanged source PDF.

From proposition 3.2, we know that the total Tof cost of performing modular addition using
the above selection of subroutines is r = ( rADD + rCOMP + rC-SUB + r′
COMP) = 4 n Tof gates.
Similarly, the number of ancillas required is s = 2 + max(sADD, n+ sCOMP, n+ sC-SUB, s′
COMP) =
2 + max(n + 1, 2n + 1, 2n + 1, n+ 1) = 2n + 3.
The above modular adder can be further modified to reduce the number of ancillas. We propose
to use the Gidney adder only for the first addition and final comparison, and use the CDKPM adder
for the constant subtraction and constant comparison, thus giving us the following result.
Theorem 3.6 (Modular adder - Gidney + CDKPM) . There is a circuit, QMODADDp , performing
the n-bit modular addition operation as per definition 3.1 using n + 3 ancillas and 6n Tof gates.
Proof. The proof follows the same steps as the proof of proposition 3.4. In particular:
• QADD: Gidney plain adder (proposition 2.4);
• QCOMP(p): CDKPM half subtractor based constant comparator proposition 2.27;
• C-QSUB(p): CDKPM plain adder, more concretely, we use Q†
ADD in proposition 2.19 for
controlled constant addition/subtraction (proposition 2.27);
• Q′
COMP: Gidney half subtractor based comparator (proposition 2.28).
From proposition 3.2, we know that the total Tof cost of performing modular addition using the
above selection of subroutines is r = (rADD + rCOMP + rC-SUB + r′
COMP) = (n + 2n + 2n + n) = 6n Tof
gates. Similarly, the number of ancillas required is s = 2+max(sADD, n+sCOMP, n+sC-SUB, s′
COMP) =
2 + max(n + 1, n+ 1, n+ 1, n+ 1) = n + 3 ancillas.
Proposition 3.7 (Modular adder - Draper/Beauregard [Bea02]) . There is a circuit, QMODADDp ,
performing the n-bit modular addition operation as per definition 3.1 with a gate count of 3 QFT’s,
3 IQFT’s, 2 CNOT’s, 2 ΦADD’s, 1 ΦSUB, 1 C-ΦSUB(p), 1 ΦADD(p), 1 ΦSUB(p) and 2 ancillas.
Proof. We leverage proposition 3.2, with the following subroutines:
• QADD: Draper plain adder corollary 2.7;
• QCOMP(p): Draper’s comparator by a classical constant proposition 2.36;
• C-QSUB(p): Draper adder, more concretely, we use Q†
ADD in proposition 2.20 and 2.13 for
controlled constant addition/subtraction;
• Q′
COMP: Draper/Beauregard comparator proposition 2.26.
The IQFT of QADD cancels with the QFT of QCOMP(p). We also find similar reductions for pairs the
IQFT’s/QFT’s of QCOMP(p)/C-QSUB(p) and C-QSUB(p)/Q′
COMP. The total gate count is therefore, 3
QFT’s, 3 IQFT’s, 2 CNOT’s, 2 ΦADD’s, 1 ΦSUB, 1 C-ΦSUB(p), 1 ΦADD(p) and 1 ΦSUB(p). The number
of ancillas required is s = 2
3.1 Controlled modular addition
Definition 3.8 (Controlled modular addition). We will denote controlled modular addition (with
modulus p) as the following circuit
|c⟩1 |c⟩1
|x⟩n
MODADDp
|x⟩n
|y⟩n |y + c ·x mod p⟩n
27
