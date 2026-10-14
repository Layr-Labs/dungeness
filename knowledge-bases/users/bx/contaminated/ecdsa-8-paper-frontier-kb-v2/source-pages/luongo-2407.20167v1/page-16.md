---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 16
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 16

The text below is a page-delimited extraction of the unchanged source PDF.

any controlled rotation C-R(θi) (for any i ∈ [n]), now becomes a double controlled rotation CC-R(θi)
gate:
|c1⟩1 |c2⟩1 |t⟩1
CC-R(θi)
7− − − − − →exp(2πi(c1 · c2 · t)/2i) |c1⟩1 |c2⟩1 |t⟩1
We can decompose any CC-R gate it into a temporary logical- AND, a single controlled rotation,
followed by an uncomputation of the logical- AND:


|c1⟩1 |c2⟩1 |0⟩1 |t⟩1
Tof7− − → |c1⟩1 |c2⟩1 |c1 · c2⟩1 |t⟩1
C-R(θi)
7− − − − →exp(2πi(c1 · c2 · t)/2i) |c1⟩1 |c2⟩1 |c1 · c2⟩1 |t⟩1
Uncompute Tof
7− − − − − − − − − →exp(2πi(c1 · c2 · t)/2i) |c1⟩1 |c2⟩1 |0⟩1 |t⟩1


Using the above decomposition, we can convert every CC-R into a temporary logical-AND + C-R
(and finally an uncomputation of the temporary logical- AND).
|0⟩1 |c⟩1 |x⟩n |ϕ(y)⟩n+1
Tof7− − → |c · xi⟩1 |c⟩1 |x⟩n |ϕ(y)⟩n+1 .
We can now perform the required rotation gates that initially had xi as the control, by using c · xi
as our control instead. Compared to ΦADD, we require an extra n(n + 3)/2 Tof for the temp logical-
AND’s, n(n + 3)/2 H gates and n(n + 3)/4 C-R(θ1) gates in expectation (cost of uncomputation of
logical ANDs) in total for C-ΦADD. We only require a single ancilla as the ancilla is reset after every
gate. The Tof cost can be made cheaper by noticing that we can rearrange the order of the controlled
rotation gates in C-ΦADD and group all gates that have a common control xi. This construction
requires only an additional n Tof gates (cost of logical ANDs), n H gates and n/2 C-R(θ1) gates in
expectation (cost of uncomputation of the logical ANDs).
2.2 Addition by a constant
Definition 2.15 (Addition by a constant). We define a quantum adder by a constant as any unitary
gate implementing the n strings addition by a classically known constant a ∈ {0, 1}n according to
the following circuit
|0⟩1 |x⟩n ADD(a) |x + a⟩n+1
Such a gate can be obtained from any given quantum adder implementation QADD in several
ways. In this section, we present a way to perform addition by a constant using any circuit as per
definition 2.1. We also dive into more specific implementations.
Procedure Tof Count Ancillas CNOT Ref.
CDKPM 2 n n + 1 4 n + 1 prop. 2.16
Gidney n 2n 6n − 1 prop. 2.16
QFTn+1 Ancillas ΦADD(a) Ref.
Draper 2 0 1 prop. 2.17
Table 4: Additon by a constant
Proposition 2.16 (Adder by a constant [Cuc+04]) . Let QADD be a quantum circuit that performs
an n-bit quantum addition as per definition 2.1 using s ancillas, and r Tof gates. Then, there is a
circuit implementing
|0⟩1 |x⟩n 7→ |x + a⟩n+1
as per definition 2.1 using n + s ancilla qubits and r Tof gates
16
