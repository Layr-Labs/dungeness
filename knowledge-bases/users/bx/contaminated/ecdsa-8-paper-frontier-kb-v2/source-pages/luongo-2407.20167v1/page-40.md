---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 40
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 40

The text below is a page-delimited extraction of the unchanged source PDF.

Then, there is a circuit QMODADDp (a) implementing quantum modular addition by a constant
as per definition 3.12 using r = (rSUB + rC-ADD + (rCOMP/2)) Tof gates in expectation and s =
1 + max(sSUB, sC-ADD, sCOMP) ancillas.
Proof. As seen in the Takashi constant modular adder (proposition 3.15), the first two subroutines
perform the following mapping
|0⟩s |x⟩n
QSUB(a),C-QADD(p)
7− − − − − − − − − − − − →|0⟩s−1 |x⟩n |x + a mod p⟩n |1[x + a < p]⟩1 .
The comparator qubit storing |1[x + a < p]⟩1 is finally supposed to be uncomputed using QCOMP(a)
and a NOT gate. We can apply the MBU lemma here on the comparator qubit and the uncomputation
subroutine QCOMP(a), thus halving the cost of QCOMP(a) in expectation. Therefore, we finally get a
cost of r = (rSUB + rC-ADD + (rCOMP/2)) Tof gates in expectation, and the same ancilla count at
proposition 3.15.
4.4 Controlled modular addition by a constant
Theorem 4.12 (MBU controlled modular adder by a constant - VBE architecture) . Let
• C-QADD(a) be a quantum circuit that performs a controlled addition by a constant using sC-ADD
ancillas, and rC-ADD Tof gates;
• QCOMP(p) be a quantum comparator using sCOMP ancillas, rCOMP Tof gates;
• C-QSUB(p) be a quantum circuit that performs a (controlled) subtraction by a constant p using
sC-SUB ancillas, and rC-SUB Tof gates;
• C-Q′
COMP(a): be a controlled constant quantum comparator using ( s′
C-COMP ancillas, r′
C-COMP
Tof gates).
There is a circuit C-QMODADDp (a) implementing an n-bit controlled quantum modular addition by a
constant as per definition 3.16 using r = (rC-ADD + rCOMP + rC-SUB + (r′
C-COMP/2)) Tof gates and
s = 2 + max(sC-ADD, sCOMP, n+ sC-SUB, s′
C-COMP) ancillas.
Proof. As seen in the controlled modular adder by a constant in VBE architecture (proposition 3.18),
the first three subroutines perform the following mapping
|0⟩s |c⟩1 |x⟩n
C-QADD(a),QCOMP(p),C-QSUB(p)
7− − − − − − − − − − − − − − − − − − − → |0⟩s−1 |c⟩1 |x⟩n |x + c · a mod p⟩n |1[x + c · a ≥ p]⟩1 .
The comparator qubit storing |1[x + c · a ≥ p]⟩1 is finally supposed to be uncomputed using
C-Q′
COMP(a). We can apply the MBU lemma here on the comparator qubit and the uncom-
putation subroutine C-Q′
COMP(a), thus halving the cost of C-Q′
COMP(a) in expectation. Therefore,
we finally get a cost of r = (rC-ADD + rCOMP + rC-SUB + (r′
C-COMP/2)) Tof gates in expectation, and
the same ancilla count at proposition 3.18.
4.5 Two-sided comparison
The following result (stating directly the complexity with and without using MBU) checks if a
register |x⟩ has a value in the range specified by two other quantum registers |y⟩ and |z⟩. Compared
to a non-MBU implementation, we save 25% for the Tof gate cost.
Theorem 4.13 (Two-sided comparator). Let x, y, z∈ {0, 1}n, and t ∈ {0, 1} Let us assume we
have access to QCOMP, with
|x⟩n |y⟩n |t⟩1
QCOMP
7− − − − → |x⟩n |y⟩n |t ⊕ 1[x < y]⟩1
40
