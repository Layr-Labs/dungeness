---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 19
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 19

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. We reuse the construction of proposition 2.17 and add controls to every rotation gate. The
cost of this circuit depends on the binary representation of a. We define as C-ΦADD(a) the gate
performing the operation
|c⟩1 |ϕ(x)⟩n+1
C-ΦADD(a)
7− − − − − − → |c⟩1 |ϕ(c · a + x)⟩n+1 .
2.4 Subtraction
Definition 2.21 (Quantum subtraction). We define a quantum subtractor as any unitary gate
implementing the n strings subtraction (see definition 1.5) according to the following circuit
|x⟩n
SUB
|x⟩n
|0⟩1 |y⟩n |y −x⟩n+1
Due to the unitarity of the quantum adder gate and the uniqueness of the adjoint, it follows that
(ADD)† implements a quantum subtractor. Alternatively, one can implement a quantum subtractor
directly from the definition of bit-string subtractions.
Theorem 2.22. The following two circuits implement a quantum subtractor.
|x⟩n
ADD
|x⟩n
|0⟩1 |y⟩n |y −x⟩n+1
(8)
|0⟩1 |x⟩n ADD(1)
ADD
ADD(1)† |0⟩1 |x⟩n
|0⟩1 |y⟩n |y −x⟩n+1
(9)
Proof. By definition, the gate L flips all bits of a given register |r⟩ namely producing the state |r⟩,
i.e. the 1’s complement of the string r (see definition 1.3). Therefore, the circuit 8 implements bit
string subtraction as given by definition 1.5. On the other hand, the second circuit in theorem 2.22
implements subtraction using the 2’s complement of the second addend as given by proposition A.1
in the appendix.
Interestingly, we recall that the gate performing addition by 1, i.e. the “increment by one”
operator, enjoys a more specialized implementation [Gid15].
Remark 2.23 (Adjoint of Gidney Adder) . While a subtractor can be built using an adjoint of
the adder, circuits involving a measurement (e.g. logical- AND adder) are generally not invertible.
One way to invert the logical- AND adder is to swap the roles of the computation (logical- AND) and
uncomputation (MBU uncomputation of logical- AND) of the logical- AND’s in the circuit.
2.5 Comparison
As expressed by proposition A.3 in appendix A, given a quantum subtractor, one can easily obtain
a string comparator reading the sign (i.e. the most significant bit) of the difference.
19
