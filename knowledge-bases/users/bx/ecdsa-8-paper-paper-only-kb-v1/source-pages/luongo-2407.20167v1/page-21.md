---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 21
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 21

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. We can directly apply proposition 2.25 giving a comparator using an adder and a subtractor.
Start preparing the register in the Fourier space.
|x⟩n |y⟩n+1 |t⟩
QFTn+1
7− − − − − → |x⟩n |ϕ(y)⟩n+1 |t⟩ .
Then, perform a ΦSUB on the Y register (subtracting by x), as the significant bit of this subtraction
is 1 only when x > y.
|x⟩n |ϕ(y)⟩n+1 |t⟩
ΦSUB
7− − − → |x⟩n |ϕ(y − x)⟩n+1 |t⟩ .
We now return back to the computational basis using a IQFTn+1
|x⟩n |ϕ(y − x)⟩n+1 |t⟩
IQFTn+1
7− − − − − → |x⟩n |y − x⟩n+1 |t⟩ .
Controlling on and copying the most significant qubit of the difference i.e. ( y − x)n, we compute
the required comparison
|x⟩n |y − x⟩n+1 |t⟩ CNOT7− − − − → |x⟩n |y − x⟩n+1 |t ⊕ 1[x > y]⟩1 .
The final set of operations described below, now return the value y − x to its original state y
|x⟩n |y − x⟩n+1 |t ⊕ 1[x > y]⟩1
QFT7− − − → |x⟩n |ϕ(y − x)⟩n+1 |t ⊕ 1[x > y]⟩1 7− →
ΦADD
7− − − → |x⟩n |ϕ(y)⟩n+1 |t ⊕ 1[x > y]⟩1 7− →
IQFT7− − − → |0⟩1 |x⟩n |y⟩n |t ⊕ 1[x > y]⟩1 .
Although the comparator described in proposition 2.25 works for any adder and subtractor,
based on the type of adder used, there are more specific constructions requiring fewer gates.
Proposition 2.27 (Comparator - CDKPM - using half a subtractor [Cuc+04]) . There is a circuit
implementing an n-bit quantum comparator as per definition 2.24 using 1 ancilla qubit and 2n Tof
gates.
Proof. The sought circuit is given by figure 21. Recall that the adjoint of a unitary quantum
adder performs a subtraction. Notice that the first part of the circuit is one-half the adjoint of the
CDKPM implementation of the adder. Comparing the definition of the UMA gate, see figure 7,
with the definition of the borrowing bk, given by equation (6) of definition 1.5, one can see that
the first sequence of UMA† accumulate in the register X the value of the borrow, in particular
Xn ← (y − x)n. By construction, see also proposition A.5, ( y − x)n computes the overflow of y − x
i.e. is 1 whenever x > y. The subsequent CNOT copies the latter value in the extra register T, and
the following sequence of UMA gate uncomputes the previous operation.
The above comparator can also be executed using the temporary logical- AND gate of Gidney,
which consumes n more ancillas (to store the temporary logical and) in comparison to proposition 2.27
Proposition 2.28 (Comparator - Gidney - using half a subtractor). There is a circuit implementing
an n-bit quantum comparator as per definition 2.24 using n ancilla qubits and n Tof gates.
One can also easily realise a controlled implementation of the comparator employing the previous
addition circuits.
21
