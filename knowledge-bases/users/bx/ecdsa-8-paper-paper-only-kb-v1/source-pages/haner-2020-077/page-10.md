---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 10
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 10

The text below is a page-delimited extraction of the unchanged source PDF.

|x1⟩
|y1⟩
|ctrl⟩
|t0 = 0⟩
|λ⟩
n
n
n
n
inv
inv
mul
mul
mul
inv
inv
(a) Inversion steps in elliptic curve
point addition from [ 27]. Auxiliary
qubits are not shown. Each inv
block represents invA, copying out,
then inv−1
A (with the same pattern
for mul). Thus, this circuit contains
4 invA steps and 2 mulA steps.
|x1⟩
|y1⟩
|ctrl⟩
|λ= 0⟩
n
n
n
0
0
0
0
0
invA
invA
0
0
0
0
0
mulA
mulA
mul−1
A
mul−1
A
0
0
0
0
0
·22n−k
inv−1
A
inv−1
A
0
0
0
0
0
(b) More eﬃcient modular division. 0⊢depicts initializing an aux-
iliary qubit to zero, and ⊣0 depicts removing an auxiliary qubit
known to be zero. The doubling of the output λ in the last step
corrects the pseudo-inverse output.
Fig. 8: Improvement to the modular division circuit from [ 27] by clearing and re-using auxiliary
qubits before the full uncomputation.
5 Elliptic curves
Elliptic curve arithmetic has been heavily optimized for classical computers, but because Shor’s
algorithm requires unique representations of points and in-place point addition, few of these
optimizations apply. We ﬁnd aﬃne Weierstrass coordinates to be the most eﬃcient method;
Appendix A.4 explains this choice in more detail.
Aﬃne Weierstrass coordinates are one of the conceptually simplest methods, and RNSL use
them for their circuit. We assume the elliptic curve equation has the form E : y2 = x3 + ax+ b
with a,b ∈Fp and we represent points by pairs (x,y) that satisfy this equation. Combining RNSL’s
circuit with the optimizations from this paper, we obtain the circuit in Figure 9. The total cost is
2 divisions, 2 multiplications, 1 squaring, and 9 additions.
The simple formulas with aﬃne coordinates are naturally in-place. The general concept is the
same as in [ 27]. The original x and y coordinates are replaced by multiplying and adding to them,
and once we have, we can use the new coordinates to uncompute the slope. This also means that
the circuit produces incorrect outputs if P or Q is the point at inﬁnity or if P = ±Q, because in
these cases the slope does not exist. Proos and Zalka [ 25] and RNSL [ 27] both argue that these
exceptional cases only slightly distort the desired quantum state in Shor’s algorithm and their
inﬂuence is negligible.
|x1⟩ |x3⟩
|y1⟩ |y3⟩
|ctrl⟩ |ctrl⟩
|λ= 0⟩ |0⟩
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0
0 0 0 0
0 0 0 0
n
n
n
−x2
−y2
div
div
mul
mul
+3x2 squ−
squ−
mul+
mul+
div
div
−2x2
−y2
+x2 neg
Fig. 9: A single elliptic curve addition of a classical point P = (x2,y2) with a quantum point
Q = (x1,y1) in aﬃne Weierstrass coordinates, with P + Q = (x3,y3). div indicates the circuit
from Figure 8b, squ− indicates squaring-and-subtracting (as in Figure 5b) and mul+ indicates
multiplying-and-adding.
10
