---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 40
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 40

The text below is a page-delimited extraction of the unchanged source PDF.

40
FIG. 6: PCTOF in terms of a Toffoli and PCNOTs and then expanded in terms of a Toffoli and CNOTs. Note that
we omitted the ancilla cleanup part.
straight Karatsuba multiplication [8]. We tune the implementation [9] to focus on optimizing an∞-to-1 weighted
sum of Toffoli and CNOT gate counts to utilize the PCTOF gates better. To get constructions made of the PCTOF
and CNOT gates, we start from the Toffoli and CNOT circuits from [9] and commute the CNOT gates to the left
while updating the sets of the PCTOF gates, resulting in circuits that start with three disjoint CNOT stages acting
on the two input registers and the resulting register followed by a circuit made of the PCTOF gates. The first two
CNOT circuits are equivalent to the identity since we do not modify the input registers and the CNOT circuit acting
on the target can be ignored since the target is always initialized in the zero state. The resulting optimized circuits
are summarized in Table VII. Fig. 7 shows theGF(23) multiplication circuit with irreducible polynomialx3 + x + 1
in terms of PCTOF gates and explicit circuit files are available as a part of the Zenodo upload of this paper.
In addition, we developed a circuit optimization method applicable to the kinds of circuits with PCTOF gates
considered. The optimization algorithm relies on two observations: first, any two PCTOF gates commute, and
second, each PCTOF gate computes a Boolean polynomial of degree 2 and then EXORs it onto a separate output
register. This means that a single PCTOF gate can be thought of as a vector in them2-dimensional Boolean space,
where each coordinate corresponds to a Boolean product of some two variables, and circuits withk PCTOF gates (with
targets on the bottom register such as in our case of GF multiplication circuits) can be thought of ask ×m2 matrices.
This means that the matrix rank determines the minimal number of PCTOF gates necessary, in a given set that
implements the desired functionality. We implemented this optimization algorithm and found a small optimization
compared to what is directly offered by [9] (compare Toffoli count to the PCTOF count in Table VII). We suspect
that the improvement is small due to the large number of optimizations that already went into [9].
3. Measurement-based Uncomputation for GF2 Multiplication.
The GF(2m) multiplication operation is an out-of-place operation that applies the transformation|x⟩|y⟩|0⟩ →
|x⟩|y⟩|xy⟩. The uncomputation of this operation can be done using only measurements andCZ gates.
The uncomputation starts by measuring the target register in theX basis. This is equivalent to applying theH⊗m
to the target register and then measuring in the computational basis. TheH⊗m operations transform the state to
|x⟩|y⟩|xy⟩ = Pai,j |i⟩|j⟩|ij⟩
H⊗m
− − − →1√
2m
P2m−1
c=0
P(−1)h(c,ij) |i⟩|j⟩

|c⟩ where h(a, b) is the Hamming weight of
a ⊕ b. After the measurement, we end up with a classical bitstringc and phase flips on some of the coefficients of the
input superpositionP(−1)h(c,ij)ai,j |i⟩|j⟩.
Whileitseemsthatweneedtoknowtheproducttocorrectthephase, thelinearityof h andsymmetryof CZ allowus
to correct the phase with onlyCZs. For example ifct=1 then we need to applyCZ(xi, yj) for all(i, j) pairs such that
xi+j mod p(x) has xt where p(x) is the irreducible polynomial. This leads to the requirement to implement a certain
CZ gate circuit. Note that any such circuit can be implemented in depth⌊m/2 + 0.4993·log2(m) + 3.0191·log(m) −
10.9139⌋, using no more thanm2/4 + O(m log2(m)) Clifford gates [58] orO(m2/ log(m)) gates asymptotically.
Our implementation of measurement-based uncomputation of GF2 multiplication is available in Qualtran [19] as
GF2MulMBUC and Fig. 8 shows the uncomputation of GF2 multiplication form=3 and irreducible polynomialx3 +x+1.
