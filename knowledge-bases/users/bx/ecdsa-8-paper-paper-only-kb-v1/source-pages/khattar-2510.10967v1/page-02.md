---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 2
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 2

The text below is a page-delimited extraction of the unchanged source PDF.

2
B. Physical Costs 28
VI. Conclusion 32
References 33
A. Optimizing the number of trials of Extended Prange 34
1. Upper Bound on the objective function 36
B. Sparse Dicke State Preparation 37
1. The unranking strategy 37
2. Divide and Conquer Unranking foreO(m) Dicke State Preparation 38
3. Iterative Unranking for low constant factor Dicke State Preparation 39
C. Improved arithmetic circuits for binary extension fields 39
1. Parity Control ToffoliP CT OFand Parity CNOTP CNOT 39
2. GF(2m) arithmetic circuits 39
3. Measurement-based Uncomputation for GF2 Multiplication. 40
D. Bounding the number of iterations for Synchronized Reversible Polynomial EEA 41
1. Worst-Case Analysis: Full PEEA (GCD) 42
2. Worst-Case Analysis: Half PEEA (Reed-Solomon Decoding) 43
E. Deferred proofs of upper bounds on affine intersections of Maiorana-McFarland target sets 43
F. Reference Python Implementation 48
1. Reed Solomon Decoding using Synchronized EEA for Explicit Bézout coefficients 48
2. Reed Solomon Decoding using Dialog based EEA for Implicit Bézout Coefficients 48
I. INTRODUCTION
The pursuit of verifiable quantum advantage is a central goal in quantum computing.Quantum advantage refers
to solving problems efficiently on a quantum computer where no efficient classical algorithm is known.Verifiability
implies we can efficiently check the solution on a classical computer. Verifiable quantum advantage problems are a
useful model of future applications of quantum computers to classical search and optimization problems abundant in
industry.
A fundamental question in this pursuit concerns the efficiency of the quantum speedup itself. Given a problem
instance with a target classical hardness ofO(2N ) (where N is the security parameter), what is the required quantum
runtime? The theoretical lower bound isΩ(N) quantum gates [2]. However, existing candidates for verifiable super-
polynomial advantage exceed this bound. For example, achievingO(2N ) hardness in integer factorization requires
Shor’s algorithm [3] to useeO(N6) gates (against the General Number Field Sieve), while Elliptic Curve Cryptography
(ECC) requires eO(N2) gates (against Pollard Rho).
One corollary of the resource estimation performed in this work is to demonstrate that Decoded Quantum Interfer-
ometry (DQI)[4], when applied tothe Optimal PolynomialIntersection(OPI) problem, is thefirst known candidate for
verifiable quantum advantage that achieves the optimal asymptotic speedup (up to polylogarithmic factors), requiring
only eO(N) quantum gates to solve instances withO(2N ) classical hardness:
Theorem I.1.There is an NP-search / optimization problem where the runtime of the best-known classical algorithm
for the problem is2N and which can be solved with a circuit ofeO(N) quantum gates.
We prove this theorem in Section IV. We compare this against prior speedups based on Shor’s algorithm in Table I.
To understand how DQI achieves this speedup, we must formalize the class of problems it addresses. DQI provides
a framework for approximating solutions to constraint satisfaction problems, specifically max-LINSAT, where its
efficiency is tied to the efficiency of reversibly decoding a related error-correcting code.
Definition I.2(max-LINSAT [4]). Let Fq be a finite field. Given anm × n matrix B over Fq (with m > n), and for
each constrainti = 1, 2, . . . , m, a subsetFi ⊂ Fq. The max-LINSAT problem is to find an assignmentx ∈ Fn
q that
maximizes the number of satisfied constraints, where thei-th constraint is satisfied ifPn
j=1 Bijxj ∈ Fi.
