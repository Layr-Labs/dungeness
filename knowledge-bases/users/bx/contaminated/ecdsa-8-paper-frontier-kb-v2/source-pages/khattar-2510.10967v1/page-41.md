---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 41
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 41

The text below is a page-delimited extraction of the unchanged source PDF.

41
FIG. 7: GF(23) multiplication with irreducible polynomialx3 + x + 1 in terms of PCTOF gates.
FIG. 8: Construction of measurement based uncomputation of GF2 multiplication for irreducible polynomial
x3 + x + 1. Note that the measurement is in the X basis.
Appendix D: Bounding the number of iterations for Synchronized Reversible Polynomial EEA
We analyze the worst-case number of iterations required for the synchronized, reversible implementation of the
Polynomial Extended Euclidean Algorithm (PEEA) presented in Section IIB2. This implementation utilizes shared
registers and a 4-stage synchronized architecture designed to allow computation branches in a superposition to proceed
efficiently at their own pace.
Let the input polynomials beA and B over a finite fieldFq, withn = deg(A) and deg(B) < n.
Definition D.1(Iteration Dynamics). For iterationi (which computes quotientQi, remainderRi, and cofactorUi):
• di = deg(Qi). We defined0 = 0. Since deg(B) < deg(A), di ≥ 1 for i ≥ 1.
• si = deg(Ri−1) − deg(Ri): The degree reduction of the remainder.si ≥ 1.
Let k be the total number of iterations. LetDk = Pk
i=1 di and Sk = Pk
i=1 si.
