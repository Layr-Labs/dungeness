---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 43
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 43

The text below is a page-delimited extraction of the unchanged source PDF.

43
2. Worst-Case Analysis: Half PEEA (Reed-Solomon Decoding)
The Half-PEEA stops whenDk > n/2.
Theorem D.6(Cycle Bound for Half PEEA). The maximum number of cycles required for the optimized synchro-
nized Half-PEEA isTmax = 6⌊n/2⌋ + 5.
Proof. We maximize the cost functionT = 3Dk + Sk −dk + 2k. The maximum degree reduction required isDk,max =
⌊n/2⌋ + 1.
To maximizeT, we seek the slowest convergence scenario. This occurs whendi = 1 and si = 1 for all i. In this
scenario:
• Dk = Dk,max.
• k = Dk,max (since di = 1).
• Sk = Dk,max (since si = 1).
• dk = 1.
Substituting these into the cost function:
Tmax = 3Dk,max + Dk,max − 1 + 2Dk,max
= 6Dk,max − 1
= 6(⌊n/2⌋ + 1) − 1
= 6⌊n/2⌋ + 5.
Appendix E: Deferred proofs of upper bounds on affine intersections of Maiorana-McFarland target sets
Here, we state and prove a few lemmas that are omitted from Section IIIB4. Together the proofs here and in
Section IIIB4 establish the upper bounds on|A ∩ Sk| given in (24).
Lemma E.1(Upper bound on|A ∩ Rk| and |A ∩ Sk| when dim A < k).
Let k be a positive integer,d a non-negative integer andA a d-dimensional affine subspace ofF2k
2 . Then
|A ∩ Rk| ≤2d, |A ∩ Sk| ≤2d. (E1)
Proof. |A ∩ Rk| ≤ |A| = 2d and |A ∩ Sk| ≤ |A| = 2d.
Lemma E.2(Size ofRk and Sk).
|Rk| = 22k−1 + 2k−1, (E2)
|Sk| = 22k−1 − 2k−1. (E3)
Proof. We can write
Rk =
G
x∈Fk
2
{x} × {x}⊥ (E4)
where {x}⊥ ⊂ Fk
2 is the set ofk-bit strings orthogonal tox ∈ Fk
2 under the standard dot product⟨., .⟩. But
|{x}⊥| =
(
2k if x = 0 ∈ Fk
2
2k−1 otherwise (E5)
so |Rk| = 22k−1 + 2k−1 and |Sk| = 22k−1 − 2k−1.
