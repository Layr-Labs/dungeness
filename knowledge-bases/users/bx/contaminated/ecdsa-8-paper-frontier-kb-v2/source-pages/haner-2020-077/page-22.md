---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 22
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 22

The text below is a page-delimited extraction of the unchanged source PDF.

|x⟩
|y⟩
|0⟩
|z⟩
n
n
n
n
×
|0⟩
|xy⟩
n
+ −†
|0⟩
|xy⟩
|xy+ z⟩ ×†
|x⟩
|y⟩
|0⟩
|xy+ z⟩
Fig. 13: Quantum circuit that implementsxy+zmod p, using out-of-place constructions for modular
multiplication, modular addition, and modular subtraction.
4. The automatically generated unitaries are composed as described in Figure 13, which uses the
technique shown in Figure 11 to turn the out-of-place addition and subtraction into an in-place
addition.
Table 5: Comparison of resource costs between a manual and automatic construction to implement
|xy+ zmod p⟩.
Manual construction Automatic construction
Bit-width T-count T-depth Width T-count T-depth Width
256 8,176,739 50,253 2,319 1,576,296 1,542 394,588
384 18,322,671 76,125 3,470 3,550,552 2,310 888,408
521 33,751,240 137,183 4,702 6,535,384 3,132 1,634,890
Table 5 lists the resource costs in terms of T-count, T-depth, and circuit width, for both the
manual construction and the automatic construction. Several factors of reduction in T-count and
T-depth are possible, while the increase in the number of qubits is signiﬁcant. However, such a
design point can be of high interest, in particular when combined with automatic quantum memory
strategies, e.g., pebbling [ 20], that can ﬁnd intermediate trade-oﬀ points that lie in between the
manual and automatic construction.
22
