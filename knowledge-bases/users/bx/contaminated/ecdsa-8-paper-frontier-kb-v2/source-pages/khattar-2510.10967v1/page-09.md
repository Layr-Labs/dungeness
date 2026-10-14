---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 9
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 9

The text below is a page-delimited extraction of the unchanged source PDF.

9
access to the Bézout coefficients, and another whereimplicit access is sufficient. This distinction allows us to select
the most resource-efficient EEA implementation for the task at hand.
As outlined at the beginning of this section, any execution of the EEA can be viewed as generating a sequence of
2 × 2 transition matrices, τ 1, τ 2, . . . ,τ m. The product of these matrices,τ total = τ m · τ m−1 ··· τ 1, contains the
final Bézout coefficients as its entries.
• Explicit Access:This is the conventional model, where the primary goal of the EEA circuit is to compute and
store the full product matrixτ total. In the context of polynomial inputs, this means computing the coefficients
of the final Bézout polynomials (e.g.,vm−1(z)) and storing them explicitly in a quantum register. This approach
is necessary when the full polynomial is required for subsequent algebraic manipulations.
• Implicit Access. In this model, we avoid the costly step of multiplying the sequence of transition matrices.
Instead, we only compute and store a compact representation of each individual matrixτ i. This metadata is
sufficient to reconstruct and apply eachτ i on the fly. The full Bézout coefficients are never materialized in
memory but existimplicitly as the result of applying the sequence of stored transformations. Any operation
requiring the Bézout coefficients is simply reformulated as a sequential application of theτ i matrices.
We illustrate the power of this implicit approach with two concrete examples:
1. Modular Polynomial Division:Consider the task of computingA(z)B(z)−1 (mod P(z)), whereP(z) is an
irreducible polynomial.
• The explicit “invert-then-multiply” approach first runs EEA(P, B) to explicitly compute and store the
inverse polynomialvm−1(z) = B(z)−1 (mod P(z)). It then performs a separate quantum-quantum multi-
plication ofA(z) by this inverse polynomial.
• The implicit “direct division” approach instead runs EEA(P, B) to generate the sequence of matrices
τ 1, τ 2, . . . ,τ m. To compute the division, it applies a sequence of matrix-vector multiplications to a differ-
ent input vector,[0, A(z)]T . The final state after applyingτ total is precisely[A(z)B(z)−1, 0]T (mod P(z)),
avoiding the need to ever store the full inverse polynomial.
We compare the costs of these approaches for modular division in Table IV.
2. Polynomial Evaluation: Consider evaluating the Bézout coefficient polynomialvm−1(z) at a specific point
γ ∈ Fq.
• With explicit access, one would use the stored coefficients ofvm−1(z) and perform a standard polynomial
evaluation (e.g., via Horner’s method), requiring a series of quantum-classical multiplications.
• With implicit access, we first evaluate the simple polynomial entries within each transition matrixτ i at
the point γ. This yields a sequence of constant2 × 2 matrices with entries inFq. We then apply this
sequence of constant matrices to an initial vector, such as[0, 1]T . The result of these operations overFq
is the desired value,vm−1(γ). Once again, we did not ever store the full Bézout coefficient polynomial
vm−1(z) in memory.
Our work provides optimized circuits for both models. For explicit access, we improve upon the synchronized
algorithm by Proos and Zalka [16], while for implicit access, we use the constant-time division-free variants of EEA
[17, 21] as basis for theDialog representation detailed in the following subsections.
TABLE IV: Cost of compiling modular division using Extended Euclidean Algorithm for two degreen polynomials
over Fq with b = ⌈log2 q⌉. Gate cost is specified in terms of the number of calls to the dominant subroutine of
quantum-quantum multiplication of elements in the underlying fieldFq. We wish to achieve
|A(z)⟩b |B(z)⟩b → |junk⟩| A(z)
B(z) (mod p(z))⟩
b
. When accounting for qubit costs, we assume multiplication of two
elements inFq does not consume any ancilla.
Source Approach Qubit Cost Gate cost
Kaye and Zalka [12] invert-then-multiply 4nb + O(log2 n) 13n2 multiplications
Roetteler et al.[13] invert-then-multiply 6nb + 2n + O(log n) 5n2 multiplications
Banegas et al.[18] invert-then-multiply 6nb + n + O(log n) 5n2 multiplications
Kim and Hong [34] invert-then-multiply 6nb + 0.5n + O(log n) 5n2 multiplications
This Work (Explicit Bézout)invert-then-multiply 4nb + O(log2 n) 7n2 multiplications
This Work (Implicit Bézout) direct-division 4nb + O(log2 n) 4n2 multiplications
