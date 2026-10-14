---
kind: source-page
source_id: arXiv:2410.00899v1
source_pdf: raw/2410.00899v1.pdf
source_page: 4
---

# Quantum schoolbook multiplication with fewer Toffoli gates - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

Figure 3: Modular multiplication circuits mod p based on controlled adders [6, 7] (a) and controlled add-subtracts (b).
We construct a version with controlled add-subtracts
in Fig. 3b. Here, we first double the input number zk−1
by adding a 0 as the least significant bit. We treat y as
an n+1-qubit number (with the most significant bit set
to 0) and perform controlled add-subtracts to obtain an
intermediate result
2zk−1 +
w−1∑
k=0
(1 −˜xk)2n+k + (2˜xk −1) ·2ky
= 2 ·result −2n(˜x + 1) + 2n+w + y −2wy .
The controlled-add-subtracts contributew(n+1) Tof-
foli gates. We apply the required corrections by per-
forming a w-qubit addition to add 2n(˜x+1) with a Tof-
foli cost of w −1, an n+w +1-qubit subtraction to sub-
tract 2n+w +y with a Toffoli cost ofn+w, and finally an
n-qubit addition to add 2wy with a Toffoli cost of n−1.
We obtain the final result after performing a division by
two by relabeling qubits. The total Toffoli count of the
multiplication is n2 + 6n + n
w
(
2w + 3 ·2w/2 + 3n −3
)
.
Conclusion. Controlled add-subtracts can be used to
construct multiplication circuits with half the asymp-
totic Toffoli count compared to constructions based
on standard controlled adders. The add-subtract-
based constructions outperform the controlled-adder-
based ones for all n ≥4. However, the Toffoli count
reduction only starts exceeding 25% atn = 8 for school-
book multiplication, at n = 6 for modular multipli-
cation mod 2n, and at n = 65 for modular multipli-
cation mod p. Still, even the latter can be useful in
practical applications. For example, several implemen-
tations of Shor’s algorithm for breaking elliptic curve
keys [6, 7, 11–15] primarily rely on modular multipli-
cation. The implementation in Ref. [15] is a family of
circuits that can be used to break 256-bit keys using
(44 + 65/k) ·106 Toffoli gates with around 3000k logi-
cal qubits of memory, where k is an integer. Replacing
4
