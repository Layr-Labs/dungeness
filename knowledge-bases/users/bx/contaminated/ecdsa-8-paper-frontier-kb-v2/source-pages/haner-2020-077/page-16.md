---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 16
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 16

The text below is a page-delimited extraction of the unchanged source PDF.

addition with projective coordinates with cost C, we can transform it to a quantum-suitable
in-place version with cost 2 C+ 2D, where D is the cost of division. The division creates a unique
representation.
Some projective coordinate systems such as projective x-only Montgomery coordinates can
only handle diﬀerential addition. In this case, we start with P, Q, and Q−P, and use Q−P as a
helper to compute P + Q. We did not ﬁnd a method to clear the register with P from the outputs
Q, Q−P, and P + Q, so we are further restricted to curves that have direct addition formulas.
According to the Explicit Formulas Database [ 6], the lowest-cost addition, possibly assuming
Z = 1 for the initial point, uses 6 squares and/or multiplications. With the required reductions,
the total cost is 12 squares/multiplications and 2 divisions, much higher than aﬃne Weierstrass
coordinates. Thus, we choose not to use projective coordinates in this work.
Elliptic curve point addition in aﬃne Montgomery coordinates. An alternative aﬃne
coordinate system is provided by elliptic curves in Montgomery form
by2 = x3 + ax2 + x. (3)
Again, we represent points as pairs ( x,y) that satisfy the curve equation.
Following the reference implementation for aﬃne coordinate addition from [ 16], we construct
the circuit in Figure 12. This uses one more register than aﬃne Weierstrass coordinates, one more
multiplication, and one more squaring.
|x1⟩
|y1⟩
|ctrl⟩
|λ= 0⟩⏐⏐λ2 = 0⟩
0 0 0
0 0 0
0 0
0 0
0 0
0 0
0 0
b b
0 0
0 0
0 0
0 0 0
0 0 0
0 0
0 0
0 0
0 0
n
n
n
−x2
−y2
div
div
div
mul
mul
mul
+3x2+a
squA
mul−
mul−
mul−
squ−1A
mul
mul
mul
−2x2
div
div
div
neg
−y2
−x2
Fig. 12: Constant point addition in aﬃne Montgomery coordinates.
However, we note that the main source of extra costs is that, for a slope λ, there is a bλ3 term.
This requires 4 sequential multiplications/squarings. If we are lucky enough to have a curve where
b = 1, then we save space and operations by directly adding the λ2 to the x1 register. In fact,
in this case, we can simply use the Weierstrass addition circuit, so long as we replace the +3 x2
operator with +3x2 + a. Thus, we have no reason to prefer aﬃne Montgomery coordinates, and we
will continue to use short Weierstrass form.
A.5 Precomputation.
Precomputed tables of certain powers of the base element can speed up exponentiations. The
“comb” method is a standard technique used for elliptic curve scalar multiplication. To multiply a
point P by a scalar k, we divide k into k1 + 2k2 + ··· + 2ℓkℓ for some ℓ, with the property that
kj contains bits of k in positions congruent to j modulo ℓ (each kj looks like a comb of bits). We
then precompute a table of all multiples of P by scalars of the form b0 + b12ℓ + b222ℓ ... , with
bi ∈{0,1}. By the deﬁnition of kj, each kjP is a precomputed point in this table for all j. Thus,
we can compute kP by using kj to look up elements of the table, adding them to a running total,
and doubling the running total.
16
