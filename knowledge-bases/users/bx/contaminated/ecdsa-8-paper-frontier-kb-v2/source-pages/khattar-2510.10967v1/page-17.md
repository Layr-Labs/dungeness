---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 17
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 17

The text below is a page-delimited extraction of the unchanged source PDF.

17
expected number of satisfied constraints by solving the following linear program (LP):
maximize
bX
s=0
psP[s]
subject to
bX
s=0
ps = 1
and
bX
s=0
sps ≤ bn/m
where ps ∈ [0, 1] ∀s ∈ {0, . . . , b}. (21)
The optimal value of the above LP gives the optimal expected fraction of satisfied constraints achieved by the XP. We
recover the truncation heuristic when we replaceAff with the setT := {{e} : e ∈ Fq}∪{ Fq}. There are exponentially
many affine subspaces inb, the degree of the field extension (e.g. whenp = 2 , |Aff| ∼7.37 · 2(b+1)2/4). But for
p = 2 and b ≤ 10, we have|Aff| < 109 and we can explicitly enumerate these to compute theP[s] table and solve
eq (21). Moreover, it seems unlikely we would really need to enumerate all the affine subspaces, since most of them will
have small overlap with the setF. Perhaps, using better heuristics or Fourier-analytic techniques, we could directly
compute the optimal allocation in timepoly(q). The XP can sometimes achieve a significantly higher expected value
than Prange’s algorithm. For example, overF4 with |F| = 2 and n/m = 1/2, XP has an expected value of1, whereas
Prange’s algorithm would give an expected value of3/4.
2. Probability-Optimal XP Allocation Strategies via a Knapsack Solver
If t is larger than the optimal expected fraction of satisfied constraints from eq (21), we may need to run the XP
many times to obtain one sample that satisfies≥ t clauses. Rather than maximizing the expectation value, we should
instead maximize the probability of obtaining a sample that satisfies≥ t clauses. The optimal-probability allocation
is the solution to the following problem:
maximize P
 mX
i=1
Xi ≥ t
!
subject to Xi ∼ Ber(P[si])
mX
i=1
si ≤ B
0 ≤ si ≤ b (22)
This problem is non-convex, and the solution may not be the same as the allocation strategy from eq (21). To obtain
good approximate solutions to equation (22), we use a dynamic programming algorithm explained in Appendix A.
3. Search for good target sets for OPI over binary extension fields
The choice of good target sets seems to be a nontrivial problem. For a fixed set size|F|, we want to make the
overlaps P[s] as small as possible for eachs ∈ {0, . . . , b}. This way, the XP allocation strategies of eq (21) and
eq (22) will have lower optimal values, giving a larger classical runtime. Identifying the optimal such setF or even
the best attainable list of overlapsP[s] appears to be an open problem. Some recent insight on a good way to choose
F came from [40], who performed algebraic cryptanalysis of the binary OPI problem in the case thatF is chosen
as the solution set of a multivariate polynomial equation (i.e., an algebraic variety). They concluded that for their
application, cubic or higher-degree varieties were required. This is because quadratic varieties contain many dimension
b/2 affine subspaces. They operated in a high-rate regime (specifically,n/m > 7/8) so that they could obtain an
exact solution with their quantum algorithm. The problem that then arises is that these affine subspaces are so large
that the number of linear equations sufficient to enforce them as constraints is small enough that a rate1/2 code
would already be able to satisfy every clause using XP. However, in our scenario, we propose to use DQI, which is an
approximate optimizationalgorithm. This allows us to keep the raten/m significantly lower than in [40] (in fact, the
