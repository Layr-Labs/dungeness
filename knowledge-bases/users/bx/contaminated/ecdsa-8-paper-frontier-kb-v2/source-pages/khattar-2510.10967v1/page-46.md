---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 46
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 46

The text below is a page-delimited extraction of the unchanged source PDF.

46
In either case,W can be partitioned into eight disjoint sets
Wrrr := {w ∈ W |(a + w ∈ Rk) ∧ (a + b + w ∈ Rk) ∧ (a + c + w ∈ Rk)} (E49)
Wrrs := {w ∈ W |(a + w ∈ Rk) ∧ (a + b + w ∈ Rk) ∧ (a + c + w ∈ Sk)} (E50)
Wrsr := {w ∈ W |(a + w ∈ Rk) ∧ (a + b + w ∈ Sk) ∧ (a + c + w ∈ Rk)} (E51)
Wrss := {w ∈ W |(a + w ∈ Rk) ∧ (a + b + w ∈ Sk) ∧ (a + c + w ∈ Sk)} (E52)
. . .
Wsss := {w ∈ W |(a + w ∈ Sk) ∧ (a + b + w ∈ Sk) ∧ (a + c + w ∈ Sk)} (E53)
so thatW = Wrrr ⊔ Wrrs ⊔ . . .⊔ Wsss. Consider the following disjoint unions of these sets
Wxxy := Wrrr ⊔ Wrrs ⊔ Wssr ⊔ Wsss (E54)
Wxxy := Wrsr ⊔ Wrss ⊔ Wsrr ⊔ Wsrs (E55)
Wxyy := Wrrr ⊔ Wrss ⊔ Wsrr ⊔ Wsss (E56)
Wxyy := Wrrs ⊔ Wrsr ⊔ Wsrs ⊔ Wssr. (E57)
The indicator function ofWxxy restricted toW is
1Wxxy (x) = 1Rk (a + x) · 1Sk (a + b + x) · 1Rk (a + c + x) + 1Rk (a + x) · 1Sk (a + b + x) · 1Sk (a + c + x) (E58)
+ 1Sk (a + x) · 1Rk (a + b + x) · 1Rk (a + c + x) + 1Sk (a + x) · 1Rk (a + b + x) · 1Sk (a + c + x) (E59)
= 1Rk (a + x) · 1Sk (a + b + x) + 1Sk (a + x) · 1Rk (a + b + x) (E60)
= (1 + 1Sk (a + x)) · 1Sk (a + b + x) + 1Sk (a + x) · (1 + 1Sk (a + b + x)) (E61)
= 1Sk (a + x) + 1Sk (a + b + x) (E62)
= 1Sk (b) + ω(a, b) + ω(b, x) (E63)
which is an affine functional onW. Therefore,Wxxy is empty or an affine subspace ofW. So isWxxy whose indicator
function restricted toW is 1Wxxy (x) = 1Wxxy (x) + 1. Moreover, (E54) and (E55) imply thatWxxy ⊔ Wxxy = W.
Similarly, the indicator function ofWxyy restricted toW is 1Wxyy (x) = 1Sk (b)+1Sk (c)+ω(a, b+c)+ω(b+c, x) which
is also an affine functional onW. Therefore, Wxyy is empty or an affine subspace ofW. So isWxyy whose indicator
function restricted toW is 1Wxyy (x) = 1Wxyy (x) + 1. Moreover, (E56) and (E57) imply thatWxyy ⊔ Wxyy = W.
We can write
|A00 ∩ Sk| = |Wsrr| + |Wsrs| + |Wssr| + |Wsss| (E64)
|A01 ∩ Sk| = |Wrsr| + |Wrss| + |Wssr| + |Wsss| (E65)
|A10 ∩ Sk| = |Wrrs| + |Wrss| + |Wsrs| + |Wsss| (E66)
irrespective ofω(b, c), so that
|A00 ∩ Sk| + |A01 ∩ Sk| + |A10 ∩ Sk| (E67)
= |Wrrs| + |Wrsr| + 2 · |Wrss| + |Wsrr| + 2 · |Wsrs| + 2 · |Wssr| + 3 · |Wsss|
also irrespective ofω(b, c). The analogous expression for|A11 ∩Rk| depends on the value ofω(b, c). We consider both
cases constructing a pair of suitable affine spacesB1 and B2 for each one in turn.
First, ifω(b, c) = 0, then
|A11 ∩ Rk| = |Wrrr| + |Wrss| + |Wsrs| + |Wssr| (E68)
and adding (E67) yields
|A00 ∩ Sk| + |A01 ∩ Sk| + |A10 ∩ Sk| + |A11 ∩ Rk| (E69)
= |Wrrr| + |Wrrs| + |Wrsr| + 3 · |Wrss| + |Wsrr| + 3 · |Wsrs| + 3 · |Wssr| + 3 · |Wsss| (E70)
= |W| + 2 · (|Wrss| + |Wsrs| + |Wssr| + |Wsss|) . (E71)
Define
B1 := (a + b + Wxxy) ⊔ (a + c + Wxxy) (E72)
B2 := (a + b + Wxxy) ⊔ (a + c + Wxxy) (E73)
