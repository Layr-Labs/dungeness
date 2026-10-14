---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 20
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 20

The text below is a page-delimited extraction of the unchanged source PDF.

20
4. IfF = {σ, 11} with σ ̸= 11, then
A ∩ Rk = ((A′
σ ∩ Rk−1) ⊗ σ) ⊔ ((A′
11 ∩ Sk−1) ⊗ 11) (45)
A ∩ Sk = ((A′
σ ∩ Sk−1) ⊗ σ) ⊔ ((A′
11 ∩ Rk−1) ⊗ 11) . (46)
5. IfF = {00, 01, 10, 11}, then
A ∩ Rk = ((A′
11 ∩ Sk−1) ⊗ 11) ⊔
G
σ∈{00,01,10}
(A′
σ ∩ Rk−1) ⊗ σ (47)
A ∩ Sk = ((A′
11 ∩ Rk−1) ⊗ 11) ⊔
G
σ∈{00,01,10}
(A′
σ ∩ Sk−1) ⊗ σ. (48)
Lemma III.1 enables inductive proof of the upper bound on|A ∩ Rk| and |A ∩ Sk| for affine spaces with dimension
dim A = 2k−1, which we defer to Lemma E.3. Below, we prove that|A∩Rk| ≤2d−1 +2k−1 and |A∩Sk| ≤2d−1 +2k−2
for affineA with k ≤ dim A <2k − 1 which requires more sophisticated tools in addition to Lemma III.1. The right-
hand sides2d−1 + 2k−1 and 2d−1 + 2k−2 indicate that the cardinality ofA ∩Sk (respectively,A ∩Rk) can exceed1
2 |A|
by at most2k−2 (respectively, 2k−1). Thus, |A ∩ Rk| can exceed 1
2 |A| by twice as much as|A ∩ Sk|, so if a recursive
structure formula forA ∩Sk contains both anA ∩Rk−1 term and anA ∩Sk−1 term, then a naive inductive argument
fails. We refer to such formulas asmixed recursive structure formulas. They have either two or four terms
A ∩ Sk = ((A′
σ ∩ Sk−1) ⊗ 00) ⊔ ((A′
11 ∩ Rk−1) ⊗ 11) (49)
A ∩ Sk = ((A′
00 ∩ Sk−1) ⊗ 00) ⊔ ((A′
01 ∩ Sk−1) ⊗ 01) ⊔ ((A′
10 ∩ Sk−1) ⊗ 10) ⊔ ((A′
11 ∩ Rk−1) ⊗ 11) . (50)
These recursive structure formulas do not cause issues in the proof of Lemma E.3 where we work around the
challenge by exploiting the fact that whendim A = 2k − 1 not all affine subspaces on the right hand side are distinct.
To face a more general situation below, we will exploit hidden affine structures in certain combinations of sets of the
form A ∩ Sk−1 and A ∩ Rk−1 that arise from the cancellation of quadratic terms in the indicator functions of these
sets as they are combined together.
Let W be a linear subspace ofF2k
2 . If a functionf from W to the underlying field of scalarsF2 is linear, then we will
refer tof as alinear functional. Let a ∈ F2k
2 and letA := a + W be an affine subspace ofF2k
2 . If a functiong from A
to the underlying field of scalarsF2 can be written asg(a + w) = c + f(w) for somec ∈ F2 and some linear functional
f, then we will refer tog as anaffine functional. The significance of affine functionals to our arguments derives from
the way they partition their domain. Ifg is a non-constant affine functional, thenf is a non-constant linear functional
and f−1(1) is a coset ofkerf = f−1(0). Therefore, |f−1(0)| = |f−1(1)|. But then also|g−1(0)| = |g−1(1)|. Thus, if
g : A → F2 is an affine functional, then eachg−1(0) and g−1(1) is either empty or affine. Moreover, if bothg−1(0)
and g−1(1) are non-empty, thendim g−1(0) = dim g−1(1) = dim A − 1.
In order to express the value of the indicator function1Sk : F2k
2 → F2 of Sk
1Sk (x) :=
kX
i=1
xixk+i = ⟨πL(x), πR(x)⟩ (51)
on bit strings in an affine spaceA := a + W, we introduce the (skew-)symmetric bilinear formω : F2k
2 → F2
ω(x, y) :=
kX
i=1
(xiyk+i + xk+iyi) = ⟨πL(x), πR(y)⟩ + ⟨πL(y), πR(x)⟩ (52)
where πL, πR : F2k
2 → Fk
2 are linear projectors defined via
πL(ab) = a, π R(ab) = b (53)
for anya, b∈ Fk
2. Indeed, we can express1Sk (a + x) for anyx ∈ W in terms ofω as
1Sk (a + x) = ⟨aL + xL, aR + xR⟩ = 1Sk (a) + ω(a, x) + 1Sk (x) (54)
where aL := πL(a), aR := πR(a), xL := πL(x), andxR := πR(x). This way of writing1Sk allows us to construct affine
subspaces from sets of the formA ∩ Rk and A ∩ Sk by arranging for the cancellation of the quadratic terms1Sk (x).
We can use these objects and their properties to prove Lemma III.2 and E.4 that enable us to express the right
hand side of (49) and (50) in terms of cardinalities of sets involvingSk−1, but noRk−1.
