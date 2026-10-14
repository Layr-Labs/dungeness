---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 47
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 47

The text below is a page-delimited extraction of the unchanged source PDF.

47
so thatB1 ⊔ B2 is an affine space of dimensiondim W + 1 and
|B1| = |W| (E74)
|B2 ∩ Sk| = |Wrss| + |Wsrs| + |Wssr| + |Wsss| (E75)
and hence
|A00 ∩ Sk| + |A01 ∩ Sk| + |A10 ∩ Sk| + |A11 ∩ Rk| = |B1| + 2 · |B2 ∩ Sk|. (E76)
Now, ifω(b, c) = 1, then
|A11 ∩ Rk| = |Wrrs| + |Wrsr| + |Wsrr| + |Wsss| (E77)
and adding (E67) yields
|A00 ∩ Sk| + |A01 ∩ Sk| + |A10 ∩ Sk| + |A11 ∩ Rk| (E78)
= 2 · |Wrrs| + 2 · |Wrsr| + 2 · |Wrss| + 2 · |Wsrr| + 2 · |Wsrs| + 2 · |Wssr| + 4 · |Wsss|.
Redefine
B1 := (a + Wxyy) ⊔ (a + b + Wxyy) (E79)
B2 := (a + Wxyy) ⊔ (a + b + Wxyy) (E80)
so thatB1 ⊔ B2 is again an affine space of dimensiondim W + 1 and
|B1| = 2 · |Wrrs| + 2 · |Wrsr| + 2 · |Wsrs| + 2 · |Wssr| (E81)
|B2 ∩ Sk| = |Wrss| + |Wsrr| + 2 · |Wsss| (E82)
and hence
|A00 ∩ Sk| + |A01 ∩ Sk| + |A10 ∩ Sk| + |A11 ∩ Rk| = |B1| + 2 · |B2 ∩ Sk| (E83)
completing the proof of the Lemma.
We note the following conditional upper bound which is implied by Lemma E.4 and which will facilitate its use in
an inductive proof.
Corollary E.2(Bound for mixed recursive structure formulas with four terms).
Let e and k > 1 be positive integers. If |B ∩ Sk−1| ≤2dim B−1 + 2k−3 for every affine subspaceB of F2k−2
2 with
dim B ∈ {e, e+ 1}, then
|A00 ∩ Sk−1| + |A01 ∩ Sk−1| + |A10 ∩ Sk−1| + |A11 ∩ Rk−1| ≤2e+1 + 2k−2 (E84)
for any four disjoint affine subspaces of the form
A00 = a + W (E85)
A01 = a + b + W (E86)
A10 = a + c + W (E87)
A11 = a + b + c + W (E88)
arising as translations of the samee-dimensional linear subspaceW ⊂ F2k−2
2 with a, b, c∈ F2k−2
2 .
Proof. By Lemma E.4, there exist two setsB1 and B2 each of which is either empty or affine and such that
|A00 ∩ Sk−1| + |A01 ∩ Sk−1| + |A10 ∩ Sk−1| + |A11 ∩ Rk−1| = |B1| + 2 · |B2 ∩ Sk−1| (E89)
and such that|B1| + |B2| = 2 · |W|. Thus, ifB1 = ∅, thenB2 is an affine subspace ofF2k−2
2 of dimensione + 1 and
using the assumption in the Corollary, we obtain
|A00 ∩ Sk−1| + |A01 ∩ Sk−1| + |A10 ∩ Sk−1| + |A11 ∩ Rk−1| ≤0 + 2· (2e + 2k−3) = 2e+1 + 2k−2. (E90)
If B2 = ∅, thenB1 is an affine subspace ofF2k−2
2 of dimensione + 1. Therefore,
|A00 ∩ Sk−1| + |A01 ∩ Sk−1| + |A10 ∩ Sk−1| + |A11 ∩ Rk−1| ≤2e+1 + 2 · 0 < 2e+1 + 2k−2. (E91)
Finally, if neitherB1 nor B2 is empty, then both are affine anddim B1 = dim B2 = e. Therefore,
|A00 ∩ Sk−1| + |A01 ∩ Sk−1| + |A10 ∩ Sk−1| + |A11 ∩ Rk−1| ≤2e + 2 · (2e−1 + 2k−3) = 2e+1 + 2k−2 (E92)
completing the proof of the Corollary.
