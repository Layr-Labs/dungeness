---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 31
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 31

The text below is a page-delimited extraction of the unchanged source PDF.

there is a circuit QMODADDp (a) implementing an n-bit quantum modular addition by a constant
as per definition 3.12 using r = ( rADD + rCOMP + rC-SUB + r′
COMP) Tof gates and s = 2 +
max(sADD, sCOMP, sC-SUB, s′
COMP) ancillas.
Proof. The proof is very similar to the proof of the VBE modular adder architecture (proposition 3.2).
We start with an addition by a constant a into our target
|0⟩s |x⟩n
QADD(a)
7− − − − − → |0⟩s−1 |x + a⟩n+1 .
Using our comparator QCOMP(p), we can perform a comparison of the previous sum with our
modulus p
|0⟩s |x + a⟩n+1
QCOMP(p)
7− − − − − − → |0⟩s−2 |x + a⟩n+1 |1[x + a < p]⟩1 .
When the comparator’s output is 0, i.e. when x + a ≥ p, we need to subtract the modulus p to
compute the correct sum x + a mod p. Therefore, we perform a controlled subtraction of p in the
register currently storing x + a (note: we need to flip, using an X gate, the value of the comparison
qubit before performing our controlled subtraction):
|0⟩s−2 |x + a⟩n+1 |1[x + a ≥ p]⟩1
C-QSUB(p)
7− − − − − − → |0⟩s−1 |x⟩n |x + a mod p⟩n |1[x + a ≥ p]⟩1 .
We finally need to uncompute the comparator qubit. We notice that1[x+a ≥ p] ≡ 1[x+a mod p < a],
therefore, we can use Q′
COMP(a) on inputs a and (x + a mod p) to perform the final step
|0⟩s−1 |x⟩n |x + a mod p⟩n |1[x + a ≥ p]⟩1
Q′
COMP(a)
7− − − − − − →|0⟩s−1 |x + a mod p⟩n |1[x + a < p] ⊕ 1[x + a mod p ≥ a]⟩1
= |0⟩s |x + a mod p⟩n .
Given that we are adding by a constant, various ways exist to create more cost-effective
modular addition circuits by modifying the plain addition implemented in the modular adder.
Takahashi [Tak09] in 2009 was the first to observe that the initial two operations in the VBE
modular architecture could be merged into a single operation when performing a constant modular
addition.
Proposition 3.15 (Modular adder by a constant - in Takahashi architecture [TTK09]) . Let
• QSUB(a) be a quantum circuit that performs a constant quantum subtraction using sSUB ancillas,
and rSUB Tof gates;
• C-QADD(p) be a quantum circuit that performs a (controlled) addition by a constant p using
sC-ADD ancillas, and rC-ADD Tof gates;
• QCOMP(a) be a classical comparator using sCOMP ancillas, rCOMP Tof gates.
there is a circuit QMODADDp (a) implementing an n-bit quantum modular addition by a constant as per
definition 3.12 using r = (rSUB + rC-ADD + rCOMP) Tof gates and s = 1 + max(sSUB, sC-ADD, sCOMP)
ancillas.
Proof. To perform the unitary operation |0⟩s |x⟩n
QMODADDp(a)
7− − − − − − − − → |x + a (mod p)⟩n, we start subtract-
ing p − a (which is different from the first step of proposition 3.2, where we add a)
|0⟩s−1 |x⟩n
QSUB(p−a)
7− − − − − − →|0⟩s−1 |x − (p − a)⟩n+1 = |0⟩s−1 |x + a − p⟩n+1
31
