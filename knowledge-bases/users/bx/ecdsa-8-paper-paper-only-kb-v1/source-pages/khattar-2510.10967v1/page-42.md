---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 42
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 42

The text below is a page-delimited extraction of the unchanged source PDF.

42
Lemma D.2(PEEA Constraints). The variables are constrained byk ≤ Dk and k ≤ Sk. For Full PEEA (coprime
inputs, unequal degrees),Dk = n and Sk = n.
We analyze the time complexityTi of iterationi based on the 5 steps described in Fig. 9.
Lemma D.3(Cost Per Iteration). The number of cyclesTi required for iterationi in the optimized implementation
is Ti = 2di + si + di−1 + 2.
Proof. We analyze the time required for each stage in the 4-stage cycle, corresponding to Steps 1-4 in Figure 1:
1. Stage 1(Step-1, Poly Long Division): Time taken is the length ofQi (number of terms), which isdi + 1.
2. Stage 2(Step-2, Remainder Normalization): Time taken is the total degree reductionsi.
3. Stage 3(Step-3, Bézout Cofactor Alignment): Time taken is the degree growth from the prior iteration,di−1.
4. Stage 4(Step-4, Bézout Cofactor Update): Time taken is the length ofQi, which isdi + 1. The register swap
(Step-5) occurs concurrently during the final cycle of this stage, incurring no extra time.
Summing the costs for iterationi:
Ti = (di + 1) +si + di−1 + (di + 1)
= 2di + si + di−1 + 2.
Lemma D.4(Total Cost Function). The total number of cyclesT required to completek iterations isT = 3Dk +
Sk − dk + 2k.
Proof. The total time is the sum ofTi from i = 1 to k.
T =
kX
i=1
Ti =
kX
i=1
(2di + si + di−1 + 2)
= 2
kX
i=1
di +
kX
i=1
si +
kX
i=1
di−1 + 2k.
We evaluate the third term:Pk
i=1 di−1 = d0 + d1 + ··· + dk−1. Since d0 = 0, this equalsDk − dk.
T = 2Dk + Sk + (Dk − dk) + 2k = 3Dk + Sk − dk + 2k.
1. Worst-Case Analysis: Full PEEA (GCD)
We analyze the maximum cycles required for the Full PEEA, assuming worst-case coprime inputs with degrees
(n, n− 1).
TheoremD.5 (CycleBoundforFullPEEA) . Themaximumnumberofcyclesrequiredfortheoptimizedsynchronized
Full PEEA on inputs of unequal degrees (max degreen) isTmax = 6n − 1.
Proof. We maximize the cost functionT = 3Dk + Sk − dk + 2k. We use the constraints for Full PEEA (Lemma D.2):
Dk = n and Sk = n.
Substituting these values:
T = 3n + n − dk + 2k = 4n − dk + 2k.
To maximizeT, we maximize the number of iterationsk and minimize the final quotient degreedk. The constraints
are k ≤ n and dk ≥ 1. We setkmax = n and dk,min = 1.
Tmax = 4n − 1 + 2n = 6n − 1.
This worst case is achieved by the generalized Fibonacci sequence wheredi = 1 and si = 1 for alli = 1 . . . n.
