---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 37
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 37

The text below is a page-delimited extraction of the unchanged source PDF.

37
Appendix B: Sparse Dicke State Preparation
The Dicke state|Dm
k ⟩ is an equal weight superposition of allm-qubit states with Hamming weightk (i.e. all strings
of lengthm with exactlyk ones over a binary alphabet). As shown in Section IIA, to prepare the syndrome register
for DQI, we need to prepare the state
lX
k=0
wk |Dm
k ⟩
where w0, w1, . . . , wl−1 where l = n/2, are classically known coefficients and|Dm
k ⟩ is the Dicke state
|Dm
k ⟩ = 1qm
k

X
|y|=k
|y⟩
In the context of DQI, the Dicke state encodes a superposition over all possible
m
k

error locations for0 ≤ k ≤ l
errors in a codeword of lengthm. This encoding usesm qubits. However, whenm ≫ l = n/2, we can define a sparse
encoding that captures the same information usingl × log2 m qubits, and thus be more space efficient.
A Sparse Dicke state |SDm
k ⟩ can be defined as a uniform superposition over all k − combinations of indices
[1, 2, . . . , m], stored usingk registers each of sizeb = ⌈log2 (m + 1)⌉, using a total ofk · b qubits.
|SDm
k ⟩ = 1qm
k

X
1≤c1<c2<···<ck≤n
|c1⟩b |c2⟩b ···| ck⟩b
First, we describe a way to prepare the Sparse Dicke states|SDm
k ⟩ using the Combinatorial Number System [57].
Then, we give two different constructions for quantum circuits to unrank combinations, one that minimizes the
asymptotic complexity and other that minimizes the constant factors.
1. The unranking strategy
The Combinatorial Number System [57] defines an ordering over all
m
k

k−combinations such that a combination
[ck, ck−1, . . . , c1] where n − 1 ≥ ck > ck−1 > ··· > c1 ≥ 0 corresponds to a unique rank0 ≤ r <
m
k

given by the
bijection
r =
kX
j=1
cj
j

Using this bijection, the state preparation strategy involves two steps:
1. Prepare a uniform superposition of all ranksr ∈ {0, . . . ,
m
k

− 1} using O(k · b) gates [30]. Here we use the fact
that
m
k

≤ mk, solog2
m
k

≤ k log2 m = k · b. The state of the system is given as follows.
1qm
k

(
m
k )−1X
r=0
|r⟩k·b
2. Apply a unitary transformationUUnrank that maps the rankr to its corresponding combinationC(r):
1qm
k

X
r
|r⟩k·b
UUnrank
− − − − − →1qm
k

X
r
|C(r)⟩k·b = |SDm
k ⟩
The efficiency of the state preparation is determined by the complexity ofUUnrank.
