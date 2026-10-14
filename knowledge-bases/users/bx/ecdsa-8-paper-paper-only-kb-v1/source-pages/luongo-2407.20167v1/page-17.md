---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 17
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 17

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. This circuit can be obtained first by performing the mapping
|0⟩s+n+1 |x⟩n
Load7− − − → |a⟩n |0⟩s+1 |x⟩n ,
using |a| NOT gates (one on each qubits i such that ai ̸= 0) and treating the first n + 1 qubits input
as an ancillary channel. Then, we use the adder circuit QADD, to perform the required addition
|a⟩n |0⟩s+1 |x⟩n
QADD
7− − − → |a⟩n |0⟩s |x + a⟩n+1 .
Finally, we uncompute the ancilla register storing a by applying the previous sequence of not gates
again.
|a⟩n |0⟩s |x + a⟩n+1
Unload7− − − − → |0⟩s+n |x + a⟩n+1 .
The corresponding circuit is depicted in figure 18, keeping implicit the s ancillary qubits required
by QADD.
|0⟩n LOAD(a)
ADD
LOAD(a) |0⟩n
|0⟩1 |x⟩n |x + a⟩n+1
ADD(a)
Figure 18: Addition by a constant value a. The unitary gate LOAD(a) is a self-adjoint implementation of the mapping
which load and unload the value a.
While proposition 2.16 is applicable to any adder that can perform the mappingQADD |x⟩n |y⟩n 7→
|x⟩n |x + y⟩n+1, in the case of Draper’s QFT adder, there is a method to add constants without
requiring ancillas. This method was used by Beauregard [Bea02].
Proposition 2.17 (Adder by a constant - Draper [Bea02]) . There is a circuit implementing an
n-bit addition by a constant as per definition 2.15 using 0 ancillas.
|ϕ(x)⟩n+1
Ua,n
|ϕ(a+ x)⟩n+1
Ua,n-2
...
Ua,1
Ua,0
≡ |ϕ(x)⟩n+1 Φ ADD(a) |ϕ(a+ x)⟩n+1
Figure 19: QFT-based addition by a constant [Bea02]
Proof. The complete proof directly follows from corollary 2.7. figure 19 details the unitary gates
that are required to perform the QFT-based addition by a constant, where Ua,i is given by
Ua,i =
iY
k=0
R (aiθi−k+1) = R
 iX
k=0
akθi−k+1
!
= R

1
2i+1
iX
k=0
2kak
!
. (7)
We denote the n qubit gate ⊗n−1
i=0 Ua,i as ΦADD(a) (because our rotation gates are determined by the
value of the bits of a).
17
