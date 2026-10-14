---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 3
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 3

The text below is a page-delimited extraction of the unchanged source PDF.

3
Problem Classical Runtime Quantum
Gate Cost
Gate Cost (for clas-
sical runtime2N )
Factoring 2
eO(n1/3) (GNFS) eO(n2)† eO(N6)
Jacobi Factoring 2
eO(n1/3) (GNFS) eO(n) eO(N3)
Elliptic Curve Cryptography 2
eO(n) (Pollard Rho) eO(n2) eO(N2)
OPI 2n (Extended Prange) eO(n) eO(N)
Best Possible 2n n Ω(N)
TABLE I: Asymptotic costs for verifiable quantum advantage with classical hardness2N . †By [5], one can factorn
bit integers by running√n + 4 quantum circuits ofeO(n3/2) gates. In this case, the overall circuit size is stilleO(n2),
but even counting a single quantum circuit, the quantum gate cost for classical runtime2N is N4.5.
The DQI algorithm addresses max-LINSAT by defining a related objective function,f(x), as the number of satisfied
constraints minus the number of unsatisfied constraints. This can be expressed as:
f(x) =
mX
i=1
fi


nX
j=1
Bijxj

, where fi(y) =
(
+1 if y ∈ Fi
−1 if y /∈ Fi
. (1)
Maximizing f(x) is equivalent to maximizing the number of satisfied constraints. The DQI algorithm works by
preparing a quantum state|P(f)⟩ = P
x P(f(x))|x⟩, where P is a polynomial of degreeℓ designed to enhance the
amplitudes of states|x⟩ wheref(x) is large. The core insight of DQI is that the preparation of this state can be reduced
to a decoding problem on the dual codeC⊥ = {d ∈ Fm
q : BT d = 0}. The algorithm involves creating a superposition
of errorse and their syndromesBT e. To achieve the necessary interference that amplifies good solutions, the error
register |e⟩ must be coherently uncomputed, which necessitates a reversible quantum implementation of a decoder for
C⊥. The performance of DQI is directly tied to the error-correction capability of this decoder. The degreeℓ of the
enhancing polynomial P corresponds to the maximum number of errors the decoder must correct. A key result of
the DQI framework [4] is the semicircle law, which provides a rigorous performance guarantee based on the decoding
capability.
Theorem I.3(DQI Semicircle Law (Informal) [4]). Given a max-LINSAT instance where the allowed setsFi have
size r over a field of sizeq. If the dual codeC⊥ can be efficiently decoded up toℓ errors, DQI can sample solutions
that satisfy an expected fraction of constraints⟨s⟩/m approaching:
 s
ℓ
m

1 − r
q

+
s
1 − ℓ
m
 r
q
!2
. (2)
This theorem formalizes the intuition that a better decoder (a larger correctable error fractionℓ/m) leads to a
better optimization result. Consequently, the efficiency of the reversible decoder dominates the resource requirements
of the entire DQI algorithm.
In this work, we focus on constructing efficient quantum circuits for DQI applied to the Optimal Polynomial
Intersection (OPI) problem, identified in [4] as a candidate for superpolynomial quantum speedup.
Definition I.4(Optimal Polynomial Intersection (OPI)). Let Fq be a finite field andn < q− 1. Given m = q − 1
subsets Fy ⊂ Fq for eachy ∈ F∗
q, find a polynomialQ ∈ Fq[y] of degree at mostn − 1 that maximizes the objective
function: fOPI(Q) = |{y ∈ F∗
q : Q(y) ∈ Fy}|.
When OPI is cast as max-LINSAT, the constraint matrixB is a Vandermonde matrix, implying the dual code
C⊥ is a Reed-Solomon (RS) code. For OPI, DQI can achieve approximation ratios that appear beyond the reach of
known polynomial-time classical algorithms [4]. RS codes possess efficient classical decoders, such as the Berlekamp-
Massey decoder [6] or the Extended Euclidean Algorithm (EEA) [7]. Our primary contribution is the development of
highly optimized, reversible quantum circuits for syndrome decoding of Reed-Solomon codes using Extended Euclidean
Algorithm-based decoders. We introduce several key strategies to minimize the quantum resources required:
1. Analysis of OPI over Binary Extension Fields:We shift the analysis from prime fields to binary extension
fields, GF(2b). This choice significantly reduces the cost of the underlying quantum arithmetic (leveraging
