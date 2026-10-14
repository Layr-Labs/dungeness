---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 4
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

Logical Qubits Toffoli CNOT,CZ X
w/o MBUwith MBU w/o MBU with MBU w/o MBUwith MBU
(5 adder) VBE [VBE96]4n+ 2 20n+ 10 16n+ 8 20n+ 2|p|+ 22 16n+ 2|p|+ 18 |p|+ 2 |p|+ 2.5
(4 adder) VBE 4n+ 2 16n+ 4 14n+ 4 20n+ 2|p|+ 18 17n+ 2|p|+ 15.5 2|p|+ 1 2|p|+ 1.5
CDKPM [Cuc+04] 3n+ 2 8n 7n 16n+ 2|p|+ 4 14n+ 2|p|+ 3.5 2|p|+ 1 2|p|+ 1.5
Gidney [Gid18] 4n+ 2 4n 3.5n 26n+ 2|p|+ 4 22.75n+ 2|p|+ 3.5 2|p|+ 1 2|p|+ 1.5
CDKPM+Gidney 3n+ 2 6n 5.5n 21n+ 2|p|+ 4 17.75n+ 2|p|+ 3.5 2|p|+ 1 2|p|+ 1.5
Logical Qubits QFTn+1 PCQFTn+1 -
w/o MBUwith MBU w/o MBU with MBU - -
Draper [Dra00] 2n+ 2 10 8 1 1
Draper (Expect) 2n+ 2 8 6 1 1
Table 1: Cost of modular addition using different plain adder circuits in the VBE architecture of modular addition.
We denote by |p| the Hamming weight of the bit string of the number p expressed in binary expansion. PCQFT
stands for “partially-classical” quantum Fourier transform, where each controlled rotation in the QFT is replaced by a
classically controlled rotation. Every row in this table corresponds to a theorem in our manuscript. Results with
MBU are considered “in expectation.”. Here, Draper (Expec) represents the repeated use of the Draper addition
circuit. In expectation, the cost of the first QFT and last IQFT become negligible compared to the rest of the circuit.
Our work has the potential to improve quantum circuits for modular multiplication, modular
exponentiation, and quantum circuits for cryptographic attacks [Wan+24a; VBE96; Wan+24b].
We leave this research for future work. The interested reader can access 1 the code for symbolic
computation of some of the statements presented in this work.
1.2 Related works
This section reviews recent progress in quantum circuits for modular arithmetic, with a focus on
optimizing size and depth. Then, we turn our attention to previous applications of measurement-
based uncomputation. Early proposals for quantum addition [Cuc+04; VBE96; Dra+04], some of
which are employed in fault-tolerant algorithms with state-of-the-art resource estimates [GE21; Lit23;
Gou+23], were inspired by classical circuits for addition, with an emphasis on minimizing the T
count and/or the Tof (Toffoli) count, and the number of ancilla qubits. Subsequent approaches have
explored more quantum-specific methods of performing arithmetic [Zal06; Dra00; Bea02; Yua+23].
A nice quantum-specific way to perform a modular addition into a quantum register |x⟩n was
developed by Zalka [Zal06]. It involves only a single non-modular addition (with modulus p) as long
as |x⟩n is prepared in a coset state: P2k−1
c=0 |x + c · p⟩n+k. The overhead here is that the size of the
padding (i.e. the value of k of extra qubits required) for the coset state grows logarithmically in the
number of additions that are to be performed (See [Gid19a] for more details). All these arithmetic
circuits listed previously (and many others) serve as building blocks for more complex operations
such as modular addition, multiplication, and exponentiation, to name a few. Another survey on
quantum adders can be found in [Tak09]. The interested reader is encouraged to read [Wan+24b]
for a comprehensive literature review.
Measurement-Based Uncomputation (MBU). Measurement-based uncomputation (MBU)
was developed to efficiently address the challenge of uncomputing boolean functions. MBU is a
technique used to perform uncomputation in a probabilistic manner [Gid18]. This technique involves
measuring the qubits to be uncomputed on the X basis. Depending on the outcome of the measure-
ment, either the uncomputation circuit is executed, or it is determined that the uncomputation has
already been completed, thereby reducing the overall quantum resource requirements.
MBU has been employed in several cases [Gid18; KSS21; Gid19a; Gid19c] to improve the resource
counts of uncomputation. In particular, Gidney applied this strategy to addition circuits in [Gid18].
Starting from a Ripple Carry Addition (RCA) algorithm (see section 2 for details), they manage to
reduce the T/Tof gate cost by replacing everyTof gate with a temporary logical-AND gate (equivalent
1https://github.com/AdithyaSireesh/mbu-arithmetic
4
