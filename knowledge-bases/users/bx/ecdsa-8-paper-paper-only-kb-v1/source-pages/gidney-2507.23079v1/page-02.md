---
kind: source-page
source_id: arXiv:2507.23079v1
source_pdf: raw/2507.23079v1.pdf
source_page: 2
---

# A Classical-Quantum Adder with Constant Workspace and Linear Gates - source page 2

The text below is a page-delimited extraction of the unchanged source PDF.

uncomputation [Gid19b]). This venting process leaves behind phasing tasks that correspond
to applying a Z gate to some of the carries of the addition.
2. The vented phasing tasks can be resolved later by interleaving phase flips and Häner et al’s
construction for xoring carries into a secondary register [HRS17].
3. Dirty workspace (e.g. the secondary register targeted by the carry-xor) can be provided by
splitting the addition into two halves, with each half borrowing the other as dirty workspace.
The paper is structured as follows. In Section 2, I explain the construction of the adder and
some variants. In Section 3, I summarize the results.
2 Construction
2.1 Notation
The bit at indexk of an integerx is referred to asxk (for examplex0 is the even-vs-odd bit):
xk = ⌊x/2k⌋mod 2 (1)
The bitwise xor ofx and y is writtenx⊕y:
x⊕y=
∞∑
k=0
(xk + yk −2xkyk)2k (2)
(Use the 2-adic metric to get the above sum to converge whenx or y are negative.)
The bitwise complement ofx is written∼x:
∼x= −1 ⊕x= −1 −x (3)
The majority of three bits is the most common bit value among the three:
maj(a,b,c ) = ⌊(a+ b+ c)/2⌋
= ((a⊕c) ·(b⊕c)) ⊕c (4)
The “carry” of an addition is the extra bit flips that occur due to propagating carries (including
from the carry input bitc0). It’s the xor between the actual result of the addition and the xor of
its two inputs:
carry(x,d,c 0) = x⊕d⊕(x+ d+ c0) (5)
Lastly, this paper uses some non-standard circuit notation defined in Figure 1.
Figure 1: Non-standard circuit notation in this paper. Left: Bit-inverted controls. A black box containing the
text "Z ⊕b" means the control’s required value is inverted when the bitb is True. Middle: Controlling with a
ZZ operator. Conditioning on a multi-qubit parity operator, likeZZ, is shown as black boxes to the side of the
control line indicating each of theZ terms. Right: Controlling with the intersection of two ZZ operators. When
an operation has two parity controls, terms from one are placed to the left of the control line while terms from
the other are placed to the right. I prefer parity controls over CNOT gates because accessingZZ is notably
cheaper than doing CNOTs when compiling into lattice surgery.
2
