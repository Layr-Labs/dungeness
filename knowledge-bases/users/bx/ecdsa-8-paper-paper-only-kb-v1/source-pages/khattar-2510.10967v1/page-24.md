---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 24
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 24

The text below is a page-delimited extraction of the unchanged source PDF.

24
which leads to
|A ∩ Rk| = |A′
00,01 ∩ Rk−1| + |A′
10 ∩ Rk−1| + |A′
11 ∩ Sk−1|. (109)
If d = k, then|A ∩Rk| ≤2d−1 + 2k−1 = 2d. For affine spaces withd > k, we prove the upper bound on|A ∩Rk| using
Corollary III.1 withe = d − 2
|A ∩ Rk| ≤2d−2 + 2k−2 + 2d−2 + 2k−2 = 2d−1 + 2k−1 (110)
where the Corollary’s assumption follows from the inductive hypothesis and Lemma E.1. The upper bound on|A∩Sk|
follows from Corollary E.2 withe = d − 2
|A ∩ Sk| = |A′
00 ∩ Sk−1| + |A′
01 ∩ Sk−1| + |A′
10 ∩ Sk−1| + |A′
11 ∩ Rk−1| ≤2d−1 + 2k−2 (111)
where the Corollary’s assumption follows from the inductive hypothesis and Lemma E.1.
Theorem III.4. For any positive integerk and any affine subspaceA ⊂ F2k
2 of dimensiond = dim A, we have
|A ∩ Sk| ≤



2d d < k
2d−1 + 2k−2 k ≤ d <2k − 1
22k−2 d = 2k − 1
22k−1 − 2k−1 d = 2k
(112)
where
Sk :=
(
(x1, ..., x2k) ∈ F2k
2 :
kX
i=1
xixi+k = 1 mod 2
)
. (113)
Proof. The four upper bounds in (112) follow from Lemma E.1, Lemma III.3, Lemma E.3, and Corollary E.1, respec-
tively.
C. Asymptotic Classical Hardness of Twisted Bent Target OPI
Definition III.5. Let R, µ∈ (0, 1) be constants. For each positive integerk, we define the Twisted Bent Target OPI
(TBT-OPI) problem as follows. letSk be the set of eq (113). For each of them = 22k −1 evaluation pointsα ∈ F∗
22k ,
let A ∼ GL2k(F2) be a random independent invertible matrix and set
Fα = ϕ−1(Aϕ(x)), (114)
where ϕ is the bijection of eq (20). The(R, µ)-TBT-OPI problem is to find a polynomialf(X) of degree at most
⌈R · m⌉ such thatf(α) ∈ Fα for at least⌊µ · m⌋ distinct α.
Lemma III.6. The TBT-OPI setsFα are efficiently constructible per requirement (2) of IV.2.
Proof. Note that ifA = I, then applying a phase toSk can be achieved with a single layer of transversal CZ gates.
We can then change the basis to account forA by conjugating this with a circuit ofO(k2) = eO(1) CNOT gates.
Theorem III.7. There exists a choice of constantR ≈ 1/10 so that, lettingµ = µDQI := 1
2 +
q
R
2

1 − R
2

, the
number of trials of XP required to solve(R, µ)-TBT-OPI (definition III.5) is at leastexp(0.02m).
Proof. The number of trials that XP needs to beat DQI is1
γ where γ is the objective function of (A2). This objective
function is upper bounded through a direct application the Hoeffding inequality [41] by (115):
P
 mX
i=1
Xi ≥ t
!
≤ exp

−2(t − E[Pm
i=1 Xi])2
m

(115)
