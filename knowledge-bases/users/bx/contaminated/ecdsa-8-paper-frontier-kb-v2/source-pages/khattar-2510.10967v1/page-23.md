---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 23
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 23

The text below is a page-delimited extraction of the unchanged source PDF.

23
where the affine subspaceA′
11 again has dimensiondim A′
11 = d −dim F = d. Using the inductive hypothesis, we find
|A ∩ Rk| = |A′
11 ∩ Sk−1| ≤2d−1 + 2k−3 < 2d−1 + 2k−1 (89)
|A ∩ Sk| = |A′
11 ∩ Rk−1| ≤2d−1 + 2k−2 = 2d−1 + 2k−2. (90)
In the third case, whereF = {σ, τ} with σ ̸= 11, τ ̸= 11 and σ ̸= τ, the recursive structure formulas read
A ∩ Rk = ((A′
σ ∩ Rk−1) ⊗ σ) ⊔ ((A′
τ ∩ Rk−1) ⊗ τ) (91)
A ∩ Sk = ((A′
σ ∩ Sk−1) ⊗ σ) ⊔ ((A′
τ ∩ Sk−1) ⊗ τ). (92)
Using the inductive hypothesis anddim A′
σ = dim A′
τ = d − dim F = d − 1, we find
|A ∩ Rk| ≤2 · (2d−2 + 2k−2) = 2d−1 + 2k−1 (93)
|A ∩ Sk| ≤2 · (2d−2 + 2k−3) = 2d−1 + 2k−2. (94)
In the fourth case, whereF = {σ, 11} with σ ̸= 11, the recursive structure formulas (30) and (31) become
A ∩ Rk = ((A′
11 ∩ Sk−1) ⊗ 11) ⊔ ((A′
σ ∩ Rk−1) ⊗ σ) (95)
A ∩ Sk = ((A′
11 ∩ Rk−1) ⊗ 11) ⊔ ((A′
σ ∩ Sk−1) ⊗ σ) (96)
where dim A′
σ = dim A′
11 = d − dim F = d − 1. Consequently,
|A ∩ Rk| = |A′
11 ∩ Sk−1| + |A′
σ ∩ Rk−1| (97)
|A ∩ Sk| = |A′
11 ∩ Rk−1| + |A′
σ ∩ Sk−1|. (98)
We obtain the upper bound on|A ∩ Rk| from the inductive hypothesis
|A ∩ Rk| ≤2d−2 + 2k−3 + 2d−2 + 2k−2 < 2d−1 + 2k−1 (99)
and the upper bound on|A ∩ Sk| using Corollary III.1 withe = d − 1
|A ∩ Sk| = |A′
11 ∩ Rk−1| + |A′
σ ∩ Sk−1| ≤2d−1 + 2k−2 (100)
where the Corollary’s assumption follows from the inductive hypothesis and Lemma E.1.
Finally, in the fifth case, whereF = {00, 01, 10, 11}, the recursive structure formulas (30) and (31) become
A ∩ Rk = ((A′
00 ∩ Rk−1) ⊗ 00) ⊔ ((A′
01 ∩ Rk−1) ⊗ 01) ⊔ ((A′
10 ∩ Rk−1) ⊗ 10) ⊔ ((A′
11 ∩ Sk−1) ⊗ 11) (101)
A ∩ Sk = ((A′
00 ∩ Sk−1) ⊗ 00) ⊔ ((A′
01 ∩ Sk−1) ⊗ 01) ⊔ ((A′
10 ∩ Sk−1) ⊗ 10) ⊔ ((A′
11 ∩ Rk−1) ⊗ 11) . (102)
There are two possibilities. Either all four affine subspacesA′
σ of F2k−2
2 are distinct or they are not.
Suppose first that the affine subspacesA′
σ are not all distinct, so that there areA′
1 and A′
2 such that
A′
1 := A′
11 = A′
ρ, A ′
2 := A′
σ = A′
τ . (103)
In this case, we use the fact thatRk−1 ⊔ Sk−1 = F2k−2
2 to write
|A ∩ Rk| = |A′
1| + 2 · |A′
2 ∩ Rk−1| (104)
|A ∩ Sk| = |A′
1| + 2 · |A′
2 ∩ Sk−1| (105)
which, using our inductive hypothesis anddim A′
σ = d − dim F = d − 2 for allσ ∈ F2
2, implies
|A ∩ Rk| ≤2d−2 + 2 · (2d−3 + 2k−2) = 2d−1 + 2k−1 (106)
|A ∩ Sk| ≤2d−2 + 2 · (2d−3 + 2k−3) = 2d−1 + 2k−2. (107)
Suppose now that the four affine subspacesA′
σ of F2k−2
2 are all distinct. By Lemma III.1, the subspaces arise as
translations of the same linear subspaceW′ ⊂ F2k−2
2 of dimensiondim W′ = d − dim F = d − 2.
By combiningA′
00 and A′
01 into (d − 1)-dimensional affine spaceA′
00,01, we can rewrite (101) as
A ∩ Rk =

(A′
00,01 ∩ Rk−1) ⊗ 00

⊔ ((A′
10 ∩ Rk−1) ⊗ 10) ⊔ ((A′
11 ∩ Sk−1) ⊗ 11) (108)
