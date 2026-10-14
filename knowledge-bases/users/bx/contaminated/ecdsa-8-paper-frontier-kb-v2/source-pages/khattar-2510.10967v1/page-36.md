---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 36
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 36

The text below is a page-delimited extraction of the unchanged source PDF.

36
1. Upper Bound on the objective function
The objective function of (A2) is upper bounded through a direct application of the Hoeffding Inequality by
P
 mX
i=1
Xi ≥ t
!
≤ exp

−2(t − E[Pm
i=1 Xi])2
m

(A8)
This upper bound is minimized by maximizingE[Pm
i=1 Xi] = Pm
i=1 P[si]. The functionP[s] is derived from (112)
as
P[s] =



1
2 − 1
2k+1 s = 0
1
2 s = 1
1
2 + 1
2k−s+2 1 < s≤ k
1 s > k
(A9)
If we letcj be the number of timessi = j then maximizing the expectation can be written as
maximize E
" mX
i=1
Xi
#
=
2kX
s=0
csP[s] (A10)
subject to
2kX
s=0
cs = m
2kX
s=0
css ≤ B = bn = bRm
Since the objective function is the expectation of the sum of m Bernoulli variables, its value is a fraction of
m = hm, 0 ≤ h ≤ 1 which can be substituted into (115) withh controlling the exponent of (116). We can compute
this expectation using a integer program or for large instances compute an upper bound by allowingcs to be real
rather than integer and solving the linear program. For the specificP[s] function in (A9) a simple strategy that uses
all of the budget to gets = k + 1 also maximizes the objective. This can be seen as follows. After spendings points
the expectation value is increased byP[s] − P[0]. To maximize our total expectation value we should spend in a way
that maximizes our gain per unit cost, i.e.(P[s] − P[0])/s. A brief analysis shows that this occurs fors = k + 1, so
the optimal solution to the LP should greedily allocate as much mass as possible ontopk+1.
Using this greedy approach we get an upper bound on the expectation
E
" mX
i=1
Xi
#
< P[k + 1]ck+1 + P[0]c0 (A11)
= B
k + 1 +
1
2 − 1
2k+1

m − B
k + 1

< B
k + 1 + 1
2

m − B
k + 1

= m
2 + 1
2
B
k + 1
< m
2 + 1
2
B
k
= m
2 + 1
2
2kRm
k
=
1
2 + R

m
