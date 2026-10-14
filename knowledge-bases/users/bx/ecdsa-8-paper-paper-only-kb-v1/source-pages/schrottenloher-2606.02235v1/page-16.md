---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 16
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 16

The text below is a page-delimited extraction of the unchanged source PDF.

Algorithm 9Non-exact controlled modular addition circuit.
control = input(BoolType())
x_reg = input(ModIntType(p))
y_reg = input(ModIntType(p))
anc_x = anc(1)
anc_y = anc(1)
cadd_uint(control, x_reg + anc_x, y_reg + anc_y)
anc = anc(1)
lt_uint(y_reg[-msbs:] + anc_y, q_msbs, anc)
self.x(anc[0])
csub_uint(anc, q, y_reg + anc_y)
clt_uint(control,y_reg[-msbs:], x_reg[-msbs:], anc)
the casex+y=q(which would not happen randomly), and one that does not
need to.
Algorithm 10Pseudo-Mersenne controlled modular addition circuit, which
does not handlex+y=q.
control = input(BoolType())
x_reg = input(ModIntType(q))
y_reg = input(ModIntType(q))
anc_x = anc(1)
anc_y = anc(1)
cadd_uint(control, x_reg + anc_x, y_reg + anc_y)
cadd_uint(anc_y, f, y_reg[:lsbs])
clt_uint(control, y_reg[-msbs:], x_reg[-msbs:], anc_y)
The latter is given in Algorithm 10. We first perform the controlled addition,
then if the register overflows, we addfin the LSBs of the output registery. We
erase the overflow bit by a new comparison.
The algorithm handling the casex+y=qis given in Algorithm 11. It detects
whetherx+y=qby checking if all MSBs are 1. Ifx+y=q, then after reduction,
the registeryshould contain 0. Thus the bit is erased by checking if all MSBs
are 0.
Difference of Cost.As can be seen in Table 1, there is a significant difference
between the case of a pseudo-Mersenne prime as insecp256k1and the generic
case. This comes entirely from the different implementations given above. An
important factor is that, for the operations which happen during the B´ ezout
reconstruction step, we need to optimize the space, so when we need to add or
subtractq, we use Gidney’s constant adder [8] with dirty ancillas (which costs
3nToffoli gates forn-bit integers). Reducing the constant addition steps fromq
tofis a significant gain of gate count.
16
