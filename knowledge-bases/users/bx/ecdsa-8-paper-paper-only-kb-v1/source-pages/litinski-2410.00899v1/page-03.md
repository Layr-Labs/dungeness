---
kind: source-page
source_id: arXiv:2410.00899v1
source_pdf: raw/2410.00899v1.pdf
source_page: 3
---

# Quantum schoolbook multiplication with fewer Toffoli gates - source page 3

The text below is a page-delimited extraction of the unchanged source PDF.

Figure 2: Schoolbook multiplication circuits based on controlled adders (a) and controlled add-subtracts (b), and modular multipli-
cation circuits mod 2n based on controlled adders (c) and controlled add-subtracts (d). Here, y[a,b] denotes the bit string formed
by extracting the bits of y between the a’th and b’th least significant bits.
n + w-qubit adder contributing n + w −1 Toffoli gates,
and an uncomputation of the lookup table contributing
3
√
2w Toffoli gates [10]. This results in a total Tof-
foli count of 2n2 + 4n + n
w
(
2w + 3 ·2w/2 + n −1
)
. The
choice of w that minimizes the Toffoli count is approx-
imately w ≈log2
(
n
log2 n
)
+ 2.
The first half of each ModMultStep consists of w con-
trolled additions that are controlled on the w bits of x
starting with the wk-th least significant bit. We refer
to this number as ˜x = x[wk,w(k+1)−1]. The input to
the circuit is an n-qubit number zk−1 and the circuit
outputs an n + w-qubit number
result = zk−1 +
w−1∑
k=0
˜xk ·2ky .
3
