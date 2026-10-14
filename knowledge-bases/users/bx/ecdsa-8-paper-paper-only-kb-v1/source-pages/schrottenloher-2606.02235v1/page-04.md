---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 4
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

Table 2.Cost of running Shor’s algorithm entirely and comparison with [2]. The
“Toffolis” column counts together CCX, CCZ as well as And gates.
Type Qubits Toffolis Reference
Space-optimized forsecp256k11191 28×(2 21.36 + 3·2 16) = 226.27 [2]
Gate-optimized forsecp256k11441 28×(2 21.00 + 3·2 16) = 225.94 [2]
Space-optimized forsecp256k11208 28×(2 21.19 + 3·2 16) = 226.11 Ours
Gate-optimized forsecp256k11462 28×(2 20.83 + 3·2 16) = 225.78 Ours
Space-optimized for any prime 1208 28×(2 21.78 + 3·2 16) = 226.66 Ours
Gate-optimized for any prime 1462 28×(2 21.42 + 3·2 16) = 226.33 Ours
whereP, Qare points on the elliptic curve given by the discrete logarithm in-
stance (Qis the input andPis the basis of the discrete logarithm). Although
the registersu, vtakenbits each roughly, wherenis the bit-size of the group
of points, they do not count towards the total qubit count thanks to thesemi-
classical Fourier transformwith qubit recycling, and we can focus instead on
the points.
Point multiplication is then reduced towindowed point addition, where one
uses aw-bit integer inputito select a point from a built-inwindow(P 0, . . . , P2w−1),
and add the constant point to the variable input:
|i⟩|R⟩ 7→ |i⟩|R+Pi⟩.
Finally, the point addition by a constant is done by an algorithm of [11]. Points
are represented usingaffinecoordinates, i.e., a pair of integers moduloq. The
addition byP i is reduced to a sequence of arithmetic operations moduloqand
threelookups, which are the circuits loading the coordinates ofP i from the input
i. All this high-level structure is detailed in Section 2 and is explicit in Babbush
et al.’s paper [2].
From In-Place Multiplication to the Extended Euclidean Algorithm (Section 3).
When doing point addition like this, one observes that the most costly step is to
multiply in-placetwo integers moduloq:|x, y⟩ 7→ |x, xy⟩. This operation happens
twice in the point addition circuit. Previous works like [19,13,11,15] reduced it
tomodular inversionand out-of-place multiplication (|x, y, z⟩ 7→ |x, y, z+xy⟩),
and implemented modular inversion using reversible variants of binary Extended
Euclidean Algorithm (EEA). While inversion and multiplication onn-bit mod-
ular integers have both a gate count inO

n2
(as does the entire point addition
circuit), the constant is noticeably bigger for the inversion part.
In Section 3, we detail the implementation of this step. The main idea, taken
from [14], is to separate the EEA into two sub-circuits. The first circuit is an
Euclidean algorithm which operates on a pair of integers (u, v) (which should
start at (q, x) if we are invertingxmoduloq), performs the operations of the
Euclidean algorithm, and outputs a bit-string describing the operations that it
has performed, ensuring reversibility. This sequence of operations is named a
4
