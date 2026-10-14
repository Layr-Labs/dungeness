---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 11
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 11

The text below is a page-delimited extraction of the unchanged source PDF.

11
FIG. 1: Evolution of the state of the system for our improved construction of Zalka’s reversible EEA [12, 16] with
in-register quotient storage which deterministically reduces the qubit counts to2nb + O(log n). Step-0 shows the
initial configuration of the system. Empty space corresponds to qubits in the|0⟩ state. The direction of the arrow
denotes the order in which the coefficients of the polynomials are stored, where the tip of the arrow stores the
highest degree coefficients and the tail stores the lowest degree coefficient. At each step, three key invariants are
satisfied - (a)deg(ui) + deg(ri) ≤ n, (b)deg(ri) < deg(ri−1) and deg(ui) > deg(ui−1) and (c)
deg(ui) + deg(ri−1) = n. Step-1 iteratively computes each term of the quotientqi+1 = ⌊ri−1/ri⌋ where
deg(qi+1) = deg(ri−1) − deg(ri) = m − deg(ui) − deg(ri), and thus the quotient is stored in-place within the shared
register storingui and ri. Step-2 performs right shift until the leader order coefficient ofri+1 is non-zero, such that
at the end of step 2, the polynomial long division is finished and we have successfully computed bothri+1 and qi+1
Step-3 iteratively right shiftsui−1 until deg(ui−1) = deg(ui). Step-4 iteratively computesui+1 = ui−1 − qi+1ui by
iteratively performingui−1 = (ui × qi+1,j − ui−1) × x for allj in [0, . . . ,deg(qi+1)]. The multiplication byx
corresponds to a right shift forui−1. Step-5 Swaps the two registers and finishes one logical iteration of the EEA.
Every symbol in the dialog representation must correspond to a small invertible matrix. When a representation has
this property, we call it alinear representation. Note that the binary representationis not linear, because the ‘1’
symbol needs to increment the accumulator, and this action does not correspond to a matrix multiplication. The
linearity of the dialog representation is a powerful property that allows us to perform complex algebraic manipulations
by simply operating on the dialog itself. For example:
• Direct Modular Division and Multiplication:Since the transformation from inputs to outputs is linear,
we can apply it to different vectors. To computeC(z)B(z)−1 (mod P(z)) where gcd(P(z), B(z)) = 1, we first
compute the Dialog representation of(P(z), B(z)). We can then apply the forward transformationτ total to the
scaled vector[0, C(z)]T . By linearity, this directly yields the result[C(z)B(z)−1, 0]T (mod P(z)) without ever
materializing the inverse. Similarly, we can also perform modular multiplication by applyingτ −1
total to the vector
[C(z), 0]T to obtain[0, B(z)]T (mod P(z)).
• Evaluating the Bézout Polynomial:To evaluate the Bézout Polynomialvm(z) at a pointγ ∈ Fq, we can
distribute the evaluation across the composition. We simply evaluate the polynomial entries of each transfor-
mation matrix τ i(z) at γ to get a sequence of constant matrices, and then multiply these constant matrices
together.
This linear representation is most powerful when the transformation matricesτ i are themselves simple. For this
reason, we construct the Dialog not from the classic EEA, but from constant-time, division-free algorithms like
Bernstein-Yang [17], whose steps correspond to simple, constant-time matrix operations such as these:
