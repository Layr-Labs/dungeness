---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 15
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 15

The text below is a page-delimited extraction of the unchanged source PDF.

15
TABLE V: Leading-order gate costs for the reversible EEA-based RS decoder, comparing the explicit
(Section IIB2) and implicit (Section IIB3) access models. Gate Costs are dominated by quantum-quantum (QQ)
and quantum-classical (QC) multiplications. GF Inverse refers to the number of field inversions. The explicit access
model also has a much higher constant factor coming from other operations like CSWAPS and CADDS, to manage
the state of the system as part of the complex synchronization scheme.
Explicit Access Model Implicit Access Model
Decoder Stage QQ MultsQC MultsGF Inverse QQ MultsQC MultsGF Inverse
Step 1: EEA (Key Equation) 3n2 — 6n n2 — n
Steps 2&3: Chien Search & Forney Algorithm — mn m 2mn mn/2 m
Total (Leading Order) 3n2 mn m + 6n 2mn + n2 mn/2 m + n
As the table shows, the choice of model creates a clear trade-off. In the typical regime for OPI wheren ≪ m, the
complexity of both models is dominated by theO(mn) terms from the Chien search and Forney’s algorithm. For the
implicit model, the dominant cost is2mn quantum-quantum multiplications needed to evaluateσ(z) and its derivative
via Dialog playback. For the explicit model, the dominant cost ismn quantum-classical multiplications to evaluate
the three required polynomials.
For circuits over binary extension fields, a quantum-classical multiplication in GF(2b) can be implemented very
efficiently using only Clifford gates (a sequence of CNOTs), whereas a quantum-quantum multiplication requires
non-Clifford resources (Toffoli gates). Therefore, for the parameter regimes we study, theexplicit access approach is
substantially cheaper, as its dominant cost has a much lower Toffoli complexity. However, this trade-off should be
carefully re-evaluated for other applications, such as those over prime fields, where quantum-classical multiplication
is also expensive.
III. CLASSICAL ATTACKS ON OPI
Suppose we have a max-LINSAT problem overFq with allowed setsF1, . . . , Fm of size|Fi| = r. Prange’s algorithm
[11] can be applied to this problem as follows. First, we subsample anyn constraints to enforce via a linear system on
the n variables. This system can then be solved with Gaussian elimination. Since we have disregarded the remaining
m − n constraints, we expect that roughlyr/q · (m − n) will be satisfied by chance since each constraint is satisfied
by r of theq. Thus, we get, in expectation, a solution that satisfiesn + r/q · (m − n) clauses. Prange’s algorithm can
be repeated to achieve any desired fraction of satisfied constraints, albeit potentially with an exponential overhead in
the number of repetitions. This is the most efficient classical attack on OPI that we are aware of. In Section IIIA,
we comment on how Prange’s algorithm could be optimized and show how to estimate the runtime required to match
DQI’s performance on a large supercomputer. Then in Section IIIB, we explain an improvement to Prange’s algorithm
over extension fields and the impact on the runtime estimates in Section V.
A. Optimizing Prange’s Algorithm
We first comment on how Gaussian elimination in Prange’s algorithm [11] can be optimized to avoid ann3 cost per
attempt. First, we can bring the generator matrixG ∈ Fn×m
q into row echelon form such that the leftmostn columns
form the identity matrix. We lete(1), e(2), . . . ,e(n) ∈ Span(G) denote the rows of this row echelon form. We can then
represent any codewordc as
c =
nX
i=1
cie(i). (16)
To iterate over the codewords that satisfy the firstn clauses, we can view the problem as iterating over the strings
where theci ∈ Fi above. Assume each|Fi| has size at least 2. Then we can iterate over strings that satisfy the first
n clauses using a Gray code that only updates two of the firstn coordinates per iteration. OverF2b, this could be
implemented as two vectorized SIMD operations per update.
