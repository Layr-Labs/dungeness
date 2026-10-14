---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 9
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 9

The text below is a page-delimited extraction of the unchanged source PDF.

|carry= 0⟩
|ui⟩
|vi⟩
|ri⟩
|si⟩
|b = 0⟩
|a = 0⟩
|mi = 0⟩
n
n
n+1
n+1
- + /2
×2
/2
×2
-
+
/2
×2
-
+
/2
×2
|0⟩
|ui+1⟩
|vi+1⟩
|ri+1⟩
|ri+1⟩
|0⟩
|0⟩
|mi⟩
(a) Round operation from [27].
|carry = 0⟩
|ui⟩
|vi⟩
|ri⟩
|si⟩
|b = 0⟩
|a = 0⟩
|mi = 0⟩
n
n
n+1
n+1
> > −
+
/2
×2
|0⟩
|ui+1⟩
|vi+1⟩
|ri+1⟩
|ri+1⟩
|0⟩
|0⟩
|mi⟩
(b) Improved round operation.
Fig. 6: Improvement to the round operation in the binary extended Euclidean algorithm from [ 27]
addressing the diﬀerent cases by controlled swaps.
(a) Kaliski’s algorithm
1: if u odd and v even then
2: v←v/2
3: r←2r
4: else ifu even and v odd then
5: u←u/2
6: s←2s
7: else if u odd and v odd and u > v
then
8: u←(u−v)/2
9: r←r+ s
10: s←2s
11: else if u odd and v odd and v ≥u
then
12: v←(v−u)/2
13: s←r+ s
14: r←2r
15: end if
(b) Equivalent formulation
1: bswap ←false
2: if u even and v odd, or u and v both
odd and u>v then
3: swap u and v
4: swap r and s
5: bswap ←true
6: end if
7: if u odd and v odd then
8: v←v−u
9: s←r+ s
10: end if
11: v←v/2
12: r←2r
13: if bswap then
14: swap u and v
15: swap r and s
16: end if
Fig. 7: Kaliski’s algorithm, and an equivalent formulation based on swaps.
9
