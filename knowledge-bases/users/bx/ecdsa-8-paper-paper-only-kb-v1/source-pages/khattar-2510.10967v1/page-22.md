---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 22
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 22

The text below is a page-delimited extraction of the unchanged source PDF.

22
If B2 = ∅, thenB1 is an affine subspace ofF2k−2
2 of dimensione. Therefore,
|A1 ∩ Rk−1| + |A2 ∩ Sk−1| ≤2e + 2 · 0 < 2e + 2k−2. (70)
Finally, if neitherB1 nor B2 is empty, then both are affine anddim B1 = dim B2 = e − 1. Therefore,
|A1 ∩ Rk−1| + |A2 ∩ Sk−1| ≤2e−1 + 2 · (2e−2 + 2k−3) = 2e + 2k−2 (71)
completing the proof of the Corollary.
A similar, although technically more complicated, proof establishes an analogous result for mixed recursive formulas
with four terms, see Lemma E.4 and Corollary E.2. Equipped with Corollary III.1 above for dealing with two-term
mixed recursive structure formulas and Corollary E.2 for dealing with four-term mixed recursive structure formulas,
we are now ready to prove the upper bounds on|A ∩ Rk| and |A ∩ Sk| for affine spaces withk ≤ dim A <2k − 1.
Lemma III.3(Upper bound on|A ∩ Rk| and |A ∩ Sk| when k ≤ dim A <2k − 1).
Let k, dbe two positive integers and letA ⊂ F2k
2 be ad-dimensional affine subspace ofF2k
2 . If k ≤ d <2k − 1, then
|A ∩ Rk| ≤2d−1 + 2k−1 (72)
|A ∩ Sk| ≤2d−1 + 2k−2. (73)
Proof. Weprovetheboundsbyinductionon k. Ifk = 1, thentherearenoaffinesubspacesofdimension 1 ≤ dim A <1,
so the upper bounds are vacuously satisfied. Fixk >1 and suppose that for any affine subspaceB ⊂ F2k−2
2 whose
dimension e := dim B satisfies k − 1 ≤ e <2k − 3, it is the case that
|B ∩ Rk−1| ≤2e−1 + 2k−2 (74)
|B ∩ Sk−1| ≤2e−1 + 2k−3. (75)
We will also use (74) and (75) whene = 2k − 3 and e = 2k − 2 which follow from Lemma E.3 and Corollary E.1,
respectively. We will show that for every affine subspaceA ⊂ F2k
2 of dimensiond = dim A with k ≤ d <2k − 1, we
have
|A ∩ Rk| ≤2d−1 + 2k−1 (76)
|A ∩ Sk| ≤2d−1 + 2k−2. (77)
By Remark III.1, we have five cases to consider
dim F = 0 ∧ 11 /∈ F (78)
dim F = 0 ∧ 11 ∈ F (79)
dim F = 1 ∧ 11 /∈ F (80)
dim F = 1 ∧ 11 ∈ F (81)
dim F = 2. (82)
In the first case, whereF = {σ} with σ ̸= 11, the recursive structure formulas (30) and (31) become
A ∩ Rk = (A′
σ ∩ Rk−1) ⊗ σ (83)
A ∩ Sk = (A′
σ ∩ Sk−1) ⊗ σ (84)
where the affine subspaceA′
σ has dimensiondim A′
σ = d − dim F = d. Using the inductive hypothesis, we obtain
|A ∩ Rk| = |A′
σ ∩ Rk−1| ≤2d−1 + 2k−2 < 2d−1 + 2k−1 (85)
|A ∩ Sk| = |A′
σ ∩ Sk−1| ≤2d−1 + 2k−3 < 2d−1 + 2k−2. (86)
In the second case, whereF = {11}, the recursive structure formulas (30) and (31) become
A ∩ Rk = (A′
11 ∩ Sk−1) ⊗ σ (87)
A ∩ Sk = (A′
11 ∩ Rk−1) ⊗ σ (88)
