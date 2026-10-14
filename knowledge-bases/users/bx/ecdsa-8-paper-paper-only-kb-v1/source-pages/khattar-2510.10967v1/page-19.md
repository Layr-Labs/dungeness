---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 19
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 19

The text below is a page-delimited extraction of the unchanged source PDF.

19
where F = π1(A) is an affine subspace ofF2
2 and the setsA′
σ ⊂ π0(A) are affine subspaces ofF2k−2
2 that arise as
translations of the same linear subspaceW′ ⊂ F2k−2
2 with dim W′ = dim A − dim F.
Proof. We can writeA = a + V where a ∈ F2k
2 is a fixed bit string andV is ad-dimensional linear subspace ofF2k
2 .
Let B = {b1, . . . , bd} be an arbitrary basis ofV . Suppose b1, b2 ∈ Bare two distinct bit strings with suffix01. Then
b1 + b2 has suffix00, so{b1 + b2} ∪ B \ {b2} is another basis ofV with the number of elements with suffix01 reduced
by one. By iterating this procedure, we can reduce the number of elements with suffix01 to at most one.
Similarly, we can reduce the number of basis elements with suffixes10 and 11 to at most one. Moreover, if B
contains three elements with distinct nonzero suffixes, then we can replace one of them with an element with suffix
00 by adding the other two elements to it. Thus,V has a basisB that takes one of the following three forms
B =



B00
B00 ⊔ {b}
B00 ⊔ {b, c}
(32)
where B00 consists of bit strings with suffix00 and b, care two bit strings with distinct nonzero suffixes.
Define F := π1(A) as the set of suffixes of the elements ofA = a + V . The projectorπ1 is a linear map, soF is an
affine subspace ofF2
2 and therefore it has either one, two or four elements. Indeed,
B = B00 ⇐⇒ F = {σ} (33)
B = B00 ⊔ {b} ⇐⇒F = {σ, τ} (34)
B = B00 ⊔ {b, c} ⇐⇒F = {00, 01, 10, 11} (35)
where σ = π1(a) and τ = π1(a + b).
For every suffixσ ∈ F, let Aσ := A ∩ π−1
1 ({σ}) be the set of elements inA with suffix σ and A′
σ := π0(Aσ) the
set of roots of those elements ofA. A singleton set is an affine space, the intersection of affine subspaces is an affine
subspace, and π0, π1 are linear maps, soAσ and A′
σ are affine subspaces ofF2k
2 and F2k−2
2 , respectively. We can
express A in terms ofA′
σ for σ ∈ F as
A =
G
σ∈F
Aσ =
G
σ∈F
π0(Aσ) ⊗ σ =
G
σ∈F
A′
σ ⊗ σ. (36)
Define W := span(B00), so thatAσ = uσ + W where uσ ∈ F2k
2 is any bit string inA with suffixπ1(uσ) = σ. Then,
A′
σ = π0(uσ) + W′ where W′ := π0(W). But π0 is a bijection onW, sodim A′
σ = dim W′ = dim W = |B00|.
Finally, intersecting both sides of (36) withRk (respectively, Sk), we obtain
A ∩ Rk =
G
σ∈F
(
(A′
σ ∩ Sk−1) ⊗ σ if σ = 11
(A′
σ ∩ Rk−1) ⊗ σ if σ ̸= 11 (37)
A ∩ Sk =
G
σ∈F
(
(A′
σ ∩ Rk−1) ⊗ σ if σ = 11
(A′
σ ∩ Sk−1) ⊗ σ if σ ̸= 11 (38)
where we switch betweenRk and Sk when σ = 11 as needed in light of (29).
Remark III.1.The recursive structure formulas take five forms depending on0 ≤ dim F ≤ 2 and on whether11 ∈ F.
1. IfF = {σ} with σ ̸= 11, then
A ∩ Rk = (A′
σ ∩ Rk−1) ⊗ σ (39)
A ∩ Sk = (A′
σ ∩ Sk−1) ⊗ σ. (40)
2. IfF = {11}, then
A ∩ Rk = (A′
11 ∩ Sk−1) ⊗ 11 (41)
A ∩ Sk = (A′
11 ∩ Rk−1) ⊗ 11. (42)
3. IfF = {σ, τ} with 11 /∈ F and σ ̸= τ, then
A ∩ Rk = ((A′
σ ∩ Rk−1) ⊗ σ) ⊔ ((A′
τ ∩ Rk−1) ⊗ τ) (43)
A ∩ Sk = ((A′
σ ∩ Sk−1) ⊗ σ) ⊔ ((A′
τ ∩ Sk−1) ⊗ τ) . (44)
