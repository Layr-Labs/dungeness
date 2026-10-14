---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 5
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

Reference Type Qubits Toffolis
[BZG+26] Space-optimized for secp256k1 1175 2 26.27
Gate-optimized for secp256k1 1425 2 25.94
[Sch26] Space-optimized for secp256k1 1192 2 26.11
Gate-optimized for secp256k1 1446 2 25.78
[CFS26] Space-optimized for secp256k1 1098 2 38.10
This workSpace-optimized for secp256k1 835 2 30.88
Table 2: Comparison of the concrete costs of circuits for secp256k1.
Each elliptic-curve point addition is decomposed into reversible modular arithmetic operations, includ-
ing modular addition, multiplication, squaring, and division, etc. Among these, modular division is the
dominant contributor to the logical-qubit cost. Figure 14 illustrates the structure of our point-addition
circuit, where these operations are encapsulated as modular arithmetic blocks. In particular, the in-place
modular division block is realized by the circuit shown in Figure 15, which consists of a forward execution
of the extended Euclidean algorithm (EEA) for modular inversion, followed by its uncomputation.
We present each component from a top-down perspective as follows.
Space-efficient reversible algorithm for modular inversion (Section 3).Our modular inversion
procedure, based on the EEA, is designed to implement the following quantum transformation:
|x⟩X|0⟩A|0⟩S 7−→ |x−1 modp⟩ X|0⟩A|Γ(x)⟩S, x∈F ×
p ,(1)
whereAis ann-qubit workspace register,Sdenotes the remaining ancillary registers, and|Γ(x)⟩is the
forward EEA state retained for later uncomputation.
We first revisit the four-phase framework of Proos and Zalka [PZ03] (see Section 3.1), which is well
suited for quantum implementation because the number of iterations (which we refer to as steps) is linear
inn. Rather than relying on the (inaccurate) 4.5nupper bound stated in [PZ03], we establish a rigorous
bound showing that a complete execution of the EEA requires at most 4⌈cn⌉steps for every inputx, where
c= 3/log 2(2+
√
3). Specifically, we consider a different roadmap: instead of computing the upper bound
of step numberN, we fix the total number of steps and then compute the minimum possible value ofp.
To do this, we formulate the problem as finding a slowest growth pattern for products of matricesM(q)
with a fixed weight sumN/4 = Pm
i=1(d(qi) + 1).Motivated by the asymptotically extremal alternating
quotient pattern (1,2,1,2, . . .) whose normalized growth rate is (2+
√
3)1/3 per unit weight, we construct
a finite polyhedral antinorm certificate, following the lower spectral radius framework of [GP13], to prove
that every admissible quotient sequence grows at least this rapidly. Details can be found in Appendix A.1.
Section 3.2 then develops an explicit and refined register-sharing strategy at the algorithmic level. In
the original construction of [PZ03], a uniform register allocation is used to accommodate all inputsx∈F p
in superposition. This worst-case allocation incurs anO( √n) space overhead and necessitates truncating
rare outlier cases, introducing anO(n −2) fidelity loss. In contrast, we present an exact allocation scheme
5
