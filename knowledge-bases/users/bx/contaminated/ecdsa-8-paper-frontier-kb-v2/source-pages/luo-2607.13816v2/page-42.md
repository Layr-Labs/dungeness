---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 42
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 42

The text below is a page-delimited extraction of the unchanged source PDF.

For integerq≥1, define the EEA transformer matrixM(q) :=

q1
1 0
!
.The EEA iteration can
therefore be written as (ri−1, ri)T =M(q i)(ri, ri+1)T .Iterating this identity and using (r m, rm+1) = (1,0)
gives
p
x
!
=M(q 1)···M(q m)

1
0
!
=M(q 1)···M(q m−1)

qm
1
!
.(10)
In particular,
p=K(q 1, . . . , qm) :=e T
1 M(q1). . . M(qm)e1.(11)
Given equation (11), writingd(q) :=⌊log 2 q⌋+ 1, our problem is to find a slowest growth pattern for
products of the matricesM(q) with a fixed weight sumN/4 = Pm
i=1(d(qi) + 1), where a factorM(q)
has weightd(q). Experiments for small total quotient bit-lengths suggest that, with Pd(q) fixed, the
quotient sequence (1,2) has the minimum averaged growing rate, i.e. the nearly alternating quotient
sequence (2,1,2,1, . . . ,2,1,2,2) asymptotically minimizes the resulting value ofp.
Sincepis the upper-left and largest entry ofP:=M(q 1)···M(q m), we havep≤ρ(P)≤ ∥P∥ ∞ ≤2p,
hereρ(P) denotes the spectral radius, i.e. the maximum absolute value of eigenvalues, and∥P∥ ∞ denotes
the maximum row sum. Sophas the same order of magnitude with the spectral radius of the matrix
productP. Therefore, the repeated block (1,2) in the quotient sequence suggests the asymptotic growth
rate: it has total weight 3, whileM(1)M(2) =

3 1
2 1
!
has spectral radius 2 +
√
3. This motivates the
normalizationρ:= 2 +
√
3 andλ:=ρ 1/3, so that one unit of weight corresponds to a factorλ.
We then give the formal argument on the aymptotic sharpness of the constantc. Fork≥0, consider
a quotient sequence
Qk =

2,1,2,1,2, . . . ,1,2| {z }
kcopies of (1,2)
,2

,
its corresponding step number isN k = 12k+16. LetM:=M(1)M(2) =

3 1
2 1
!
be a two-iteration EEA
transformation matrix with maximal eigenvalueρ= 2+
√
3. From basic linear algebra argument, the value
ofp=e T
1 M(2)M kM(2)e1 = (2,1)M k(2,1) T will asymptotically be bounded by Θ(ρ k). Consequently,
log2 pk =klog 2 ρ+O(1), and
lim
k→∞
Nk
log2 pk
= 12
log2 ρ = 4c.
Therefore, the coefficientcin the upper bound forN≤4⌈cn⌉cannot be decreased for general admissible
quotient sequences.
In the rest of this section, we will discuss the roadmap for proving this sharp upper bound, and then
give the formal proof.
Roadmap for the proof of the upper bound.We consider the invariant cone
C:=
(
a
b
!
:a≥b≥0
)
,
42
