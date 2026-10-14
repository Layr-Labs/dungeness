---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 33
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 33

The text below is a page-delimited extraction of the unchanged source PDF.

The above construction works for any modular adder construction that performs the operation
|x⟩n |y⟩n
QMODADDp
7− − − − − − → |x⟩n |y + x⟩n. However, if we look at the VBE architecture specifically, we can
modify some of the subroutines to provide a different method for performing a controlled constant
modular addition.
Proposition 3.18 (Controlled modular adder by a constant - in VBE architecture [VBE96]) . Let
• C-QADD(a) be a quantum circuit that performs a controlled constant addition using sC-ADD
ancillas, and rC-ADD Tof gates;
• QCOMP(p) be a quantum comparator using sCOMP ancillas, rCOMP Tof gates;
• C-QSUB(p) be a quantum circuit that performs a (controlled) subtraction by a constant p using
sC-SUB ancillas, and rC-SUB Tof gates;
• C-Q′
COMP(a): be a controlled constant quantum comparator using ( s′
C-COMP ancillas, r′
C-COMP
Tof gates).
There is a circuit C-QMODADDp (a) implementing an n-bit controlled quantum modular addition by
a constant as per definition 3.16 using r = (rC-ADD + rCOMP + rC-SUB + r′
C-COMP) Tof gates and
s = 2 + max(sC-ADD, sCOMP, sC-SUB, s′
C-COMP) ancillas.
Proof. The proof is very similar to the proof of the VBE modular adder architecture (proposition 3.2).
We start with a controlled addition by a constant a into our target
|0⟩s |c⟩1 |x⟩n
C-QADD(a)
7− − − − − − → |0⟩s−1 |x + c · a⟩n+1 .
Using our comparator QCOMP(p), we can perform a comparison of the previous sum with our
modulus p
|0⟩s−1 |c⟩1 |x + c · a⟩n+1
QCOMP(p)
7− − − − − − → |0⟩s−2 |c⟩1 |x + c · a⟩n+1 |1[x + c · a < p]⟩1 .
When the comparator’s output is 0, i.e. when x + c · a ≥ p, we need to subtract the modulus p to
compute the correct sum x + c · a mod p. Therefore, we perform a controlled subtraction of p in
the register currently storing x + c · a (Note: We need to flip, using an X gate, the value of the
comparison qubit before performing our controlled subtraction )
|0⟩s−2 |c⟩1 |x + c · a⟩n+1 |1[x + c · a ≥ p]⟩1
C-QSUB(p)
7− − − − − − → |0⟩s−1 |c⟩1 |x⟩n |x + c · a mod p⟩n |1[x + c · a ≥ p]⟩1
We finally need to uncompute our previously computed output of the comparator. We notice that
x · 1[x + c · a ≥ p] ≡ ·1[x + c · a mod p < c· a] (similar to the proof of proposition 3.9), therefore,
we can use Q′
C-COMP(a) on inputs a and (x + c · a mod p) to perform the final step
|0⟩s−1 |c⟩1 |x⟩n |x + c · a mod p⟩n |1[x + c · a ≥ p]⟩1
Q′
C-COMP(a)
7− − − − − − − → |0⟩s−1 |c⟩1 |x + c · a mod p⟩n |1[x + c · a ≥ p] ⊕ c · 1[x + c · a mod p < c· a]⟩1
= |0⟩s |c⟩1 |x + c · a mod p⟩n .
A QFT-based controlled constant modular adder was proposed by Beauregard [Bea02], and
works by combining the VBE architecture with Draper’s QFT adder [Dra00] (proposition 2.5). We
propose a slightly modified proof below.
33
