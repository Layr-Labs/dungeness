---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 8
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 8

The text below is a page-delimited extraction of the unchanged source PDF.

Algorithm 1Reversible point addition circuit (from [11], slightly modified to
allow addition ofO).
Parameter:window of pointsP 0, . . . , P2w−1
Input:Registersx 2, y2 (coordinates ofR), registeri
Output:Registers are modified in-place and containR+P i
1:c←(i̸= 0)
2:x 1, y1 ←Lookup(P i)▷First lookup
▷Wheni= 0, we havex 1, y1 = 0 per our definition
3:x 2 ←x 2 −x 1
4:y 2 ←y 2 −y 1
5: Unlookup(P i)▷Removesx 1, y1
6:x 2, y2 ←x 2, y2 ·x −1
2 ▷Inverse of an in-place multiplication
7:x←Lookup(3x Pi )▷Second lookup
8:x 2 ←x 2 +x
9: Unlookup(3x Pi )▷Removesx
10: Ifcthenx 2 ←x 2 −y 2
2 ▷Controlled modular squaring
11:x 2, y2 ←x 2, y2 ·x 2 ▷In-place multiplication
12: Ifcthenx 2 ← −x2 ▷Controlled modular negation
13:x 1, y1 ←Lookup(P i)▷Third lookup
14:y 2 ←y 2 −y 1
15:x 2 ←x 2 +x 1
16: Unlookup(P i)▷Removesx 1, y1
17: Uncomputec
During the computation of the formulas, we need to use the coordinates ofPi
three separate times: first the entire point, then 3xPi , then the entire point again.
Each time, we load these coordinates using atable lookupcircuit, and unload
them immediately after use. A table lookup of 2w values costs 2w Toffoli gates [1],
and the unlookup is almost free thanks to measurement-based uncomputation.
In addition, the Toffoli gate count of lookups being still an order of magnitude
below the cost of the other operations, we could also just compute the inverse
of the lookup circuit.
As can be seen in Algorithm 1, the circuit contains 3 lookups, some arithmetic
operations inO(n) gates, a modular squaring, and twoin-place multiplication
circuits which we will detail next.
Number of Point Additions.The number of point additions can slightly be op-
timized [2], following [15]. Indeed, the first addition can be replaced by a lookup
of the result, and the last three ones can be removed at the cost of more clas-
sical post-processing [6]. In thesecp256k1case, this means that only 28 point
additions are necessary.
3 Modular In-Place Multiplication
The modular in-place multiplication:
|x⟩|y⟩ 7→ |x⟩|yx⟩(6)
8
