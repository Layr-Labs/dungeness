---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 47
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 47

The text below is a page-delimited extraction of the unchanged source PDF.

Location-controlled addition/subtraction onr’s.First, observe thatt jqj ≤t j+1 < p, which
impliesℓ t +b j ≤n+ 1. Since a location-controlled addition/subtraction onr’s is only activated in Phase
1 and 2, i.e. 0< u≤2(b j + 1), we then analyze the claimed bound by considering two cases.
•Case 1.Suppose thatu≤b j + 1. In this case, we haveℓ q = 0. By Lemma A.2, it follows that
ℓt > T−u−4δ
4c ≥ T−(n+ 1−ℓ t)−4δ
4c .
Henceℓ t +ℓ q =ℓ t > T−n−1−4δ
4c−1 .
•Case 2.Suppose thatb j + 1< u≤2(b j + 1). Thenℓ q =u−(b j + 1), and we obtain that
ℓt +ℓ q > T−u−4δ
4c +u−(b j + 1).
The right-hand side is minimized whenu=b j + 1, in which case the expression reduces to that of
Case 1.
Combining the two cases, we conclude thatℓ t +ℓ q + 2≥max
T−n−1−4δ
4c−1

,1

+ 2.
Location-controlled swaps.For the lower bound, a location-controlled swap is only activated in
Phase 2 and 3, i.e.b j + 1< u≤3(b j + 1), we then analyze the claimed lower bound by considering two
cases.
•Case 1.Suppose thatb j + 1< u≤2(b j + 1). In this case, we also haveℓ t +ℓ q ≥ T−n−1−4δ
4c−1 .
•Case 2.Suppose that 2(b j + 1)< u≤3(b j + 1). In this case, we haveℓ q = 3(bj + 1)−u. By
Lemma A.2, it follows that
ℓt ≥ T−u−4δ
4c ≥ T−3(n+ 1−ℓ t)−4δ
4c ,
henceℓ t +ℓ q ≥ℓ t ≥ T−3(n+ 1)−4δ
4c−3 .
The Case 1 bound is no smaller than the Case 2 bound throughout the active range. Indeed, their
difference equals 2(4cn+ 4c+ 4δ−T)
(4c−1)(4c−3) >0,where we usedT≤N max <4cn+ 4. Combining the two
cases, we conclude thatℓ t +ℓ q + 1≥max
T−3(n+ 1)−4δ
4c−3

,1

+ 1.
For the upper bound, recall the recurrence relation of the EEA on thet-sequence, that ist i+1 =
ti−1 +q iti <(q i + 1)ti ≤2 bi+1ti. By iterating this inequality, we obtain that
t=t j ≤
j−1Y
i=1
2bi+1 = 2(T−u)/4 ,and thenℓ t ≤(T−u)/4 + 1.
By Equation (16), we know thatℓ q ≤u/2. Hence,
ℓt +ℓ q + 1≤ ⌊(T−u)/4 +u/2 + 2⌋=⌊(T+u)/4⌋+ 2≤ ⌊T/2⌋+ 2.
Finally, since theWork1register stores a valuer≥1, we conclude thatℓ t +ℓ q + 1≤n+ 2.
47
