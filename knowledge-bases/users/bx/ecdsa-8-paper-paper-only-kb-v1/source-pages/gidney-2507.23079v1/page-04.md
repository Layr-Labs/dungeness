---
kind: source-page
source_id: arXiv:2507.23079v1
source_pdf: raw/2507.23079v1.pdf
source_page: 4
---

# A Classical-Quantum Adder with Constant Workspace and Linear Gates - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

Figure 2: An n = 6 example of an adder that vents carries in order to only use 2 clean ancilla andn ±
O(1) Toffolis. Performs target→(target+ d + carryin) mod 2n, except that completing the addition requires
performing phase flips based on the vented valuesm0, . . . , mn−3. If mk is true, then a phase flip by carry(∼
target′, d,carryin)k+1 is needed, where target′ is the value of the target register after the addition. Click here
to open this circuit, specialized tod = 43, in Quirk.
Figure 3: An n = 6 variant of the carry-xor construction from [HRS17]. Performs _dirty → _dirty ⊕
⌊carry(target, d,carryin)/2⌋. Skips over the least significant carry because that’s equal to the carry input and so
is trivial to access. Click here to open this circuit, specialized tod = 43, in Quirk.
4
