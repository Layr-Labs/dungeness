---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 5
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

to a Tof gate). While a Tof gate performs the mapping |x⟩1 |y⟩1 |t⟩1
Tof7− − → |x⟩1 |y⟩1 |x · y ⊕ t⟩1, the
logical-AND gate uses an ancilla qubit to execute the Tof gate as follows:
|x⟩1 |y⟩1 |t⟩1 |0⟩1
Tof7− − → |x⟩1 |y⟩1 |t⟩1 |x · y⟩1
CNOT7− − − − → |x⟩1 |y⟩1 |x · y ⊕ t⟩1 |x · y⟩1 .
Since the Tof gates come in pairs (the Tof gates used in the RCA computation must also be
uncomputed), MBU is used to avoid performing a Tof gate for the uncomputation, replacing it with
an X basis measurement followed by a classically controlled C-Z gate. In [Gid19a], MBU is used to
construct the coset state more effectively. In the QROM lookup circuits introduced in [Bab+18;
Gid19c], MBU is used to construct a highly efficient unlookup (uncomputation of lookup) operation.
For an address register |a⟩n, a lookup table performs the operation
|a⟩n
Lookup
7− − − − → |a⟩n |ℓa⟩, (4)
where ℓa is the lookup value associated with address a. An address register of size n qubits
corresponds to a lookup table of L = 2n elements, making the cost of performing a lookup L = 2n
Toffolis. After ℓa has been used in the computation, it must be uncomputed. Naively performing
the uncomputation would cost the same as the lookup. However, by combining unary encoding with
MBU, it is possible to reduce the cost of the uncomputation to just
√
L [Bab+18; Gid19c] gates.
Other works study the more general problem of reversibly computing a chain of functions
x0
f1
7− →x1 = f1(x0)
f2
7− → ···xm−1 = fm−1(xm−2)
fm
7− − →xm = fm(xm−1) through the use of pebbling
games [Ben89]. Pebbling games offer a way to perform these computations reversibly and find
effective ways of studying space-time tradeoffs of various strategies to uncompute intermediate
results. In the case of chains of unitaries {Ufi }m
i=1, spooky pebble games were introduced by
Gidney [Gid19b], which allowed X basis quantum measurements as an additional operation in
pebbling games. The measurements may result in a phase applied to the states in the superposition,
which is then tracked and corrected at a later time in the computation.
1.3 Notation and convention
We assume basic knowledge of quantum computing; we refer the interested reader to [NC11]. As
in [Cuc+04], we denote the quantum registers by capital lettersA, B, C, etc. Each register is encoded
with several qubits; we denote by Ai the i-th qubit of register A. Each qubit can be understood as a
memory location; if not differently stated, we will assume that in qubit Ai is initially stored the value
ai. We represent the state of a n qubit register A as |a⟩n. In principle, applying a quantum gate
to a given register affects the values stored in its qubit; we denote by Ai ← x the storing of value
x ∈ {0, 1} in the i-th component of register A as the result of a certain quantum circuit. Where
necessary, we put the number of qubits in a register as a subscript following the ket representing the
register’s state, e.g. |x⟩n for an n-qubit register. For an n bit string x = xn−1xn−2 . . . x0 ∈ {0, 1}n
we shall often equate it with the decimal number x encoded in binary by x. We denote with a|n the
n bit string encoding the number a ∈ {−2n, . . . ,0, 1, . . . ,2n − 1} in the 2’s complement notation
(see remark A.4 in the appendix). For a number a ∈ N, |a| denotes the Hamming weight of the
binary representation of a. The interested reader is referred to [Von93] or [HH10] and appendix A
for further details on bit strings operations.
Quantum computing. We recall the definition of the following single-qubit gates.
X =
0 1
1 0

, Z =
1 0
0 −1

, S =
1 0
0 i

, T =
1 0
0 eiπ/4

.
We denote by Ci-Rj(θk) the rotation by θk = 2π/2k of qubit j controlled by qubit i (See figure 3).
We can eventually use register names indexed by its qubits: e.g. CXj -RYi (θk) performs a controlled
5
