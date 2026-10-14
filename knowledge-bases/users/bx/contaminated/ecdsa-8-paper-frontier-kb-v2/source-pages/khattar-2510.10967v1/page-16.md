---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 16
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 16

The text below is a page-delimited extraction of the unchanged source PDF.

16
The semicircle law of [4] states that DQI will satisfyt clauses in expectation, where
t/m =
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
. (17)
Suppose we apply the classical attack to find a solution satisfying at leastt of the m clauses, where t > n. The
number of satisfied clauses is distributed binomially, and the probability of sampling such a solution is:
p(t) :=
mX
s=t
m − n
s − n
 r
q
s−n 
1 − r
q
m−s
. (18)
To match this with the classical attack will take, in expectation,1/p(t) trials. We estimate the classical resources
required for one trial, using the Frontier supercomputer as an example [37]. Frontier contains 37,632 AMD Instinct
MI250X accelerators (i.e., GPUs). Each MI250x has 220 compute units (CUs) and runs at 1.7 GHz. Each CU has
4 SIMD lanes. So, we can imagine that with an optimized implementation, Frontier could potentially run this many
trials of the heuristic in one day:
24 × 3600 × 1
2 × 37, 632 × 220 × 4 × 1.7 × 109 ≈ 2.43 × 1021 (19)
Note that no networking is required for our classical attacks (i.e., they are embarrassingly parallel), so we could easily
distribute the workload over the Internet to many independent machines that run at different times, in odd hours,
etc.
B. Extended Prange’s Algorithm over Extension Fields
The eXtended Prange’s algorithm (XP) is a folklore algorithm alluded to in [38], although we do not know of a
reference that fully formalizes it as a cryptanalytic attack. For simplicity, supposeF1 = F2 = . . .= Fm = F. Suppose
q = pb for primep. Let
ϕ :Fpb ↔ Fb
p
ϕ(x) = (tr (ζx) : ζ ∈ B) (20)
denote the natural bijection from elements inFpb to vectors inFb
p, whereB is any basis forFpb over Fp and tr(α) =Pb−1
i=0 αqi
is the field trace (See Ch. 2 of [39]). LetAff ⊆ 2Fb
p denote the set of nonempty affine subspaces ofFb
p. For
each codimensions ∈ {0, 1, . . . , b}, letAs ∈ Aff denote the(b − s)-dimensional affine subspace which has thelargest
intersection |A ∩ ϕ(F)| with the setϕ(F), and letP[s] denote its fractional overlap byP[s] := |A∩ϕ(F)|
|A| . The general
idea is that if we “pay”s affine constraints over the base field on one of the coordinatesi ∈ [m], then we get to flip a
P[s]-biased coin that determines whether theith constraint is satisfied. We have a budget ofn·b base field constraints
to spend. We call any budget-respecting strategy which assigns a value ofs to each coordinatei an “XP Allocation
Strategy”. We consider two such strategies below.
1. Expectation-Optimal XP Allocation Strategies via Linear Programming
We can use a randomized procedure to decides for each clause. For each clause, this strategy sampless indepen-
dently according to the discrete probability distributionps. This distribution is constrained such that, on average,
we usebn/m Fp-linear constraints, meaning we are exactly within-budget. It can be optimized to get the maximum
