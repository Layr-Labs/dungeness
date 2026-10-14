---
kind: source-page
source_id: arXiv:2410.00899v1
source_pdf: raw/2410.00899v1.pdf
source_page: 5
---

# Quantum schoolbook multiplication with fewer Toffoli gates - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

the controlled-adder-based multiplication circuits with
controlled-add-subtract-based circuits reduces the Tof-
foli count to (30 + 73/k) ·106 Toffoli gates per key.
Asymptotically, this is a reduction of over 30% from
44 million to 30 million Toffoli gates per key. However,
for moderate values of k, this reduction will be lower,
e.g., a reduction of 20% for k = 4, going from 60 million
to 48 million Toffoli gates per key.
Multiplication circuits are also useful outside of cryp-
tography applications. For instance, in some variations
of quantum simulation algorithms, they may be used
to compute potential and kinetic energies. While there
exist multiplication circuits with better asymptotic scal-
ing [16–19], schoolbook multiplication is typically still
cheaper for practically relevant problem sizes. This pa-
per is also meant to highlight the usefulness of the con-
trolled add-subtract operation. It has previously been
used to reduce the cost of square roots [4] and controlled
rotations [5], so perhaps it can be used to reduce the cost
of other subroutines that rely on controlled adders.
Acknowledgments
I would like to thank Jessica Lemieux and Mark Steudt-
ner for discussions that inspired this construction.
A Additional figures
Figure 4 shows a Gidney adder [3] with and without
carry-out.
References
[1] E. T. Campbell, B. M. Terhal, and C. Vuil-
lot, Roads towards fault-tolerant universal quantum
computation, Nature 549, 172 (2017).
[2] B. M. Terhal, Quantum error correction for quan-
tum memories, Rev. Mod. Phys. 87, 307 (2015).
[3] C. Gidney, Halving the cost of quantum addition,
Quantum 2, 74 (2018).
[4] E. Mu˜ noz-Coreas and H. Thapliyal, T-count and
qubit optimized quantum circuit design of the non-
restoring square root algorithm, arXiv:1712.08254
(2017).
[5] Y. R. Sanders, D. W. Berry, P. C. Costa, L. W.
Tessler, N. Wiebe, C. Gidney, H. Neven, and
R. Babbush, Compilation of fault-tolerant quantum
heuristics for combinatorial optimization, PRX
Quantum 1, 020312 (2020).
[6] T. H¨ aner, S. Jaques, M. Naehrig, M. Roetteler,
and M. Soeken, Improved quantum circuits for
elliptic curve discrete logarithms, Post-Quantum
Cryptography , 425 (2020).
[7] ´Elie Gouzien, D. Ruiz, F.-M. L. R´ egent, J. Guil-
laud, and N. Sangouard, Computing 256-bit Ellip-
tic Curve Logarithm in 9 Hours with 126133 Cat
Qubits, arXiv:2302.06639 (2023).
[8] P. L. Montgomery, Modular multiplication without
trial division, Mathematics of computation 44, 519
(1985).
[9] R. Babbush, C. Gidney, D. W. Berry, N. Wiebe,
J. McClean, A. Paler, A. Fowler, and H. Neven,
Encoding electronic spectra in quantum circuits
with linear T complexity, Phys. Rev. X 8, 041015
(2018).
[10] C. Gidney, Windowed quantum arithmetic,
arXiv:1905.07682 (2019).
[11] P. Shor, Algorithms for quantum computation: dis-
crete logarithms and factoring, Proceedings 35th
Annual Symposium on Foundations of Computer
Science , 124 (1994).
[12] P. W. Shor, Polynomial-time algorithms for prime
factorization and discrete logarithms on a quantum
computer, SIAM Journal on Computing 26, 1484
(1997).
[13] J. Proos and C. Zalka, Shor’s discrete logarithm
quantum algorithm for elliptic curves, arXiv:quant-
ph/0301141 (2003).
[14] M. Roetteler, M. Naehrig, K. M. Svore,
and K. Lauter, Quantum resource estimates
for computing elliptic curve discrete logarithms,
arXiv:1706.06752 (2017).
[15] D. Litinski, How to compute a 256-bit elliptic curve
private key with only 50 million Toffoli gates,
arXiv:2306.08585 (2023).
[16] A. Parent, M. Roetteler, and M. Mosca, Improved
reversible and quantum circuits for Karatsuba-
based integer multiplication, arXiv:1706.03419
(2017).
[17] S. Dutta, D. Bhattacharjee, and A. Chattopad-
hyay, Quantum circuits for Toom-Cook multiplica-
tion, Phys. Rev. A 98, 012311 (2018).
[18] C. Gidney, Asymptotically efficient quantum
Karatsuba multiplication, arXiv:1904.07356
(2019).
[19] G. D. Kahanamoku-Meyer and N. Y. Yao, Fast
quantum integer multiplication with zero ancillas,
arXiv:2403.18006 (2024).
5
