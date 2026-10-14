---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 8
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 8

The text below is a page-delimited extraction of the unchanged source PDF.

8
This process is guaranteed to terminate because the degree of the remainder polynomial,deg(ri(z)), is a non-negative
integer that strictly decreases with each iteration. The algorithm stops when the remainderrm(z) becomes the zero
polynomial. At this point, the previous remainder,rm−1(z), is thegcd(A(z), B(z)), and the corresponding cofactors
um−1(z) and vm−1(z) are the final Bézout coefficients.
Each step of the EEA can be expressed as an application of a2 ×2 transition matrixτ i on the vector[ri−2, ri−1]T .
The product of the firsti transition matrices store the Bézout coefficientsui, ui−1 and vi, vi−1. This matrix repre-
sentation of the EEA will be useful as we describe our new constructions below.

ri−1
ri

=

0 1
1 −qi

| {z }
τ i

ri−2
ri−1
 
vi−1
vi

= τ i

vi−2
vi−1
 
ui−1
ui

= τ i

ui−2
ui−1

(10)
τ total = τ m · τ m−1 . . .τ 1 =

um−1 vm−1
um vm
 
gcd(A, B)
0

= τ total

A
B

(11)
One important application of the Extended Euclidean Algorithm is to compute multiplicative inverses in a finite
field Fq ∼= Fp[z]/P(z), where P(z) is an irreducible polynomial. To find the inverse of a polynomial A(z), one
applies the EEA toP(z) and A(z). This yields cofactor polynomialsu(z) and v(z) such thatP(z)u(z) + A(z)v(z) =
gcd(P(z), A(z)) = 1 . Taking this equation moduloP(z) gives A(z)v(z) ≡ 1 (mod P(z)), revealing that the Bézout
coefficient v(z) is the modular inverse. This operation is the principal computational bottleneck in Shor’s algorithm
for Elliptic Curve Cryptography (ECC), a cornerstone of modern public-key infrastructure. As a result, a significant
body of research, summarized in Table III and Table IV, has been dedicated to designing resource-efficient quantum
circuits for the EEA.
Early work by Kaye and Zalka [12] and Proos and Zalka [16] showed that the standard Euclidean Algorithm based
on polynomial long division is stepwise reversible and can be compiled using3nb + O(log n) qubits using a register-
sharing technique, where the registers holding the remainders and the Bézout coefficients are overlapped to use a
total of 2nb qubits and anothernb ancilla qubits are used to store the quotient in each iteration. By tolerating a
small error, they show how to further reduce the qubit counts down to2nb + O(log n), by using aO(log n) sized
register to store the quotients since large quotients occur relatively rarely in the EEA. Their circuit design relies on
a complex synchronization scheme, and they do not analyze the constant factors for gate counts. More recent works
[13, 14, 18, 34] focus on using constant-time division-free variants of the Extended Euclidean Algorithm, like Binary
GCD [21] and Bernstein-Yang GCD [17], to reduce the gate counts but suffer from significantly higher qubit counts
because each iteration of these constant-time EEA algorithms is not stepwise reversible and generates additional
garbage that leads to a higher ancilla overhead.
In this work, we provide two improved constructions for compiling the EEA, the first where the EEA explicitly
computes the Bézout coefficients in memory, and the second where it suffices to have an implicit representation of
Bézout coefficients. For both the constructions, we reduce the qubit counts to2nb + O(log n), which is the best one
can hope for given the input size is2nb, and our gate counts are lower than previous state of the art.
TABLE III: Cost of compiling the Extended Euclidean Algorithm for two degree-n polynomials overFq with
b = ⌈log2 q⌉. Gate cost is specified in terms of the number of calls to the dominant subroutine of quantum-quantum
multiplication of elements in the underlying fieldFq.
Source EEA Technique Qubit Cost Dominant gate cost
Kaye and Zalka [12] Euclids GCD 3nb + O(log2 n) 12n2 multiplications
Roetteler et al.[13] Binary GCD 4nb + 2n + O(log n) 4n2 multiplications
Banegas et al.[18] Bernstein-Yang GCD 4nb + n + O(log n) 4n2 multiplications
Kim and Hong [34] Bernstein-Yang GCD4nb + 0.5n + O(log n) 4n2 multiplications
This Work (Explicit Bézout) Euclids GCD 2nb + O(log2 n) 6n2 multiplications
This Work (Implicit Bézout)Bernstein-Yang GCD 2nb + O(log2 n) 2n2 multiplications
1. Explicit versus Implicit Access to Bézout Coefficients
A key theme of our work is the optimization of quantum circuits by carefully considering how the results of the
EEA are used by the broader algorithm. We distinguish between two computational models: one requiringexplicit
