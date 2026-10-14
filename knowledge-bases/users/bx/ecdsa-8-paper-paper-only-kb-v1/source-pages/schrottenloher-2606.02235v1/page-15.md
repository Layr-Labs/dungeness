---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 15
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 15

The text below is a page-delimited extraction of the unchanged source PDF.

Algorithm 6Non-exact modular doubling circuit.
x_reg = input(ModIntType(q))
anc1, anc2 = anc(1), anc(1)
shift_right(x_reg + anc1, 1)
lt_uint(x_reg[-padding:] + anc1, q_msbs, anc2) # non-exact step
self.x(anc2)
csub_uint(anc2, q, x_reg + anc1)
cx(x_reg[0], anc2)
Algorithm 7Pseudo-Mersenne modular doubling circuit.
x_reg = input(ModIntType(q))
anc1 = anc(1)
shift_right(x_reg + anc1, 1)
cadd_uint(anc1, f, x_reg[:lsbs])
cx(x_reg[0], anc1[0])
and a comparison to erase an ancilla qubit. (Note that compared to the non-
controlled circuit, the subtraction / addition ofqdo not need to be modified).
Algorithm 8Exact controlled modular addition circuit from [20].
control = input(BoolType())
x_reg = input(ModIntType(p))
y_reg = input(ModIntType(p))
anc_x = anc(1)
anc_y = anc(1)
cadd_uint(control, x_reg + anc_x, y_reg + anc_y)
sub_uint(p, y_reg + anc_y)
cadd_uint(anc_y, p, y_reg)
clt_uint(control, y_reg, x_reg, anc_y)
x(anc_y)
Our first simplification is given in Algorithm 9. We first perform a non-
modular (controlled) addition, then check if the result overflows (but only on
the MSBs). If it does, we subtractqfrom the result. The ancilla bit checking
the overflow can then be erased by the conditiony < x, since the only case
where this happens is precisely when there was an overflow. Both comparisons
being performed only on the MSBs, the remaining dominating operations are a
controlled addition and a controlled subtraction by a constant.
Whenqis a pseudo-Mersenne prime of the form 2 u −f, wheref≪2 u, we
can further simplify this circuit. Here we need two variants: one that handles
15
