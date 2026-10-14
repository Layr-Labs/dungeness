---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 26
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 26

The text below is a page-delimited extraction of the unchanged source PDF.

Therefore, a circuit computing x + y mod p can be alternatively given by
|x⟩n
ADD SUB
|x⟩n
|0⟩1 |y⟩n
MOD(p)
|0⟩1 |y⟩n
|0⟩n+2 |0⟩2 |x + y mod p⟩n
Proposition 3.2 gives an overview for constructing modular adders using any available combination
of adders, (controlled) subtractor (by a constant), and comparators (by a constant). In the theorems
below, we delve into specific adder circuits used for modular addition and calculate concrete costs
more thoroughly.
Proposition 3.4 (Modular adder - CDKPM [Cuc+04]) . There is a circuit, QMODADDp , performing
the n-bit modular addition operation as per definition 3.1 using n + 3 ancillas and 8n Tof gates.
Proof. We employ proposition 3.2 with the following subroutines:
• QADD: CDKPM plain adder (proposition 2.3);
• QCOMP(p): CDKPM half subtractor based constant comparator proposition 2.27;
• C-QSUB(p): CDKPM plain adder, more concretely, we use Q†
ADD in theorem 2.19 for controlled
constant addition/subtraction (proposition 2.27);
• Q′
COMP: CDKPM half subtractor based comparator proposition 2.27.
From proposition 3.2, we know that the totalTof cost of performing modular addition using the above
selection of subroutines is r = (rADD+rCOMP+rC-SUB+r′
COMP) = 8n Tof gates. Similarly, the number
of ancillas required is s = 2 +max(sADD, sCOMP, sC-SUB, s′
COMP) = 2 +max(1, n+ 1, n+ 1, 1) = n + 3.
The version presented above has essentially the same structure of [VBE96] but enjoys some
improvements. Namely, we use CDKPM’s adder (in proposition 2.3 instead of proposition 2.2), and
we substitute the use of two adder circuits for the comparator Q′
COMP (proposition 2.25) with a single
comparator circuit. These changes are already known in the literature (e.g. [Lit23]), but it is not
often mentioned the use of n ancilla qubits for internal operations. If one has access to 2 n ancillas,
one can use Gidney’s adder (proposition 2.4 instead of the CDKPM adder (i.e. proposition 2.3).
This allows for a decrease in the number of Tof gates and also the Tof depth.
Proposition 3.5 (Modular adder - Gidney [Gid18]) . There is a circuit, QMODADDp , performing the
n-bit modular addition operation as per definition 3.1 using 2n + 3 ancillas and 4n Tof gates.
Proof. The proof follows the same steps as proposition 3.4. We leverage proposition 3.2, with the
following subroutines:
• QADD: Gidney plain adder (proposition 2.4);
• QCOMP(p): Gidney half subtractor based constant comparator proposition 2.28;
• C-QSUB(p): Gidney plain adder, more concretely, we use Q†
ADD in proposition 2.19 for controlled
constant addition/subtraction (proposition 2.27);
• Q′
COMP: Gidney half subtractor based comparator proposition 2.28.
26
