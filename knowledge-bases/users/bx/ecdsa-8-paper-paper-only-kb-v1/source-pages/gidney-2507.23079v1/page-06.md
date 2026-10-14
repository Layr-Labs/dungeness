---
kind: source-page
source_id: arXiv:2507.23079v1
source_pdf: raw/2507.23079v1.pdf
source_page: 6
---

# A Classical-Quantum Adder with Constant Workspace and Linear Gates - source page 6

The text below is a page-delimited extraction of the unchanged source PDF.

Figure 5: An n = 9 example of an adder circuit that uses 3 clean ancillae and4n ±O(1) Toffolis. Top:
decomposed into other subroutines defined by the paper. Bottom: further decomposed into constant sized
gates. Performs target→(target+ d + carryin) mod 2n.
Figure 6: A controlled variant of Figure 5, specialized to the cased = 279. Performs target→(target+control·
(279 +carryin)) mod 2n. 279 in binary is 100010111, so this circuit substitutesd8, d4, d2, d1, d0 →control and
d7, d6, d5, d3 →0.
6
