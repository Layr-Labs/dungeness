---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 18
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 18

The text below is a page-delimited extraction of the unchanged source PDF.

18
space cost scaling is dominated byn, so the lower the rate of the code, the better). Although we do not obtain exact
solutions, we obtain better approximate optima than can be obtained in polynomial time by any algorithm known to
us, which is sufficient to obtain the large speedups here.
In fact, we find that a particular quadratic variety is an excellent choice to get a quantum advantage. Specifically,
we chose bent functions from the Maiorana-McFarland family. In more detail, letn = 2k. Let
Sk =
(
(x1, ..., xn) ∈ Fn
2 :
kX
i=1
xixi+k = 1 mod 2
)
. (23)
As we show in Section IIIB4, for any affine subspaceA ⊂ Fn
2 of dimensiond = dim A, we have
|A ∩ Sk| ≤



2d d < k
2d−1 + 2k−2 k ≤ d <2k − 1
22k−2 d = 2k − 1
22k−1 − 2k−1 d = 2k.
(24)
This can be fed as input to the knapsack solver described in Appendix A.
4. Upper bounds on affine intersections of Maiorana-McFarland target sets
We have found a technical proof of the upper bounds in (24), although we believe a simpler proof may be possible.
All the key concepts involved are present in the proof for affine spaces withk ≤ dim A <2k − 1. Therefore, we defer
the proofs of upper bounds ford < k, d = 2k − 1, andd = 2k to Appendix E and focus here onk ≤ d <2k − 1.
Let k be a positive integer. We use the standard dot product⟨x, y⟩ := Pk
i=1 xiyi ∈ F2 where x, y∈ Fk
2 to define
Rk :=

(x, y) ∈ Fk
2 × Fk
2 : ⟨x, y⟩ = 0

(25)
Sk :=

(x, y) ∈ Fk
2 × Fk
2 : ⟨x, y⟩ = 1

(26)
so thatRk ∪Sk = F2k
2 andRk ∩Sk = ∅. We will use⊔ to make simultaneous assertions about the union and intersection
of two sets. Namely, we defineX ⊔ Y = Z ⇐⇒ (X ∪ Y = Z) ∧ (X ∩ Y = ∅) for any three setsX, Y , andZ. Thus,
Rk ⊔ Sk = F2k
2 . In arguments below, we will make frequent use of the implicationX ⊔ Y = Z =⇒ |X| + |Y | = |Z|.
We begin by derivingrecursive structure formulasthat express the setsA ∩ Rk and A ∩ Sk as the disjoint union⊔
of the sets of the formB ∩ Rk−1 and B ∩ Sk−1 for some affine subspacesB ⊂ F2k−2
2 . To that end, we use two linear
projections π0 : F2k
2 → F2k−2
2 and π1 : F2k
2 → F2
2 defined by
π0(xayb) = xy, π 1(xayb) = ab (27)
where x, y∈ Fk−1
2 and a, b∈ F2 and where juxtaposition denotes concatenation. For aw ∈ F2k
2 , we will refer toπ0(w)
as the root of w and to π1(w) as the suffix of w. The map (π0, π1) : F2k
2 → F2k−2
2 × F2
2 is invertible. Its inverse is
⊗ : F2k−2
2 × F2
2 → F2k
2 defined as
xy ⊗ ab = xayb (28)
where x, y∈ Fk−1
2 and a, b∈ F2 as before. ForX ⊂ F2k−2
2 , Y ⊂ F2
2, ands ∈ F2
2, we will writeX ⊗ s = {x ⊗ s |x ∈ X}
and X ⊗ Y = {x ⊗ y |x ∈ X, y∈ Y }. Note that|X ⊗ Y | = |X| · |Y |.
The recursive structure ofA ∩ Rk and A ∩ Sk arises from
⟨x, y⟩ = ⟨π0(x), π0(y)⟩ + ⟨π1(x), π1(y)⟩ (29)
where we slightly abused notation by using⟨., .⟩ to refer to the dot product in three different vector spaces,F2k
2 , F2k−2
2 ,
and F2
2. We now state and prove the recursive structure formulas.
Lemma III.1(Recursive Structure Formulas).
For integersd ≥ k >1, letA be ad-dimensional affine subspace ofF2k
2 . Then
A ∩ Rk =
G
σ∈F
(
(A′
σ ∩ Sk−1) ⊗ σ if σ = 11
(A′
σ ∩ Rk−1) ⊗ σ if σ ̸= 11 (30)
A ∩ Sk =
G
σ∈F
(
(A′
σ ∩ Rk−1) ⊗ σ if σ = 11
(A′
σ ∩ Sk−1) ⊗ σ if σ ̸= 11 (31)
