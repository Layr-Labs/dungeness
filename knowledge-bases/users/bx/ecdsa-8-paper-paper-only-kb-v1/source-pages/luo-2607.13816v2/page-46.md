---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 46
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 46

The text below is a page-delimited extraction of the unchanged source PDF.

For a global step indexT∈ {1,2, . . . , Nmax}, letj=j(x, T) denote the index of the EEA iteration
containing stepT, and letu=u(x, T) denote the position ofTwithin that iteration. More precisely, the
pair (j(x, T), u(x, T)) is uniquely determined by the conditions
j−1X
i=1
4(bi + 1)< T≤
jX
i=1
4(bi + 1), u=T−
j−1X
i=1
4(bi + 1).
The bit-length of the current quotientℓ q(x, T) depends deterministically on indices (j, u):
ℓq(x, T) =



0u(x, T)∈(0, b j + 1]∪(3(b j + 1),4(bj + 1)],
u(x, T)−(bj + 1)u(x, T)∈(b j + 1,2(bj + 1)],
3(bj + 1)−u u(x, T)∈(2(b j + 1),3(bj + 1)].
(16)
We next state a lemma that characterizes the minimal possible value oft j, conditioned on the total
number of stepsN j taken before reaching thej-th iteration of EEA. LetFbe the function constructed
in Appendix A.1, and define
η:= F

(2,1) T 
λ2F((1,1) T ) = 4
√
3−3
13 λ2, δ:=−log λ η= 0.726208. . . .
Lemma A.2.Suppose thatN j = Pj−1
i=1 4(bi + 1)is fixed. Then, over all possible EEA iteration indices
jand all admissible quotient sequences(q 1, . . . , qj−1), we havet j ≥ηλ Nj/4 =λ Nj/4−δ.Consequently,
⌊log2 tj⌋+ 1> Nj/4−δ
c = Nj −4δ
4c ,⌊log 2 tj⌋+ 1≥
Nj −4δ
4c

.
Proof.By Algorithm 1, the EEA inputxis chosen to be smaller thanp/2, and henceq 1 ≥2. Setd i :=
bi + 1. The Lemma A.1 established in Appendix A.1 giveF(M(q)v)≥λ ⌊log2 q⌋+1F(v) andF

(q,1) T 
≥
λd−2F

(2,1) T 
, wheneverq≥2 has bit-lengthd. Given the EEA iteration rulet i+1 =t i−1 +q iti, we can
write that (ti+1, ti)T =M(q i)(ti, ti−1)t.Therefore, forj≥2,
F

(tj, tj−1)T 
=F

M(qj−1)···M(q 2)
q1
1

≥λ Nj/4−d1 F

(q1,1) T 
≥λ Nj/4−2F

(2,1) T 
.
Since 0≤t j−1 ≤t j andFis coordinatewise nondecreasing and positively homogeneous,
F

(tj, tj−1)T 
≤F

(tj, tj)T 
=t jF

(1,1) T 
.
Combining the two inequalities givest j ≥ηλ Nj/4. The casej= 1 follows fromt 1 = 1≥η.
We then provide the detailed proofs of the bounds stated in Section 4.2 in the remainder of this
subsection.
46
