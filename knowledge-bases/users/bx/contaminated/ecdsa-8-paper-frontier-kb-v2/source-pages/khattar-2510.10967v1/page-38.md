---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 38
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 38

The text below is a page-delimited extraction of the unchanged source PDF.

38
2. Divide and Conquer Unranking for eO(m) Dicke State Preparation
We first describe a Divide and Conquer strategy for fast unranking. Given inputs(m, k, r), we split them elements
into two halves,M1 and M2, of sizesm1 = ⌊m/2⌋ and m2 = ⌈m/2⌉, and then calculate:
1. The number of elementsk1 and k2 that the combinationC(r) selects from the first (M1) and second halves
(M2) respectively, such thatk1 + k2 = k.
2. The residual ranksr1 and r2, such thatCm,k(r) = Cm1,k1 (r1)∥Cm2,k2 (r2).
The unranking problem can then be solved by recursively solving the left and right subproblems for(m1, k1, r1)
and (m2, k2, r2). If the work done at one level of recursion isW(m, k), then the overall complexity ofUUnrank follows
the following recurrence relation:
T(m, k) = T(m/2, k1) + T(m/2, k− k1) + W(m, k)
If we can show that W(m, k) = eO(m), then by Master Theorem (Case 2), the total complexity is T(m, k) =
eO(m log m), which iseO(m).
The number of ways to choosek items such that exactlyi items come fromM1 is given by the Hypergeometric
distribution:
H(i) =
m1
i
 m2
k − i

To find the correctk1 for rankr, we seek the value such that the prefix sum ofH(i) crosses r:
P S(k1) =
k1−1X
i=0
H(i) ≤ r < P S(k1 + 1)
We can findk1 using a binary search inO(log k) steps, provided we can efficiently calculate the prefix sumP S(x).
Once k1 is found, we calculate the residual ranksr1 and r2 corresponding to the left and right subproblems (via
division and modulo operations onr − P S(k1)), and recursively solve them.
The efficiency of this approach hinges on the fast calculation of the Hypergeometric prefix sumP S(x). The numbers
involved (ranks and binomial coefficients) have bit lengthL = O(k log m). A naive summation ofO(k) terms is too
slow. We use a technique calledBinary Splitting. This method is effective for evaluating series where the ratio of
consecutive termsR(i) = H(i + 1)/H(i) is a simple rational function ofi:
R(i) = (m1 − i)(k − i)
(i + 1)(m2 − k + i + 1)
The prefix sum can be written asP S(x) = H(0) · (1 +R(0) +R(0)R(1) +. . .). Binary Splitting recursively computes
this expression in a balanced tree structure. Crucially, it leverages fast integer multiplication algorithms (e.g., Schön-
hage–Strassen), which multiplyL-bit numbers in timeeO(L). The total time complexity for calculatingP S(x) using
Binary Splitting is thuseO(L log k) = eO(k log m).
The divide and conquer algorithm can be implemented as a reversible quantum circuitUUnrank.
1. Reversible Fast Arithmetic:We require efficient reversible quantum circuits for fast integer multiplication
and division that maintain theeO(L) complexity for arithmetic overL bit integers.
2. Reversible Binary Splitting (UBS ): The Binary Splitting procedure is implemented reversibly using the fast
arithmetic circuits. The gate complexity ofUBS is eO(k log m).
3. Reversible Search: The binary search fork1 is implemented using the reversible Bit-wise Quantum Search
strategy. This requiresO(log k) coherent calls toUBS .
The work done at one level of the recursion,W(m, k), is dominated by the reversible search:
W(m, k) = O(log k) · Cost(UBS ) = eO(k log m) = eO(m)
