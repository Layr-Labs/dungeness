---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 35
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 35

The text below is a page-delimited extraction of the unchanged source PDF.

35
To solve the problem we employ a knapsack like dynamic programming approach. Dynamic programming is a
constructive paradigm and since we are building an approximation algorithm the order we choosesi affects the
quality of the result. Eq (A3) shows that as we construct our solution the joint probability distribution induced by
our choices ofsi flows in the direction of increasingPXi. We also note that the change in the joint distribution
from P(•|s1 ··· sk) to P(•|s1 ··· sksk+1) is controlled byP(1|sk+1) which from eq (A1) is monotonic, from these two
observation we find that it is advantageous to choose thesi values in descending orders1 ≥ s2 ≥ ··· ≥sm. The
advantage of this ordering is two folds, the first is that after the first few choices ofsi the joint probability distribution
stabilizes from one choice to another, the second is computational since it reduces the runtime of the algorithm.
P
 k+1X
i=1
Xi ≥ t|s1 ··· sksk+1
!
=
P
 kX
i=1
Xi ≥ t|s1 ··· sk
!
+ P (1|sk+1) P
 kX
i=1
Xi = t − 1|s1 ··· sk
!
(A3)
Our solution has a dynamic programming state of(i, budget, low) which means for the firsti variables and budget
budget ≤ B and ∀j≤isj ≥ low what is the best joint probability distribution. This state has only two transitions
(i, budget, low) → (i, budget, low + 1) and (i, budget, low) → (i − 1, budget − low, low). To compare between the up
to two probability distributions we get from these transitions we used two comparison functions.
The first comparison function is eq (A5), which is quick and for most test cases we generated was at most5%
lower than the optimal result with some outliers with a bigger error. The second is eq (A6) which is slower since
it involves computing the convolution between the probability distribution induced by our tuples1 ··· sk and the
one induced by the sequence computed by eq (A7). The intuition behindF which is computed using the classical
dynamic programming knapsack algorithm is that we are doing a look ahead trying to estimate the best probability
distribution given the remaining budget, but for computational reasons instead of solving the original problem we
solve the related easier problem of maximizing the sum of probabilities, this gives us a better lower bound on the
best final joint probability distribution starting from the givenS. Note that, eq (A5) is a special case of eq (A6)
since it can be interpreted as the convolution of the current probability distribution with the probability distribution
P(0) = 1.
T(S) = (P(
X
Xi ≥ t|S), P(
X
Xi = t − 1|S), P(
X
Xi = t − 2|S), ··· , P(
X
Xi = 0|S)) (A4)
S1 ≥ S2 ⇐⇒ T(S1) ≥ T(S2) (A5)
S1 ≥ S2 ⇐⇒ T(S1 + F(m − k, budget −
X
s∈S1
si, s(1)
k ) ≥ T(S2 + F(m − k, budget −
X
s∈S2
si), s(2)
k ) (A6)
S1 + S2 = (s(1)
1 , ··· , s(1)
a ) + (s(2)
1 , ··· , s(2)
b )
= (s(1)
1 , ··· , s(1)
a , s(2)
1 , ··· , s(2)
b )
F(m, budget, low) = argmaxs1···sm
mX
i=1
P[si]
subject to
X
si ≤ budget
and si ≥ low (A7)
We were unable to find a case where the dynamic programming approach with the slow sorting relation eq (A6)
disagrees with brute force solution. Although such cases theoretically exist we believe the error will be small. The time
complexity of this solution isO(mbBt) with the fast sorting relation andO(mbBt2) with the slow sorting relation.
