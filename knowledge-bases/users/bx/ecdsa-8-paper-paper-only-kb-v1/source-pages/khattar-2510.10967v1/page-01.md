---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 1
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

Verifiable Quantum Advantage via Optimized DQI Circuits
Tanuj Khattar,1, ∗ Noah Shutty,1, † Craig Gidney,1 Adam Zalcman,1
Noureldin Yosri,1 Dmitri Maslov,1 Ryan Babbush,1 and Stephen P. Jordan1
1Google Quantum AI, Venice, CA 90291
(Dated: October 09, 2025)
Decoded Quantum Interferometry (DQI) provides a framework for superpolynomial quantum
speedups by reducing certain optimization problems to reversible decoding tasks. We apply DQI
to the Optimal Polynomial Intersection (OPI) problem, whose dual code is Reed-Solomon (RS).
We establish that DQI for OPI is the first known candidate for verifiable quantum advantage with
optimal asymptotic speedup: solving instances with classical hardnessO(2N ) requires only eO(N)
quantum gates, matching the theoretical lower bound. Realizing this speedup requires highly ef-
ficient reversible RS decoders. We introduce novel quantum circuits for the Extended Euclidean
Algorithm, the decoder’s bottleneck. Our techniques, including a new representation for implicit
Bézout coefficient access, and optimized in-place architectures, reduce the leading-order space com-
plexity to the theoretical minimum of2nb qubits while significantly lowering gate counts. These
improvements are broadly applicable, including to Shor’s algorithm for the discrete logarithm. We
analyze OPI over binary extension fieldsGF(2b), assess hardness against new classical attacks, and
identify resilient instances. Our resource estimates show that classically intractable OPI instances
(requiring > 1023 classical trials) can be solved with approximately 5.72 million Toffoli gates. This
is substantially less than the count required for breaking RSA-2048, positioning DQI as a compelling
candidate for practical, verifiable quantum advantage.
Data availability: Code and assets created for this paper are available on Zenodo [1].
CONTENTS
I. Introduction 2
II. Methods for Optimized Implementation 4
A. The DQI Quantum Circuit: An Improved Construction for Qubit Efficiency 5
B. Efficient Quantum Circuits for Extended Euclidean Algorithm 7
1. Explicit versus Implicit Access to Bézout Coefficients 8
2. Synchronized Reversible EEA for Explicit Bézout coefficients 10
3. Dialog Representation for Implicit Bézout coefficients 10
C. Optimal Polynomial Intersection (OPI) over binary extension fields 13
D. Decoding Reed Solomon Codes using the Extended Euclidean Algorithm 13
III. Classical Attacks on OPI 15
A. Optimizing Prange’s Algorithm 15
B. Extended Prange’s Algorithm over Extension Fields 16
1. Expectation-Optimal XP Allocation Strategies via Linear Programming 16
2. Probability-Optimal XP Allocation Strategies via a Knapsack Solver 17
3. Search for good target sets for OPI over binary extension fields 17
4. Upper bounds on affine intersections of Maiorana-McFarland target sets 18
C. Asymptotic Classical Hardness of Twisted Bent Target OPI 24
IV. Asymptotically Optimal Quantum Speedup 25
A. Asymptotically Optimal Implementation 25
B. Asymptotic Optimality 26
V. Resource Estimates 27
A. Logical Costs 27
∗ Corresponding author: tanujkhattar4@gmail.com
† Corresponding author: shutty@google.com
arXiv:2510.10967v1  [quant-ph]  13 Oct 2025
