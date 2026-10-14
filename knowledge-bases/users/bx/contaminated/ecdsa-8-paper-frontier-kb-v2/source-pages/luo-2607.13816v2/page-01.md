---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 1
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

Quantum Algorithm for Elliptic Curve Discrete Logarithms with
Space-Efficient Point Addition∗
Han Luo†1, Ziyi Yang†2,3, Jingquan Luo†4, Ziruo Wang2,3, Yuexin Su2,3, Xiaoming Sun5,6,
Lvzhou Li‡4, and Tongyang Li§2,3
1Institute for Interdisciplinary Information Sciences, Tsinghua University
2Center on Frontiers of Computing Studies, Peking University
3School of Computer Science, Peking University
4Institute of Quantum Computing and Software, School of Computer Science and Engineering,
Sun Yat-Sen University
5State Key Lab of Processors, Institute of Computing Technology, Chinese Academy of Sciences
6School of Computer Science and Technology, University of Chinese Academy of Sciences
Abstract
The Elliptic Curve Discrete Logarithm Problem (ECDLP) is a fundamental problem in cryptog-
raphy, and reducing the resource requirements of quantum algorithms for solving ECDLP is an im-
portant goal. In this work, we present a space-efficient quantum algorithm for solving the ECDLP
over prime fields, achieving an implementation with only 3n+ 6⌊log 2 n⌋+O(1) logical qubits and
1008n3/log 2 n+O(n 2) Toffoli gates, wherenis the bit-length of the prime. For a 256-bit prime-field
curve, our construction requires only 835 logical qubits, reducing the previous best estimates of 1098
and 1175 logical qubits by Chevignard et al. [EUROCRYPT 2026] and Babbush et al. [ArXiv Preprint
2026], respectively.
The key to our improvement is a new space-efficient reversible modular inversion circuit, which ad-
dresses the dominant space bottleneck in affine-coordinate point addition. Starting from the extended
Euclidean algorithm (EEA), we refine the register-sharing technique of Proos and Zalka by introducing
length registers and location-controlled arithmetic to compactly store and update intermediate vari-
ables. We further optimize the reversible update procedures and construct the corresponding controlled
arithmetic circuits, resulting in a modular inversion circuit implemented by only 2n+ 6⌊log 2 n⌋+O(1)
logical qubits and 217n2 +O(nlog 2 n) Toffoli gates. This modular inversion circuit together with mid-
circuit measurements and classical feed-forward operations provides a space-efficient controlled affine
point-addition circuit and a complete implementation of Shor’s algorithm for ECDLP.
∗This paper supersedes our earlier preprint arXiv:2604.02311. Compared with the earlier version, the present paper
reduces the space complexity from 5n+O(log 2 n) to 3n+O(log 2 n) for affine point addition and from 3n+O(log 2 n) to
2n+O(log 2 n) for modular inversion. It also improves the overall Toffoli counts of ECDLP fromO(n 3) toO(n 3/logn).
†Equal contribution.
‡Corresponding author. Email: lilvzh@mail.sysu.edu.cn
§Corresponding author. Email: tongyangli@pku.edu.cn
1
arXiv:2607.13816v2  [quant-ph]  9 Aug 2026
