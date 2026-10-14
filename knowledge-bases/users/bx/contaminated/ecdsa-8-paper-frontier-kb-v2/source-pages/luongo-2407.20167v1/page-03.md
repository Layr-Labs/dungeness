---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 3
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 3

The text below is a page-delimited extraction of the unchanged source PDF.

However, this process leaves carry bits in memory, which need to be uncomputed from the rest
of the registers to ensure the correctness of the computation. Efficient quantum arithmetic circuits
are pivotal for advancing quantum computing, underpinning numerous key algorithms. This also
involves finding cheaper ways of performing uncomputation on qubits storing garbage/intermediate
computations.
1.1 Main results
In this work, we improve quantum circuits for modular arithmetic using measurement-based
uncomputation, specifically focusing on quantum modular adders. In section 2, we begin by
formalizing previously known circuits for addition and defining in a theorem the resources required
for their implementation. For all the adders we consider [Cuc+04; VBE96; Dra00; Gid18], we also
cover the possible cases for (controlled) addition, subtraction and comparison (by a constant). While
these constructions can be easily derived, we could not find records of many of them in previous
literature, e.g., (controlled) comparator by a constant, controlled modular addition, etc. We offer
a modular and composable framework to construct these arithmetic circuits from other known
arithmetic primitives. We also show a construction for a controlled adder using just a single ancilla
by modifying the CDKPM adder (theorem 2.12). In section 3, we consider various tradeoffs for
combining the results presented in the previous section to form a quantum circuit that performs
a (controlled) modular addition (by a constant). In particular, we show how two different adder
architectures (the CDKPM adder [Cuc+04] and Gidney adder [Gid18]) can be combined, leading
to better space-time tradeoffs compared to using either adder individually within the modular
adder architecture (see theorem 3.6). These tradeoffs are particularly important when running
quantum algorithms in early error-corrected settings. In section 4, we discuss the proof of the
measurement-based uncomputation lemma, which we present below. This technique was already
known in the literature [Gid18; KSS21; Gid19a], but to the best of our knowledge, it has not
been formalized as a plug-and-play result. While MBU can be generalized to uncomputation of
multi-qubit registers, for modular arithmetic we can use the following lemma.
Lemma (Measurement-based uncomputation lemma). Let g : {0, 1}n → {0, 1} be a function, and
let Ug be a self-adjoint (n + 1)-qubit unitary that maps Ug |x⟩n |b⟩1 = |x⟩n |b ⊕ g(x)⟩1. There is an
algorithm performing the mapping P
x αx |x⟩n |g(x)⟩1 7→ P
x αx |x⟩n |0⟩1 using Ug, 2 H gates, and 1
NOT gate with 1/2 probability. It also involves one single-qubit computational basis measurement
and a single H gate.
Applying the MBU lemma leads to gate costs expressed “in expectation”. The expected value
is calculated based on a Bernoulli distribution with a probability p = 1
2 . This is because, for any
quantum state P
x αx |x⟩n |g(x)⟩1, if g(x) ∈ {0, 1}, when the last register is measured in the X basis,
there is an equal probability of obtaining a |0⟩ or |1⟩ state. The remainder of section 4 is dedicated to
deriving formal statements for modular addition circuits optimized by MBU. While table 1 presents
our results for modular addition (section 4.1), we also share resource counts for controlled modular
addition (section 4.2), modular addition by a constant (section 4.3), and controlled modular addition
by a constant (section 4.4). For example, for the controlled modular adder derived from [Cuc+04],
MBU can reduce the Tof (Toffoli) count by n + 1
2 gates in expectation (compare proposition 3.4
with proposition 3.10). The minimum number of Tof gates is achieved by proposition 3.11 using
2n + 2 ancilla qubits. For modular addition by a constant, MBU reduces the Tof count by n gates
in expectation (compare proposition 3.15 with theorem 4.11), leading to a 16 .7% improvement on
the original circuit. We obtain similar improvements for controlled modular addition by a constant.
We also show a way to perform a double-sided comparison (theorem 4.13), i.e. to see if a given
register’s value is contained within two other register’s values. This circuit is a prime candidate for
MBU, leading to a nearly 25% reduction in the cost of the circuit.
3
