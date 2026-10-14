---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 45
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 45

The text below is a page-delimited extraction of the unchanged source PDF.

and the matrixH= (H j,s) with entries
H=


u1 4
5 u0 + 1
5 u1 u0 u0
u1 u0 u2 u0
u3 u0 u0 u0
u0 u0 u2 u0


.
It is trivial to verify that
Gj,s ⪰C Hj,s andH j,sv≥F(v),for allj, s∈ {0, ...,3}.
Consequently,
F(M(2 d)v) =λ d+1 min
0≤j≤3
Gj,dv≥λ d+1F(v),for 0≤d≤3.
SinceFis coordinatewise nondecreasing,F(M(q)v)≥F(M(2 d−1)v)≥λ dF(v).Thus we prove (13)
for 1≤d≤4.
It remains to considerd≥5. Writev= (a, b) T , a≥b≥0.A direct check of the four defining rows
givesF((1,0) T ) =u 3(1,0) T , F((1,1)T ) =u 2(1,1) T =λF((1,0) T ).By monotonicity and homogeneity,
F(M(q)v) =F

qa+b
a
!
≥F

qa
0
!
=qaF

1
0
!
= qa
λ F

1
1
!
= q
λF

a
a
!
≥ q
λF(v).(15)
Ford= 5, 2 4 = 16> λ6 = (2 +
√
3)2 = 7 + 4
√
3,and the inequality propagates to all largerd, since
2> λ. Henceq/λ≥2 d−1/λ≥λ d. Together with (15) this proves (13) for everyd≥5.
We next prove (14). Sinceq≥2 d−1, it suffices by monotonicity to considerq= 2 d−1:
•Ford= 2, the claim is immediate.
•Ford= 3, direct substitution givesF((4,1) T )≥λF((2,1) T ).
•Ford≥4, the same four-row calculation gives 8F(1,0) T ≥λ 2F(2,1) T .Therefore,
F

2d−1
1
!
≥2 d−1F

1
0
!
= 2d−4

8F

1
0
!!
≥2 d−4λ2F

2
1
!
≥λ d−2F

2
1
!
,
where the last inequality uses 2> λ.
This completes the proof.
A.2 Step-dependent active windows
Fix an inputx, let (q1, . . . , qk−1) denote the quotient sequence produced by EEA, and definebi :=⌊log 2 qi⌋
for each iterationi. Under the four-phase schedule, each EEA iterationiis expanded into 4(b i + 1) steps.
The total number of steps isN= 4 Pk−1
i=1 (bi + 1)≤N max := 4⌈cn⌉, whereλ:= (2 +
√
3)1/3 and
c:= 1/log 2 λ= 3/log 2(2 +
√
3) (see Appendix A.1).
45
