---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 25
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 25

The text below is a page-delimited extraction of the unchanged source PDF.

There is a circuit, QMODADDp , performing the n-bit modular addition operation as per definition 3.1
using r = (rADD + rCOMP + rC-SUB + r′
COMP) Tof gates and s = 2 +max(sADD, sCOMP, sC-SUB, s′
COMP)
ancillas.
Proof. We start with a plain addition into our target
|0⟩s+1 |x⟩n |y⟩n
QADD
7− − − → |0⟩s |x⟩n |x + y⟩n+1 .
Using our comparator QCOMP(p), we can perform a comparison of the previous sum with the given
modulus p
|0⟩s−1 |x⟩n |x + y⟩n+1
QCOMP(p)
7− − − − − − → |0⟩s−1 |x⟩n |x + y⟩n+1 |1[x + y < p]⟩ .
When the comparator’s output is 0, i.e. when x + y ≥ p, we need to subtract the modulus p to
compute the correct sum x + y mod p. Therefore, we perform a controlled subtraction of p in the
register currently storing x + y (Note: We need to flip, using an X gate, the value of the comparison
qubit before performing our controlled subtraction as pointed out in remark 2.39 )
|0⟩s−1 |x⟩n |x + y⟩n+1 |1 ⊕ 1[x + y < p]⟩1 = |0⟩s−1 |x⟩n |x + y⟩n+1 |1[x + y ≥ p]⟩1
C-QSUB(p)
7− − − − − − → |0⟩s−1 |x⟩n |x + y mod p⟩n+1 |1[x + y ≥ p]⟩1 .
Finally, we need to uncompute our previously computed output of the comparator. We notice that
1[x + y ≥ p] ≡ 1[x + y mod p < x] whenever y < pstrictly. Namely, call d = 1[x + y ≥ p] then
x + y mod p ≡ x + y − d · p hence
1[x > x+ y mod p] = 1[d · p > y] = d .
Therefore, we can use Q′
COMP on inputs x and (x + y mod p) to perform the final step
|0⟩s−1 |x⟩n |x + y mod p⟩n+1 |1[x + y ≥ p]⟩1
Q′
COMP
7− − − − →|0⟩s−1 |x⟩n |x + y mod p⟩n+1 |1[x + y > p] ⊕ 1[x + y mod p < x]⟩1
= |0⟩s |x⟩n |x + y mod p⟩n+1 .
|x⟩n
ADD ·> ·
|x⟩n
|0⟩1 |y⟩n ·< p SUB(p) |y + x mod p⟩n |0⟩1
|0⟩1 |0⟩1
Figure 22: Implementation of a modular adder using previous quantum adder circuits.
Remark 3.3. In principle, one can implement a subroutine computing x mod p for any given
number 0 ≤ x <2p as follows
|x⟩n
MOD(p)
|x⟩n
|0⟩n+1 |0⟩1 |x mod p⟩n =
·> ·
·< p SUB(p)
25
