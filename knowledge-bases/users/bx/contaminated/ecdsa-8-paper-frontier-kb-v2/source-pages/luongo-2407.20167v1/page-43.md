---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 43
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 43

The text below is a page-delimited extraction of the unchanged source PDF.

[NC11] Michael A. Nielsen and Isaac L. Chuang. Quantum Computation and Quantum
Information: 10th Anniversary Edition . Cambridge University Press, 2011. isbn:
9781107002173.
[Sho94] Peter W. Shor. “Algorithms for quantum computation: Discrete logarithms and
factoring”. In: Proceedings 35th Annual Symposium on Foundations of Computer
Science. IEEE. 1994, pp. 124–134.
[Tak09] Yasuhiro Takahashi. “Quantum arithmetic circuits: a survey”. In: IEICE TRANSAC-
TIONS on Fundamentals of Electronics, Communications and Computer Sciences 92.5
(2009), pp. 1276–1283.
[TTK09] Yasuhiro Takahashi, Seiichiro Tani, and Noboru Kunihiro. “Quantum Addition Circuits
and Unbounded Fan-Out”. In: (2009).
[VBE96] Vlatko Vedral, Adriano Barenco, and Artur Ekert. “Quantum networks for elementary
arithmetic operations”. In: Physical Review A 54.1 (1996), p. 147.
[Von93] John Von Neumann. “First Draft of a Report on the EDVAC”. In: IEEE Annals of
the History of Computing 15.4 (1993), pp. 27–75.
[Wan+24a] Siyi Wang, Suman Deb, Ankit Mondal, and Anupam Chattopadhyay. “Optimal Toffoli-
Depth Quantum Adder”. In: arXiv preprint arXiv:2405.02523 (2024).
[Wan+24b] Siyi Wang, Xiufan Li, Wei Jie Bryan Lee, Suman Deb, Eugene Lim, and Anupam
Chattopadhyay. “A Comprehensive Study of Quantum Arithmetic Circuits”. In: arXiv
preprint arXiv:2406.03867 (2024).
[Yua+23] Yewei Yuan, Chao Wang, Bei Wang, Zhao-Yun Chen, Meng-Han Dou, Yu-Chun Wu,
and Guo-Ping Guo. “An improved QFT-based quantum comparator and extended
modular arithmetic using one ancilla qubit”. In: New Journal of Physics 25.10 (2023),
p. 103011.
[Zal06] Christof Zalka. “Shor’s algorithm with fewer (pure) qubits”. In: arXiv preprint quant-
ph/0601097 (2006).
A Background on binary arithmetics
In this appendix, we briefly survey some standard results on bit string arithmetics. In particular,
we recall how bit strings can be interpreted as unsigned or signed integers. We refer to the section
1.3 for our notation on bit strings arithmetics.
Proposition A.1. The bit string subtraction can be expressed in terms of 2’s complement as
x − y = x + y .
Proof. According to definition 1.2 and 1.4, the string on the right-hand side is defined bitwise as
rk = xk ⊕ yk ⊕ 1 ⊕ zk, where zk is defined recursively as follows
z0 = 1
zi+1 = maj(xi, yi ⊕ 1, zi) .
The thesis follows by showing inductively that zk = bk ⊕ 1, where bk is the borrowing defined in
definition 1.5. Namely, assume zk = bk ⊕ 1, then
zk+1 = xkyk ⊕ xkyk ⊕ xkzk ⊕ ykzk ⊕ xk ⊕ zk
= xkyk ⊕ xkyk ⊕ xk(bk ⊕ 1) ⊕ yk(bk ⊕ 1) ⊕ xk ⊕ bk ⊕ 1
= xkyk ⊕ xkyk ⊕ xkbk ⊕ ykbk ⊕ yk ⊕ bk ⊕ 1
= bk+1 ⊕ 1 .
43
