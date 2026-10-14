---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 32
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 32

The text below is a page-delimited extraction of the unchanged source PDF.

32
VI. CONCLUSION
This work establishes Decoded Quantum Interferometry (DQI) applied to the Optimal Polynomial Intersection
(OPI) problem as a landmark candidate for practical quantum advantage. From a complexity-theoretic perspective,
we have shown that DQI+OPI is the first known proposal for verifiable superpolynomial speedup that achieves
optimal asymptotic efficiency, requiring onlyeO(N) quantum gates to solve instances with classical hardnessO(2N ).
This matches the theoretical lower bound and significantly outperforms the asymptotic scaling of Shor’s algorithm
for cryptography.
The realization of this speedup relies on the concrete efficiency of the underlying reversible Reed-Solomon (RS)
decoder. We introduced a suite of novel algorithmic and compilation techniques targeting the Extended Euclidean
Algorithm (EEA), the critical bottleneck in RS decoding. Our innovations, including theDialog representation for
implicit Bézout coefficient access and optimizedin-place register sharingarchitectures, rigorously reduce the space
complexity to the theoretical minimum of2nb qubits while substantially lowering gate counts. These techniques
are broadly applicable and promise significant improvements for other quantum algorithms reliant on the EEA,
particularly those for Elliptic Curve Cryptography.
We provided a comprehensive end-to-end compilation and resource analysis for DQI, focusing on OPI over binary
extension fields GF(2b). We analyzed the classical hardness against tailored attacks, such as the Extended Prange
algorithm, and identified resilient instances based on bent functions. Our concrete resource estimates demonstrate
that DQI can solve instances requiring> 1023 classical trials using approximately 5.72 million Toffoli gates and 1885
logical qubits. This represents a reduction of three orders of magnitude in the gate count compared to breaking
RSA-2048. Furthermore, our physical resource analysis, supported by hand-optimized lattice surgery layouts for key
primitives, estimates that such instances could be solved on a fault-tolerant architecture with800, 000 physical qubits
in ≈ 1 hour of runtime.
While our results position DQI as a compelling pathway for demonstrating quantum advantage in optimization,
several avenues for future research remain.
Continued refinement of the classical hardness analysis is crucial. While we have demonstrated resilience against
the best known classical attacks in the low-rate approximation regime, further investigation into the impact of so-
phisticated algebraic attacks ([40]) and establishing formal average-case hardness guarantees remain important open
problems.
On the quantum side, there are a few routes to improved performance as well. In [54], a few interesting ideas
were proposed. Among these was the idea to use Guruswami-Sudan and Koetter-Vardy list decoding algorithms for
RS codes [55, 56]. This would allow us to find solutions that would take exponential time even with DQI and the
Berlekamp-Massey decoder, with the cost of a higher (still polynomial) quantum circuit complexity. In a concurrent
work, [15] considers applying DQI to algebraic geometry codes. These codes have some potentially favorable properties
for verifiable quantum advantage demonstrations. Notably, they can maintain a constant rate and relative distance
with considerably smaller (and in some cases constant) alphabet sizes than Reed-Solomon codes, which could improve
the space footprint of the syndrome registers.
The Dialog representation introduced here opens new theoretical and practical questions regarding linear represen-
tations of numbers and polynomials. Key open questions include:
1. Can the size of the Dialog be reduced from≈ 2n field elements to≈ n when one of the inputs to the GCD is
known classically?
2. Is there an efficient, in-place algorithm for transforming the Dialog forx into the Dialog forx−1, or for computing
the Dialog ofx+y from the Dialogs ofx and y, without passing through the standard polynomial representation?
3. Are there more efficient linear representations beyond those based on the GCD algorithm, potentially enabling
parallelization?
By bridging complexity theory with concrete algorithmic engineering, this work identifies and enables an asymp-
totically optimal and practically efficient route toward verifiable quantum advantage.
Acknowledgments: We thank Mary Wootters for helpful conversations about decoding algorithms. We thank
Alexandru Gheorghiu for teaching us about bent functions such as in eq (23) at a Simons workshop organized by
Umesh Vazirani.
