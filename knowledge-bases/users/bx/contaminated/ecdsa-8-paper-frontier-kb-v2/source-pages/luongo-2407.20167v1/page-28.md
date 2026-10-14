---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 28
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 28

The text below is a page-delimited extraction of the unchanged source PDF.

A naive approach to creating a controlled modular adder is to add an extra control to each gate
of the four subroutines composing the modular adder described in proposition 3.2. However, there
is a more efficient approach where only the first adder and final comparator need to be controlled.
Such a trick has been mentioned in [Lit23] without providing a proof.
Proposition 3.9 (Controlled modular adder). Let
• C-QADD be a quantum circuit that performs a quantum (controlled) addition using sC-ADD
ancillas, and rC-ADD Tof gates;
• QCOMP(p) be a quantum comparator by a constant p, using sCOMP ancillas, rCOMP Tof gates;
• C-QSUB(p) be a quantum circuit that performs a quantum subtraction by a constant p, using
sC-SUB ancillas, and rC-SUB Tof gates;
• C-Q′
COMP: be a controlled quantum comparator using ( s′
C-COMP ancillas, r′
C-COMP Tof gates).
There is a circuit C-QMODADDp , performing the n-bit controlled modular addition operation as per
definition 3.8, using r = (rC-ADD +rCOMP +rC-SUB +r′
C-COMP) Tof gates and s = 2+ max(sC-ADD, n+
sCOMP, n+ sC-SUB, s′
C-COMP) ancillas.
Proof. In order to perform a controlled modular adder, start by first performing out controlled
addition of the addend x into the target register
|0⟩s |c⟩1 |x⟩n |y⟩n
C-QADD
7− − − − →|0⟩s−1 |c⟩1 |x⟩n |c · x + y⟩n+1
We can now follow the step similar to the modular addition protocol, where we perform a constant
comparison
|0⟩s−1 |c⟩1 |x⟩n |c · x + y⟩n+1
QCOMP(p)
7− − − − − − →|0⟩s−2 |c⟩1 |x⟩n |c · x + y⟩n+1 |1[c · x + y < p]⟩1
Once again, similar to the modular addition protocol, we perform a controlled subtraction of the
modulus p, controlled on our comparator’s output because if ( c · x + y) ≥ p, then the modulus p
needs to be subtract to reduce the sum mod p. Note: We need to first flip the comparison qubit,
and then perform the controlled subtraction (see remark 2.39)
|0⟩s−2 |c⟩1 |x⟩n |c · x + y⟩n+1 |1[c · x + y ≥ p]⟩1
C-QSUB(p)
7− − − − − − →|0⟩s−1 |c⟩1 |x⟩n |c · x + y mod p⟩n |1[c · x + y ≥ p]⟩1
We need to now uncompute the value initally computed by QCOMP. As in the modular addition
case, we need to find a comparison operation that is equivalent to d = 1[c · x + y ≥ p] (the qubit
we wish to uncompute/reset). Since ( c · x + y mod p) = ( c · x − c · d · p), one finds out that
c ·1[c ·x + y ≥ p] ≡ 1[(c ·x + y) mod p < c·x] and in particular d = c ·d since (c ·x + y ≥ p) is false
whenever c = 0 from the condition y < p. The only difference here compared to proposition 3.2
is that the comparator bit is only set for states with c · x + y ≥ p, AND with the control bit
set. The required operation is nothing but a controlled comparison, with control c, inputs x and
(c · x + y) mod p
|0⟩s−1 |c⟩1 |x⟩n |c · x + y mod p⟩n |1[c · x + y ≥ p]⟩1
C-Q′
COMP
7− − − − − →|0⟩s |c⟩1 |x⟩n |c · x + y mod p⟩n .
28
