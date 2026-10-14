---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 11
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 11

The text below is a page-delimited extraction of the unchanged source PDF.

the remainderr i+1 =r i−1 −q iri. The process terminates whenr k+1 = 0, at which point the greatest
common divisor ofpandxequalsr k.
TheExtended Euclidean Algorithm (EEA)not only computes the GCD ofpandx, but also outputs
the modular inversex −1 modpwhenpandxare coprime. In addition to computing the sequencer i, it
also initializest 0 := 0 andt 1 := 1, and for each iterationi= 1,2, . . ., updatest i+1 =t i−1 +q iti after
obtainingq i =⌊r i−1/ri⌋. When the algorithm first encountersr k = 1, the modular inverse is given by
(−1)k−1tk modp.
When realizing the Extended Euclidean algorithm on a quantum computer to compute the modular
inverse ofxwith a prime moduluspofnbinary digits, the primary challenge lies in handling superpositions
ofx. The number of iterations required varies from 1 toO(n) depending on the input, implying that
a straightforward implementation would requireO(n) iterations. Each iteration involves divisions and
multiplications onn-digit numbers, leading to an overall gate complexity ofO(n 3).
In what follows, we describe the dedicated four-phase algorithm framework first proposed in [PZ03],
followed by our own algorithmic optimizations and the details of our optimized circuit implementation.
3.1 The four-phase algorithm framework
The four-phase algorithm framework was originally introduced in [PZ03]. It operates on six quantum
registers, denoted asr i−1,r i,t i−1,t i,q i, andℓ, where the first five registers correspond to the variables
used in thei-th iteration of EEA. To compute the quotientq i =⌊r i−1/ri⌋, the algorithm performs a
binary long-division procedure consisting solely of bit shifts and long additions or subtractions. The
algorithm proceeds through the following four phases:
•Phase 1.The register containingr i is repeatedly shifted left by one bit, while the shift counterℓ
is incremented at each step. This continues until the inequality 2 ℓri > ri−1 holds. Conceptually,
this phase determines the largest power of two by whichr i can be multiplied without exceeding
ri−1. Equivalently, after the loop terminates,ℓ 0 :=ℓ−1 gives the highest bit position in the binary
representation ofq i.
•Phase 2.The register containingr i is then shifted right by one bit per step, withℓdecremented
accordingly. At each step, the registers corresponding tor i−1 andq i are updated as
(ri−1 −q ′ri, q′)→

ri−1 −(q ′ + 2ℓqi,ℓ)ri, q′ + 2ℓqi,ℓ

,
depending on whetherr i−1 −q ′ri is at least 2ℓri. Hereq ′ denotes the current partial quotient, given
byq ′ = 2ℓ0 qi,ℓ0 + 2ℓ0−1qi,ℓ0−1 +···+ 2 ℓ+1qi,ℓ+1, representing the most significant bits accumulated
so far in the binary expansion
qi = 2ℓ0 qi,ℓ0 + 2ℓ0−1qi,ℓ0−1 +···+q i,0.
This iterative process ultimately yields the transformation
(ri−1,0)→(r i−1 −q iri, qi),
completing the computation ofq i.
11
