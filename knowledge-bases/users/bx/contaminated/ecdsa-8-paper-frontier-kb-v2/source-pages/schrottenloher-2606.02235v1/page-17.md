---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 17
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 17

The text below is a page-delimited extraction of the unchanged source PDF.

Algorithm 11Pseudo-Mersenne controlled modular addition circuit which han-
dlesx+y=q.
control = input(BoolType())
x_reg = input(ModIntType(q))
y_reg = input(ModIntType(q))
anc_x = anc(1)
anc_y = anc(1)
cadd_uint(control, x_reg + anc_x,y_reg + anc_y)
anc = anc(1)
y_is_q = all(y_reg[-msbs:])
cxor(y_is_q, q, y_reg) # Controlled-XOR of constant (CNOT gates)
cx(anc_y, anc)
cadd_uint(anc, f, y_reg[:lsbs])
cx(anc, anc_y)
clt_uint(control, y_reg[-msbs:], x_reg[-msbs:], anc)
cx(y_is_q, anc)
y_is_q = all(not y_reg[-msbs:])
5 Discussion
After constructing the entire circuit, it is interesting to look at the proportion
of the CCX cost of all its sub-circuits (we count together CCX and And gates
resulting from Gidney’s adder construction [7]). Our estimations are given in Ta-
ble 3. We can see as noticed above that the difference in gate count between a
pseudo-Mersenne prime and a generic prime can be attributed to the modu-
lar addition and doubling circuits, and more precisely to the constant additions
therein.
Table 3.Proportion of the CCX cost of different sub-circuit components.
Space-optimized
forsecp256k1
Space-optimized
for any prime
Main components:
Modular squaring 9 % 10 %
In-place multiplier and its inverse 90 % 90 %
B´ ezout reconstruction 54 % 64 %
GCD construction 36 % 24 %
Some sub-components:
Controlled-swap 19 % 12 %
Hybrid adder 22 % 14 %
Controlled modular adder (and inverse) 39 % 45 %
Modular double (and inverse) 8 % 24 %
Gidney constant adder (controlled and not) 15 % 34 %
17
