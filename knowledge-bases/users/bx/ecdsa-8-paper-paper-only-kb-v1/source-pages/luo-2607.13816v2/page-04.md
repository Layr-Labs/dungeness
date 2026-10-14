---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 4
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

Reference Space of point addition Space of modular inversion
[RNSL17] 9n+ 2 log2 n+O(1) 7n+ 2 log2 n+O(1)
[HJN+20] 8n+ 10.2 log2 n+O(1) 7n+ log 2 n+O(1)
[CFS26] 3.12n+o(n) not based on modular inversion
[Sch26] 4.12n+O( √n) 2.12n+O( √n)
This work 3n+ 6 log2 n+O(1) 2n+ 6 log2 n+O(1)
Table 1: Comparison of the number of logical qubits required for ECDLP and modular inversion.
addition circuit with mid-circuit measurement (Figures 15 and 14), we obtain a complexity of 1003n 2 +
O(nlog 2 n) Toffoli gates per point addition. Furthermore, incorporating the point addition circuit into
the complete quantum algorithm for solving the ECDLP using the signed-window technique [HJN +20,
Section 5.1] yields a total Toffoli-gate complexity of 1008n 3/log 2 n+O(n 2).
We complement the asymptotic comparison with numerical gate-count estimates and concrete secp256k1
resource estimates. Figure 1 reports the Toffoli and CNOT counts of our modular-inversion and point-
addition circuits as functions of the field sizenand Table 2 compares the resulting secp256k1 estimates
with recent quantum ECDLP implementations. For secp256k1, our construction uses 835 logical qubits,
saving more than 250 logical qubits compared to 1098 qubits in the previous best space-optimized es-
timate of Chevignard et al. [CFS25]. Furthermore, our Toffoli count is two orders of magnitude lower
than [CFS25].
0 64 128 160 192 224 256 384 512
Bit size n
0
20
40
60
80
100
120
140
160
180Gate count (×106)
T offoli
CNOT
(a) modular inversion count
0 64 128 160 192 224 256 384 512
Bit size n
0
50
100
150
200
250
300
350
400
450Gate count (×106)
T offoli
CNOT (b) point addition count
Figure 1: Toffoli gate count and CNOT gate count for modular inversion and point addition.
1.2 Overview
We present an overview of our quantum circuit for solving ECDLP. The standard implementation of
Shor’s algorithm consists of 2n+2 controlled elliptic-curve point additions followed by a quantum Fourier
transform (QFT), as illustrated in Figure 2. Replacing the QFT with its semiclassical variant reduces
the logical-qubit requirement without altering the algorithmic functionality, as shown in Figure 3.
4
