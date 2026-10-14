---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 49
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 49

The text below is a page-delimited extraction of the unchanged source PDF.

Thus, ifc= 0, the accumulator bit remainsB i; ifc= 1, it becomesB i ⊕A i ⊕γ i, which is exactly
thei-th sum bit. Finally, a CNOT from the carry wire to the addend wire restoresA i ⊕γ i 7−→Ai.
Therefore, the controlled writing of thensum bits contributes preciselynadditional Toffoli gates.
In addition, after the forward sweep the final carryγ n is copied into the overflow flag only when
c= 1, using one more CCX gate,
f←−f⊕cγ n.
Hence this controlled variant of ripple-carry adder costs 3n+O(1) Toffoli gates.
LetS=B+cA, then after the first step the accumulator contains
eB=Smod 2 n,
and the overflow bit
h=⌊S/2 n⌋
has been XORed into the flag. SinceA, B old < p <2n, we haveS≤2p−2<2 n+1, soh∈ {0,1}.
The true reduction condition isS≥p. Ifh= 0, then eB=S, so this condition is exactly [ eB≥p].
Ifh= 1, then reduction is certainly needed, while eB=S−2 n < p, so [ eB≥p] = 0. Hence the
reduction bit is
r=h⊕[ eB≥p].
We therefore update the flag by XORing in the fixed-modulus comparison [ eB≥p], which is evalu-
ated by the classical-quantum comparator from [Gid25]. Here we use the dirty-assisted adder which
costs 3n+O(1) Toffoli gates by borrowing the non-target registerAas dirty workspace. Controlled
on this flag, we subtract the fixed moduluspfromB, again using the same Gidney-style controlled
classical–quantum subtractor, with cost 3n+O(1). Finally, after the correction, the flag can be
uncomputed by one Toffoli gate applying
f←f⊕c[B final < A].
[Bfinal < A] can be evaluated using the high-bit-only Cuccaro quantum comparator, derived from
the Cuccaro ripple-carry adder [CDKM04], costing 2n+O(1) Toffoli gates. All clean and borrowed
dirty workspace, including the flagf, is restored at the end of the block.
Therefore, one controlled modular addition costs
Tadd(n) = (3n+O(1)) + (3n+O(1)) + (3n+O(1)) + (2n+O(1)) = 11n+O(1)
Toffoli gates.
•Modular doublings.For modular doubling, we follow the implementation from [RNSL17]. The
binary doubling itself is implemented by Clifford shift/CNOT operations. Sincepis odd, the
reduction flag can be cleared from the least significant output bit. The only parts that require
Toffoli gates are one fixed comparison withpand one conditional fixed subtraction, which can be
implemented by the same classical-quantum adder from [Gid25].
Therefore, one modular doubling costs
Tdbl(n) = (3n+O(1)) + (3n+O(1)) = 6n+O(1)
Toffoli gates.
49
