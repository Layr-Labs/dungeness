---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 7
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 7

The text below is a page-delimited extraction of the unchanged source PDF.

Definition 1.5 (Bit string subtraction). We call bit string subtraction the binary operator
− : {0, 1}n × {0, 1}n → {0, 1}n+1 , (x, y) 7→ (x + y) .
The string d = x − y is given bit-wise by di = xi ⊕ yi ⊕ bi, where the bit bi, called i-th borrow, is
defined recursively by
b0 = 0
bi+1 = maj(xi ⊕ 1, yi, bi) . (6)
Naming convention for theorems and propositions. As a guideline, we use “proposition”
to refer to statements already present in the literature; in cases where we are unaware of a formal
proof in the literature, we provide one. We use “theorem” to denote facts first stated and proven in
this manuscript (to the best of our knowledge). We use the convention “operation name - subroutine
variant used (if any) - additional descriptors (if any)” to name theorems and propositions. For
example, “Comparator - CDKPM - using half a subtractor” represents a quantum comparator
operation based on a subroutine variant by authors CDKPM, using a partial subtraction circuit.
2 Quantum adders
Definition 2.1 (Quantum addition). We define a quantum adder as any unitary gate implementing
the n-bit strings addition (see definition 1.2) according to the following circuit
|x⟩n
ADD
|x⟩n
|0⟩1 |y⟩n |x + y⟩n+1
The initial extra qubit, prepared in |0⟩, in the second register is needed to take into account the
possible overflow. Note that by the theory of bit string additions (see appendix A and section 1.3),
such a circuit implements both the addition of unsigned integers, interpreting the bit string x with
the corresponding decimal number, and the addition of signed integers, interpreting the two entries
in the 2’s complement convention. Several quantum implementations of bit string addition have
been discussed in the literature. Due to their significant role as the fundamental components of
quantum arithmetic, we recollect four of them for the sake of completeness.
Procedure Toff. Count Ancillas CNOT Ref.
VBE plain adder [VBE96] 4 n n 4n + 4 prop. 2.2
CDKPM plain adder [Cuc+04] 2 n 1 4 n + 1 prop. 2.3
Gidney plain adder [Gid18] n n 6n − 1 prop. 2.4
QFTn+1 Ancillas Ref.
Draper [Dra00] 3 0 − prop. 2.5
Table 2: Gate count and logical qubits count for plain adders.
VBE implementation One of the first implementations of a quantum adder had been proposed
by Vedral, Barenko and Ekert (VBE) in [VBE96]. Such a circuit is built out of the auxiliary unitary
gates CARRY and SUM (see figure 4) computing the carry and the sum on a single bit. The VBE
implementation is subsumed by the following proposition.
7
