---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 39
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 39

The text below is a page-delimited extraction of the unchanged source PDF.

39
3. Iterative Unranking for low constant factor Dicke State Preparation
The divide and conquer strategy described has optimal asymptotic complexity but would not be ideal for a constant
factor analysis. Here, we describe a simple greedy algorithm to find thek−combination corresponding to rankr with
small constant factors: takeck maximal with
ck
k

≤ r, then takeck−1 maximal with
ck−1
k−1

≤ r −
ck
k

, and so on. We
can translate this greedy algorithm into a reversible quantum circuit to prepare Sparse Dicke states using2 · k · b + b
qubits andO(m.k + k2b2) Toffoli gates as follows:
1. The unitaryUUnrank(n, k) can be defined as a product ofk unitaries, each of which iteratively finds thejth
coefficient cj in the sequenceC(r) as follows:
UUnrank(m, k) = Usearch(m, 1) · Usearch(m, 2) . . . Usearch(m, k− 1) · Usearch(m, k)
Here Usearch(m, j) can be defined as:
Usearch(m, j) |r⟩j log2 m |0⟩log2 m → |r −
cj
j

⟩
(j−1) log2 m
|cj⟩log2 m
2. The unitaryUsearch(m, j) can be implemented using a bitwise binary search strategy, where we determine the
largest cj such that
cj
j

≤ r, iterating overlog2 m bits of cj from most significant bit to least significant bit,
and for eachlog2 m ≥ i ≥ 0, setcj = cj + 2i if
cj+2i
j

≤ r. A reversible quantum circuit would therefore require
log2(m) calls to a sparse QROM, theith of which loads2i binomial coefficients of the form
cj+2i
j

. The total
Toffoli cost of the sparse QROMs across all iterations is thereforek.m. Once the Binomial coefficients are loaded
using the QROM, we also need ak. log2 m comparator for each of thelog2 m bits ofcj. The total Toffoli cost
of the comparators across all iterations is thereforeO((k log2 m)2).
Appendix C: Improved arithmetic circuits for binary extension fields
m Toffoli CNOT PCTOF CNOT
10 39 738 39 0
11 47 1278 46 0
12 51 1506 51 0
TABLE VII: Resource counts for GF(2m) multiplication form = 10, 11, 12, expressed as gate counts over two
libraries, {Toffoli, CNOT} and {Parity Control Toffoli, CNOT}.
1. Parity Control Toffoli PCTOF and Parity CNOTPCNOT
The parity control Toffoli PCTOF is equivalent to a multi-target Toffoli gate with controls being the parity of a
subset of qubits. The PCNOT gate is a CNOT gate that computes the XOR of its controls and is equivalent to a
series of CNOTs with the same target. The main advantages of the PCNOT gate is that in the presence of enough
ancillae, it can be performed in a single cycle using lattice surgery independent of the number of controls.
When the two control sets of a PCTOF are disjoint, as is the case of GF(2m) multiplication, the two control parities
can be computed in a single cycle. Fig. 6 shows the first PCTOF of Fig. 7 expanded in terms of PCNOT and Toffoli
and in terms of CNOT and Toffoli gates.
2. GF( 2m) arithmetic circuits
Our implementation of the DQI algorithm relies on arithmetic circuits over GF field sizes of210 through 212. The
bottleneck is GF multiplication.
To implement the respective multiplication (and division) circuits, we rely on [9]. This synthesis algorithm develops
a modification of Karatsuba multiplication over a carefully selected irreducible polynomial, along with local optimiza-
tions using templates, allowing for a reduction in both Toffoli and CNOT gate counts compared to the state-of-the-art
