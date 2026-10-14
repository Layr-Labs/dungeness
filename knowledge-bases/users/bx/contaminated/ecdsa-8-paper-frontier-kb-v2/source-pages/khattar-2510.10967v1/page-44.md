---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 44
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 44

The text below is a page-delimited extraction of the unchanged source PDF.

44
Corollary E.1(Upper bound on|A ∩ Rk| and |A ∩ Sk| when dim A = 2k).
Let k be a positive integer andA = F2k
2 the 2k-dimensional affine subspace ofF2k
2 . Then
|A ∩ Rk| = 22k−1 + 2k−1, (E6)
|A ∩ Sk| = 22k−1 − 2k−1. (E7)
Proof. Immediate consequence of Lemma E.2.
Lemma E.3(Upper bound on|A ∩ Rk| and |A ∩ Sk| when dim A = 2k − 1).
Let k be a positive integer and letA ⊂ F2k
2 be a(2k − 1)-dimensional affine subspace ofF2k
2 . Then
|A ∩ Rk| ≤22k−2 + 2k−1 (E8)
|A ∩ Sk| ≤22k−2. (E9)
Proof. If k = 1, then |A| = 2 and |S1| = 1, so |A ∩ R1| ≤2 and |A ∩ S1| ≤1. Assume k >1. The affine space A
contains 22k−1 bit strings, but there are only22k−2 bit strings of each possible suffix. Therefore,F has at least two
elements. Thus, by Remark III.1 we have three cases to consider
dim F = 1 ∧ 11 /∈ F (E10)
dim F = 1 ∧ 11 ∈ F (E11)
dim F = 2. (E12)
We prove the first two cases directly and the third one by induction.
If dim F = 1, then Lemma III.1 implies thatdim W′ = 2k − 2 and therefore
A = F2k−2
2 ⊗ F. (E13)
If 11 /∈ F, then
A ∩ Rk = Rk−1 ⊗ F (E14)
A ∩ Sk = Sk−1 ⊗ F (E15)
and using Lemma E.2
|A ∩ Rk| = |F| · |Rk−1| = 2 · (22k−3 + 2k−2) = 22k−2 + 2k−1 (E16)
|A ∩ Sk| = |F| · |Sk−1| = 2 · (22k−3 − 2k−2) < 22k−2. (E17)
If F = {σ, 11} with σ ̸= 11, then
A ∩ Rk = (Rk−1 ⊗ σ) ⊔ (Sk−1 ⊗ 11) (E18)
A ∩ Sk = (Sk−1 ⊗ σ) ⊔ (Rk−1 ⊗ 11) (E19)
and usingRk−1 ⊔ Sk−1 = F2k−2
2 , we find
|A ∩ Rk| = |F2k−2
2 | < 22k−2 + 2k−1 (E20)
|A ∩ Sk| = |F2k−2
2 | = 22k−2. (E21)
We now prove the casedim F = 2 by induction. We established the base case at the opening of the proof. Assume
now that
|A ∩ Rk−1| ≤22k−4 + 2k−2 (E22)
|A ∩ Sk−1| ≤22k−4. (E23)
By Lemma III.1, the four affine subspacesA′
σ of F2k−2
2 with σ ∈ F in (30) and (31) arise as translations of the same
linear subspaceW′ of dimension2k − 3, so at most two of them are distinct
A′
1 := A′
11 = A′
ρ, A ′
2 := A′
σ = A′
τ . (E24)
