---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 14
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 14

The text below is a page-delimited extraction of the unchanged source PDF.

14
a. Solving the Key Equation: The core of the decoding process is to solve the fundamental key equation, a
polynomial congruence that relates the knownS(z) to two unknown polynomials: the error-locator polynomialσ(z)
and the error-evaluator polynomialΩ(z):
σ(z)S(z) ≡ Ω(z) (mod z2ℓ). (12)
Here, ℓ = n
2 is the maximum number of errors that the code can correct,σ(z) is called the error-locator polynomial
because its roots identify the error positions, andΩ(z) is called the error-evaluator polynomial and is used to find the
error magnitudes [6, 24]. A unique solution exists ifdeg(σ(z)) = |e| ≤ℓ and deg(Ω(z)) < ℓ.
This polynomial congruence can be solved using several algorithms, most notably the Berlekamp-Massey algorithm
[6] or the Extended Euclidean Algorithm (EEA) [7]. To solve it using EEA, we apply the EEA to the two specific
polynomials A(z) = z2ℓ and B(z) = S(z). As established in the previous section, the EEA produces a sequence of
remainders ri(z) and corresponding Bézout coefficientsui(z) and vi(z) such that:
A(z)ui(z) + B(z)vi(z) = ri(z). (13)
Taking this identity moduloA(z) = z2ℓ, the first term vanishes, leaving:
S(z)vi(z) ≡ ri(z) (mod z2ℓ). (14)
This directly matches the form of the key equation Eq. (12), withσ(z) ∝ vi(z) and Ω(z) ∝ ri(z). The algorithm is
halted at the first iterationi where deg(ri(z)) < ℓ, which guarantees that the degree constraints for a valid solution
are met.
Our quantum circuits for EEA perform this first step using either the synchronized algorithm of Section IIB2 for
explicit access to bothσ(z) and Ω(z), or the Dialog-based method of Section IIB3 for implicit access toσ(z) and
explicit access toΩ(z). The efficiency of the subsequent decoding stages depends on which model is used.
b. Chien Search and Forneys algorithm: Once the key equation has been solved via the EEA, yielding the error-
locator polynomialσ(z) and the error-evaluator polynomialΩ(z), the decoder proceeds in two final stages. First, the
Chien search [23] finds the error locations by identifying the roots ofσ(z). This is achieved by evaluatingσ(z) at
every non-zero element of the field,γj ∈ F∗
q. An error is located at positionj if σ(γ−1
j ) = 0. Second, For each error
location j found by the Chien search, Forney’s algorithm [24] computes the corresponding error valueej using the
formula:
ej = −
Ω(γ−1
j )
σ′(γ−1
j ), (15)
where σ′(z) is the formal derivative ofσ(z). This requires evaluating bothΩ(z) and σ′(z) at the pointγ−1
j , followed
by a modular division.
The implementation of these two steps differs significantly between the access models. In theexplicit model, the
EEA provides the coefficients ofσ(z) and Ω(z) directly. The Chien search and Forney’s algorithm then proceed by
evaluating these polynomials (and the easily computed derivativeσ′(z)) at each pointγ−1
j using n quantum-classical
multiplications per evaluation. In contrast, theimplicit modelprovides the Dialog of lengthn = 2ℓ for σ(z), while still
providing Ω(z) explicitly as the final remainder. Here, evaluatingσ(γ−1
j ) and σ′(γ−1
j ) is achieved by playing back the
Dialog on an augmented state vector. Since differentiation is a linear operator, we can track the derivative through
the sequence of linear transformations by applying the chain and product rules. This requires2n quantum-quantum
multiplications andn/2 quantum-classical multiplications per evaluation.
The quantum resource costs for these stages depend heavily on whether the explicit or implicit access model was
used for the initial EEA step. The trade-off is summarized in Table V. The dominant costs arise from sequences
of Galois field multiplications, which are categorized as either quantum-quantum (QQ), where both operands are in
quantum registers, or quantum-classical (QC), where one operand is a known classical value.
