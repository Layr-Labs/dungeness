---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 39
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 39

The text below is a page-delimited extraction of the unchanged source PDF.

• C-QSUB(p) be a quantum circuit that performs a controlled quantum subtraction by a constant
p using the Gidney adder in proposition 2.16, requiring sC-SUB = 2n+1 ancillas, and rC-SUB = n
Tof gates;
• C-Q′
COMP be the controlled quantum comparator described in proposition 2.31: controlled
comparator - using half a Gidney subtractor. This subroutine requires s′
C-COMP = n + 1
ancillas, r′
C-COMP = n + 1 Tof gates.
Now, applying theorem 4.2, we find that our expected Tof gate cost is
r =

rC-ADD + rCOMP + rC-SUB +

r′
C-COMP/2

= (2n + n + n + (n + 1)/2) = 4.5n + 0.5
and the ancilla count is s = 2n + 3.
4.3 Modular addition by a constant
Theorem 4.10 (MBU modular addition by a constant - VBE architecture) . Let
• QADD(a) be a quantum circuit that performs a constant quantum addition using sADD ancillas,
and rADD Tof gates;
• QCOMP(p) be a quantum comparator using sCOMP ancillas, rCOMP Tof gates;
• C-QSUB(p) be a quantum circuit that performs a (controlled) subtraction by a constant p using
sC-SUB ancillas, and rC-SUB Tof gates;
• Q′
COMP(a): be a constant quantum comparator using ( s′
COMP ancillas, r′
COMP Tof gates).
there is a circuit QMODADDp (a) implementing an n-bit quantum modular addition by a constant
as per definition 3.12 using r = (rADD + rCOMP + rC-SUB + (r′
COMP/2)) Tof gates and s = 2 +
max(sADD, sCOMP, sC-SUB, s′
COMP) ancillas.
Proof. As seen in the constant modular adder in VBE architecture (theorem 3.14), the first three
subroutines perform the following mapping
|0⟩s |x⟩n
QADD(a),QCOMP(p),C-QSUB(p)
7− − − − − − − − − − − − − − − − − − → |0⟩s−1 |x⟩n |x + a mod p⟩n |1[x + a ≥ p]⟩1 .
The comparator qubit storing |1[x + a ≥ p]⟩1 is finally supposed to be uncomputed using Q′
COMP(a).
We can apply the MBU lemma here on the comparator qubit and the uncomputation subroutine
Q′
COMP(a), thus halving the cost of Q′
COMP(a) in expectation. Therefore, we finally get a cost of
r = (rADD + rCOMP + rC-SUB + (r′
COMP/2)) Tof gates in expectation, and the same ancilla count at
theorem 3.14.
Theorem 4.11 (MBU modular adder by a constant - in Takahashi Architecture) . Let x ∈ {0, 1}n.
Assume to know classically p, a∈ {0, 1}n with 0 ≤ a, x < p. Also, assume we have access to the
following subroutines:
• QSUB(a) be a quantum circuit that performs a constant quantum subtraction using sSUB ancillas,
and rSUB Tof gates;
• C-QADD(p) be a quantum circuit that performs a (controlled) addition by a constant p using
sC-ADD ancillas, and rC-ADD Tof gates;
• QCOMP(a) be a classical comparator using sCOMP ancillas, rCOMP Tof gates.
39
