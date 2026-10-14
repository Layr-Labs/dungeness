---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 12
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 12

The text below is a page-delimited extraction of the unchanged source PDF.

•Phase 3.The register containingt i is shifted left by one bit per step, andℓis incremented
correspondingly. The registers associated witht i−1 andq i are updated as
(ti−1 +q ′′ti, q′)→

ti−1 + (q′′ + 2ℓqi,ℓ)ti, q′

,
where the update depends on the bit valueq i,ℓ ofq i. After each step,q i,ℓ is reset to 0, depending on
whethert i−1 + (q′′ + 2ℓqi,ℓ)ti >2 ℓti. Hereq ′ andq ′′ represent the most and least significant portions
of the quotient, respectively:
q′ = 2ℓ0 qi,ℓ0 + 2ℓ0−1qi,ℓ0−1 +···+ 2 ℓqi,ℓ, q ′′ = 2ℓ−1qi,ℓ−1 + 2ℓ−2qi,ℓ−2 +···+q i,0.
After completing all steps, the registers corresponding tot i−1 andq i are updated as
(ti−1, qi)→(t i−1 +q iti,0).
•Phase 4.Finally, the register containingt i is repeatedly shifted right by one bit, andℓis decre-
mented at each step. The process terminates onceℓ= 0.
Upon completion of all four phases, SWAP operations are applied between the register pairs cor-
responding to (r i−1, ri) (which is currently (r i+1, ri)) and the register pairs corresponding to (t i−1, ti)
(which is currently (ti+1, ti)), respectively. This completes one full iteration of the EEA implementation.
We emphasize that, during the execution of this four-phase algorithm, the correspondence between
the iteration index in EEA and the phase number may vary depending on the input valuex. In other
words, the algorithm’s internal progression through iterations and phases is input-dependent. To avoid
ambiguity in the subsequent descriptions, we use “step” to represent any sub-iteration occurring within
any phase of an EEA iteration. The example in Table 3 illustrates how the step status evolves for different
input values under this four-phase framework.
Although the sequence of step statuses differs for each inputx, the total number of steps required
to reach an indexksuch thatr k−1 = 1, rk = 0 can be bounded within the interval [4n,4⌈cn⌉] with
c= 3/log 2(2 +
√
3), as formally proven in Appendix A.1. This bounded-step property is crucial for
quantum implementation: it implies that a quantum circuit corresponding to one “step” can be repeated
at most 4⌈cn⌉<6.316ntimes to definitely obtain the modular inverse of any inputxin superposition.
Since each step involves arithmetic operations such as shifts, additions, and subtractions, which require
O(n) quantum gates, the overall gate complexity of the algorithm is reduced toO(n 2).
Keeping the above discussion in mind, the forward space-efficient EEA subroutine for computing the
modular inversex −1 modp, wherepis a prime represented withnbinary digits andx∈ {1,2, . . . , p−1},
is summarized in Algorithm 1. In this context: (i) the register allocation strategy is described in Section
3.2; (ii) Algorithm 3 provides the optimized stepwise iteration designed to minimize gate complexity and
ensure quantum reversibility, as further discussed in Sections 3.2 and 3.3; (iii) whenx > p/2, we run the
EEA onp−xinstead ofxand record this choice in the iteration-parity qubit.
3.2 Space-efficient algorithm by register sharing
In [PZ03], the authors introduced the concept ofregister sharing. The central idea of register sharing is
that, during the execution of the EEA, the sequence{r i}is monotonically decreasing while the sequence
12
