---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 27
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 27

The text below is a page-delimited extraction of the unchanged source PDF.

27
• Better Shor circuits: Assuming the speedup for OPI stands, we wonder if further ideas along the line of
thinking of [5, 49] could culminate in an asymptotically-optimal speedup based on Shor’s algorithm.
• Peeling off log factors:Although we omit the polylogarithmic factors here, there is room to optimize them
and we wonder whether such effort would reveal a more practically-usable speedup or merely complicate matters
without much gain at useful problem scales.
V. RESOURCE ESTIMATES
A. Logical Costs
To provide a concrete assessment of the resources required to solve an instance of OPI using DQI, we performed a de-
tailed logical cost analysis of the complete, end-to-end algorithm. We implemented the key subroutines—including the
RS Decoders using the Synchronized and Dialog based EEA methods (as detailed in Section IIB2 and Section IIB3),
and the Sparse Dicke State Preparation from Appendix B; as a Bloq in the Qualtran quantum compilation framework
[19] and used it to analyze the precise qubit and gate costs.
The results of this analysis are summarized in Table VI for several representative instances of the Optimal Polyno-
mial Intersection (OPI) problem. The table presents the total Toffoli and Clifford gate counts, the number of logical
qubits required for the reversible decoder, and the estimated classical intractability of each instance. ForGF(2b), since
multiplication by a constant field element requires only Clifford gates, for smalln/m it turns out to be better to spend
a higher gate cost to run Zalka’s EEA and have explicit access to the Bézout coefficients such that the Chien search
subroutine that evaluates the Bézout coefficient polynomialσ(x) at m different constants, uses only Clifford gates.
Using Dialogs, the EEA part is significantly cheaper than Zalka’s EEA, but because we only have implicit access to
the polynomialσ(x), each evaluation ofσ(x) and σ′(x) now requires applying the Dialog and uses quantum-quantum
multiplication [8] of field elements instead of quantum-classical multiplication. For both the approaches, the qubit
counts scale as2nb + O(log2(n))
These resource estimates become particularly noteworthy when contextualized against other well-studied, classically
intractable and verifiable optimization problems. Integer factorization using Shor’s algorithm serves as the canonical
benchmark for large-scale quantum computation. As shown in the state-of-the-art estimates in [20], factoring a 2048-
bit RSA integer is estimated to require approximately6.5 × 109 Toffoli gates and1399 logical qubits, while factoring
a 1024-bit RSA integer requiers1.1 × 109 Toffoli gates and742 logical qubits. In comparison, several of our OPI
instances that are well into the classically intractable regime (requiring> 1023 trials) and exhibit Toffoli counts that
are about two to three orders of magnitude smaller, with logical qubit counts that are about two to three times higher.
(m, n, b, r) Toffoli Clifford Qubits # Prange Trials# XP Trials
(1023, 60, 10, 496) 2.76 × 106 3.89 × 107 1364 5.49 × 1019 1.92 × 1015
(1023, 70, 10, 496) 3.59 × 106 4.91 × 107 1569 1.26 × 1022 4.64 × 1016
(1023, 80, 10, 496) 4.52 × 106 6.04 × 107 1769 4.30 × 1024 1.22 × 1018
(1023, 90, 10, 496) 5.56 × 106 7.30 × 107 1970 1.07 × 1027 2.08 × 1019
(1023, 100, 10, 496) 6.71 × 106 8.68 × 107 2170 1.75 × 1029 2.56 × 1020
(4095, 60, 12, 2016) 4.64 × 106 1.27 × 108 1640 2.02 × 1023 4.02 × 1020
(4095, 70, 12, 2016) 5.72 × 106 1.52 × 108 1885 4.75 × 1026 1.97 × 1023
(4095, 80, 12, 2016) 6.92 × 106 1.79 × 108 2125 9.48 × 1029 7.99 × 1025
(4095, 90, 12, 2016) 8.27 × 106 2.08 × 108 2366 1.41 × 1033 2.27 × 1028
(4095, 100, 12, 2016) 9.75 × 106 2.41 × 108 2606 2.10 × 1036 5.91 × 1030
TABLE VI: Resource estimates for solving the Optimal Polynomial Intersection (OPI) problem using Decoded
Quantum Interferometry (DQI).m is the number of constraints,n is the number of variables, the problem is defined
over binary extension fieldFq where q = 2b, r is the size of the target setFy, ∀y ∈ F∗
q. We also report the expected
number of classical trials needed to sample a DQI grade solution using Extended Prange’s algorithm [11]. We
believe problem instances requiring more than1023 trials can be classically intractable. Here, we use the quadric set
in eq (23) throughout. We have observed that some increase in the# XP trials is possible by optimizing the choice
of set. Therefore we expect the classical hardness can be increased, though we likely cannot match# Prange Trials
even with an optimal choice of set. We do not know the ultimate limits nor do we understand how to choose the set
in a principled way.
