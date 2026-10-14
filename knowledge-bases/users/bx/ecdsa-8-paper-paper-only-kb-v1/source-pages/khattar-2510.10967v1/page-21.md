---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 21
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 21

The text below is a page-delimited extraction of the unchanged source PDF.

21
Lemma III.2(Proxy expression for mixed recursive structure formulas with two terms).
Let k be a positive integer anda1, a2 ∈ F2k
2 . For any two affine spacesA1 := a1 + W and A2 := a2 + W arising as
translations of the same linear subspaceW ⊂ F2k
2 , there exist two setsB1 and B2 each of which is either empty or
affine and such that
|A1 ∩ Rk| + |A2 ∩ Sk| = |B1| + 2 · |B2 ∩ Sk| (55)
and |B1| + |B2| = |W|.
Proof. We begin by partitioningW into four disjoint sets
Wrr := {x ∈ W |(a1 + x ∈ Rk) ∧ (a2 + x ∈ Rk)} (56)
Wrs := {x ∈ W |(a1 + x ∈ Rk) ∧ (a2 + x ∈ Sk)} (57)
Wsr := {x ∈ W |(a1 + x ∈ Sk) ∧ (a2 + x ∈ Rk)} (58)
Wss := {x ∈ W |(a1 + x ∈ Sk) ∧ (a2 + x ∈ Sk)} (59)
so thatW = Wrr ⊔ Wrs ⊔ Wsr ⊔ Wss. Consider the sets
W0 := Wrr ⊔ Wss W1 := Wrs ⊔ Wsr. (60)
The indicator function ofW1 restricted toW can be written as
1W1 (x) = 1Rk (a1 + x) · 1Sk (a2 + x) + 1Sk (a1 + x) · 1Rk (a2 + x) (61)
= (1 + 1Sk (a1 + x)) · 1Sk (a2 + x) + 1Sk (a1 + x) · (1 + 1Sk (a2 + x)) (62)
= 1Sk (a1 + x) + 1Sk (a2 + x) (63)
= ω(a1 + a2, x) + 1Sk (a1) + 1Sk (a2) (64)
where we dropped the terms1Sk (a1 + x) · 1Sk (a2 + x) and 1Sk (x), becauseF2 has characteristic2. But ω is bilinear,
so 1W1 restricted to W is an affine functional onW. Therefore, W1 is either empty or an affine subspace ofW.
Similarly, the indicator function ofW0 restricted toW is 1W0 (x) = 1W1 (x) + 1and hence also an affine functional on
W. Therefore, W0 is either empty or an affine subspace ofW. Moreover, W = W0 ⊔ W1, so if bothW0 and W1 are
non-empty, thendim W0 = dim W1 = dim W − 1. Translation is bijective, so definitions (56)-(59) imply that
|A1 ∩ Rk| + |A2 ∩ Sk| = |Wrr| + 2 · |Wrs| + |Wss|. (65)
Finally, defineB1 := a1 + W0 and B2 := a2 + W1, so that|B1| + |B2| = |W0| + |W1| = |W| and rewrite (65) as
|A1 ∩ Rk| + |A2 ∩ Sk| = |B1| + 2 · |B2 ∩ Sk| (66)
where we used|B1| = |Wrr| + |Wss| and |Wrs| = |B2 ∩ Sk|.
In order to facilitate the use of Lemma III.2 in an inductive proof, we note the following conditional upper bound
it implies.
Corollary III.1(Bound for mixed recursive structure formulas with two terms).
Let e and k > 1 be positive integers. If |B ∩ Sk−1| ≤2dim B−1 + 2k−3 for every affine subspaceB of F2k−2
2 with
dim B ∈ {e − 1, e}, then
|A1 ∩ Rk−1| + |A2 ∩ Sk−1| ≤2e + 2k−2 (67)
for every pair ofe-dimensional affine subspacesA1 := a1 + W and A2 := a2 + W of F2k−2
2 that arise as translations
of the same linear subspaceW of F2k−2
2 .
Proof. By Lemma III.2, there exist two setsB1 and B2, each of which is either empty or affine and such that
|A1 ∩ Rk−1| + |A2 ∩ Sk−1| = |B1| + 2 · |B2 ∩ Sk−1| (68)
and |B1| + |B2| = |W|. If B1 = ∅, thenB2 is an affine subspace ofF2k−2
2 of dimensione. Therefore,
|A1 ∩ Rk−1| + |A2 ∩ Sk−1| ≤0 + 2· (2e−1 + 2k−3) = 2e + 2k−2. (69)
