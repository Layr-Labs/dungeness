---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 34
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 34

The text below is a page-delimited extraction of the unchanged source PDF.

34
https://www.olcf.ornl.gov/wp-content/uploads/Public-AMD-Instinct-MI-250X-Frontier-8.23.23.pdf .
[38] Y. Chen, Q. Liu, and M. Zhandry, Quantum algorithms for variants of average-case lattice problems via filtering, inAnnual
international conference on the theory and applications of cryptographic techniques(Springer, 2022) pp. 372–401.
[39] G. L. Mullen and D. Panario,Handbook of finite fields, Vol. 17 (CRC press Boca Raton, 2013).
[40] P. Briaud, I. Dinur, R. Ghosal, A. Jain, P. Lou, and A. Sahai, Quantum advantage via solving multivariate polynomials
(2025), arXiv:2509.07276 [quant-ph].
[41] W. Hoeffding, Probability inequalities for sums of bounded random variables, Journal of the American Statistical Associ-
ation 58, 13 (1963).
[42] J. Von Zur Gathen and J. Gerhard,Modern computer algebra(Cambridge university press, 2003).
[43] A. Schönhage and V. Strassen, Schnelle multiplikation großer zahlen, Computing7, 281–292 (1971).
[44] D. G. Cantor and E. Kaltofen, On fast multiplication of polynomials over arbitrary algebras, Acta Informatica28, 693
(1991).
[45] D. Harvey, J. van der Hoeven, and G. Lecerf, Faster polynomial multiplication over finite fields (2014), arXiv:1407.3361
[cs.CC].
[46] J. Justesen, On the complexity of decoding reed-solomon codes (corresp.), IEEE Transactions on Information Theory22,
237 (2006).
[47] A. Bartschi and S. Eidenbenz, Short-depth circuits for dicke state preparation, in2022 IEEE International Conference on
Quantum Computing and Engineering (QCE)(IEEE, 2022) p. 87–96.
[48] O. Garcia-Morchon, R. Rietman, I. E. Shparlinski, and L. Tolhuizen, Interpolation and approximation of polynomials in
finite fields over a short interval from noisy values, Experimental mathematics23, 241 (2014).
[49] G. D. Kahanamoku-Meyer, S. Ragavan, V. Vaikuntanathan, and K. Van Kirk, The Jacobi factoring circuit: Quantum
factoring with near-linear gates and sublinear space and depth, inProceedings of the 57th Annual ACM Symposium on
Theory of Computing(2025) pp. 1496–1507.
[50] C. Gidney, M. Newman, P. Brooks, and C. Jones, Yoked surface codes, Nature Communications16, 4498 (2025).
[51] C. Gidney, N. Shutty, and C. Jones, Magic state cultivation: growing T states as cheap as CNOT gates (2024),
arXiv:2409.17595 [quant-ph].
[52] C. Gidney, A classical-quantum adder with constant workspace and linear gates (2025), arXiv:2507.23079 [quant-ph].
[53] C. Gidney, Inplace access to the surface code y basis, Quantum8, 1310 (2024).
[54] A. Chailloux and J.-P. Tillich, Quantum advantage from soft decoders, inProceedings of the 57th Annual ACM Symposium
on Theory of Computing(2025) pp. 738–749.
[55] V. Guruswami and M. Sudan, Improved decoding of reed-solomon and algebraic-geometric codes, inProceedings 39th
Annual Symposium on Foundations of Computer Science (Cat. No. 98CB36280)(IEEE, 1998) pp. 28–37.
[56] R. Koetter and A. Vardy, Algebraic soft-decision decoding of reed-solomon codes, IEEE Transactions on Information
Theory 49, 2809 (2003).
[57] D. E. Knuth,The Art of Computer Programming, Volume 4, Fascicle 3: Generating All Combinations and Partitions
(Addison-Wesley Professional, 2005).
[58] D. Maslov and B. Zindorf, Depth optimization of CZ, CNOT, and Clifford circuits, IEEE Transactions on Quantum
Engineering 3, 1 (2022).
Appendix A: Optimizing the number of trials of Extended Prange
Recall the optimization problem from Section IIIB
maximize P
 mX
i=1
Xi ≥ t
!
subject to Xi ∼ Ber(P[si])
mX
i=1
si ≤ B
0 ≤ si ≤ b
P(1|s) ≤ P(1|s + 1) (A1)
(A2)
Eq (A2) is hard to solve exactly for largem, b,and B, but using dynamic programming we can compute a tight
approximation. To compute this approximation we note that eq (A2) is invariant under permutations ofsi which
allows us to build the solution in any order we desire.
Before we describe our approach we note that any constructive that chooses thesi values iteratively faces the
problem of givens1 ··· sk choose the bestsk+1 which is a hard question since the sequence ofsi induce a probability
distribution and the set of probability distributions is intrinsically an unordered set. However, given our objective we
can impose a few ordering relations with various degrees of effectiveness.
