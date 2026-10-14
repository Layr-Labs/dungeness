---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 44
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 44

The text below is a page-delimited extraction of the unchanged source PDF.

Formal proof of the upper bound.Setρ= 2 +
√
3, λ=ρ1/3 = (2 +
√
3)1/3 andC={(a, b) T :a≥
b≥0}. Define the following four positive row vectors:
u0 := (1 +
√
3,1), u 1 :=λ −1u0M(1), u 2 :=λ −3u1M(4), u 3 :=λ −1u2M(1).
Equivalently, usingλ 3 −1 = 1 +
√
3,
u0 = (λ3 −1,1), u 1 =

λ2, λ3 −1
λ

, u 2 =
5
λ − 1
λ4 , 1
λ

, u 3 =
6λ3 −1
λ5 , 5λ3 −1
λ5

.
Forv∈ C, define
F(v) := min
0≤j≤3
ujv.
Since the coordinates of the four vectors are positive, it is easy to prove that the functionFis positive
onC \ {0}, homogeneous, concave, and coordinatewise nondecreasing. For the functionF, we have the
following lemma.
Lemma A.1.Letq≥1be a positive integer,d=⌊log 2 q⌋+ 1. For any vectorv∈ C, we have
F(M(q)v)≥λ dF(v).(13)
Moreover, ifd≥2, then
F

(q,1) T 
≥λ d−2F

(2,1) T 
.(14)
The overall upper bound of EEA step number follows directly from Lemma A.1. More precisely, we
have that
p
2 ·F

(2,1) T 
=F

(p, p/2)T 
≥F

(p, x)T 
(By Algorithm 1,x < p/2)
=F

M(q1)···M(q m−1)

qm
1
!!
(By Equation 10)
≥λ N/4−dmF

(qm,1) T 
(By Inequality 13)
≥λ N/4−2F

(2,1) T 
.(By Inequality 14, wherer m−1 ≥2 impliesd m ≥2)
This implies that
N/4≤2 + log2 p−1
log2 λ <2 + n−1
log2 λ <1 + n
log2 λ.
AsN/4 is an integer, we can conclude thatN≤4⌈cn⌉, wherec= 1/log 2 λ= 3/log 2(2 +
√
3).
What left is to prove Lemma A.1.
Proof of Lemma A.1.For row vectorsa, b, writea⪰ C bif (a−b)(1,0) T ≥0 and (a−b)(1,1) T ≥0. Since
each element inCcan be represented as a linear combination of (1,0) T and (1,1) T with nonnegative
coefficients, the relationa⪰ C bimpliesav≥bvfor everyv∈ C.
We first prove (13). Define the matrixG= (G j,s) forj= 0, . . . ,3 ands= 0, . . . ,3 by
Gj,s :=λ −s−1ujM(2s).
44
