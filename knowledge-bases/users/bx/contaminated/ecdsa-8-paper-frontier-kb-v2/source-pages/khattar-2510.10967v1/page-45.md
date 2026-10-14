---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 45
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 45

The text below is a page-delimited extraction of the unchanged source PDF.

45
The equationRk−1 ⊔ Sk−1 = F2k−2
2 implies then that
|A ∩ Rk| = |A′
1| + 2 · |A′
2 ∩ Rk−1| (E25)
|A ∩ Sk| = |A′
1| + 2 · |A′
2 ∩ Sk−1| (E26)
and using our inductive hypothesis, we obtain
|A ∩ Rk| ≤22k−3 + 2 · (22k−4 + 2k−2) = 22k−2 + 2k−1 (E27)
|A ∩ Sk| ≤22k−3 + 2 · 22k−4 = 22k−2 (E28)
completing the proof of the Lemma.
Lemma E.4(Proxy expression for mixed recursive structure formulas with four terms).
Let k be a positive integer anda, b, c∈ F2k
2 . For any four disjoint affine subspaces of the form
A00 = a + W (E29)
A01 = a + b + W (E30)
A10 = a + c + W (E31)
A11 = a + b + c + W (E32)
arising as translations of the same linear subspaceW ⊂ F2k
2 , there exist two disjoint setsB1 and B2 each of which is
either empty or affine and such that
|A00 ∩ Sk| + |A01 ∩ Sk| + |A10 ∩ Sk| + |A11 ∩ Rk| = |B1| + 2 · |B2 ∩ Sk| (E33)
and |B1| + |B2| = 2 · |W|.
Proof. First note that for anyx ∈ W
1Sk (a + x) = 1Sk (a) + ω(a, x) + 1Sk (x) (E34)
1Sk (a + b + x) = 1Sk (a) + 1Sk (b) + ω(a, b) + ω(a, x) + ω(b, x) + 1Sk (x) (E35)
1Sk (a + c + x) = 1Sk (a) + 1Sk (c) + ω(a, c) + ω(a, x) + ω(c, x) + 1Sk (x) (E36)
1Sk (a + b + c + x) = 1Sk (a) + 1Sk (b) + 1Sk (c) + ω(a, b) + ω(b, c) + ω(c, a)
+ ω(a, x) + ω(b, x) + ω(c, x) + 1Sk (x) (E37)
which means that
1Sk (a + x) + 1Sk (a + b + x) + 1Sk (a + c + x) + 1Sk (a + b + c + x) = ω(b, c). (E38)
Thus, for any fixeda, b, c∈ F2k
2 , we can infer1Sk (a + b + c + x) from 1Sk (a + x), 1Sk (a + b + x), and1Sk (a + c + x).
Indeed, ifω(b, c) = 0, then for everyx ∈ W we have the following eight equivalences
(a + x ∈ Rk) ∧ (a + b + x ∈ Rk) ∧ (a + c + x ∈ Rk) ⇐⇒ a + b + c + x ∈ Rk (E39)
(a + x ∈ Rk) ∧ (a + b + x ∈ Rk) ∧ (a + c + x ∈ Sk) ⇐⇒ a + b + c + x ∈ Sk (E40)
(a + x ∈ Rk) ∧ (a + b + x ∈ Sk) ∧ (a + c + x ∈ Rk) ⇐⇒ a + b + c + x ∈ Sk (E41)
(a + x ∈ Rk) ∧ (a + b + x ∈ Sk) ∧ (a + c + x ∈ Sk) ⇐⇒ a + b + c + x ∈ Rk (E42)
. . .
(a + x ∈ Sk) ∧ (a + b + x ∈ Sk) ∧ (a + c + x ∈ Sk) ⇐⇒ a + b + c + x ∈ Sk. (E43)
If on the other handω(b, c) = 1, then for everyx ∈ W we have the eight equivalences
(a + x ∈ Rk) ∧ (a + b + x ∈ Rk) ∧ (a + c + x ∈ Rk) ⇐⇒ a + b + c + x ∈ Sk (E44)
(a + x ∈ Rk) ∧ (a + b + x ∈ Rk) ∧ (a + c + x ∈ Sk) ⇐⇒ a + b + c + x ∈ Rk (E45)
(a + x ∈ Rk) ∧ (a + b + x ∈ Sk) ∧ (a + c + x ∈ Rk) ⇐⇒ a + b + c + x ∈ Rk (E46)
(a + x ∈ Rk) ∧ (a + b + x ∈ Sk) ∧ (a + c + x ∈ Sk) ⇐⇒ a + b + c + x ∈ Sk (E47)
. . .
(a + x ∈ Sk) ∧ (a + b + x ∈ Sk) ∧ (a + c + x ∈ Sk) ⇐⇒ a + b + c + x ∈ Rk. (E48)
