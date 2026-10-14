---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 7
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 7

The text below is a page-delimited extraction of the unchanged source PDF.

circuit.
We note that mid-circuit measurements have previously been used to reduce either the qubit count or
theT-gate cost of quantum arithmetic circuits [Gid19, KSS25, LMNS25, KH21]. In particular, the lowest-
qubit quantum algorithm currently known for the elliptic-curve discrete logarithm problem also makes
extensive use of measurements to reduce the number of qubits [CFS26]. That work does not keep the full
elliptic-curve point, nor does it reduce the index registers using a semiclassical Fourier transform. Instead
of computing the full point, it computes a one-bit Legendre symbol from the projective coordinates of
that point using residue-number-system arithmetic. Its measurements are used to release intermediate
nodes in a spooky pebbling strategy for a binary tree [Gid19, KSS25]. In contrast, we keep the standard
affine point-addition structure and use measurements only inside the in-place division and multiplication
blocks, where they recycle a register needed as workspace for running the inverse EEA circuit.
Resource estimations (Section 6).Putting everything together, we quantify the space complexity
and gate costs of the complete construction of Shor’s ECDLP circuit. We first show in Section 6.1 that
the modular inversion circuit requires 2n+6⌊log 2 n⌋+19 logical qubits, and that the affine point addition
circuit of Section 5 can therefore be implemented using 3n+ 6⌊log 2 n⌋+ 19 logical qubits. Section 6.2
then combines the per-block gate costs (Section 4.4) with the step-dependent active-window bounds
(Section 4.2), to obtain an upper bound of 217n 2 +O(nlog 2 n) Toffoli gates and 274n 2 +O(nlog 2 n)
CNOT gates for modular inversion, as well as an upper bound of 1003n 2 +O(nlog 2 n) Toffoli gates for
one affine point addition.
We complement these asymptotic bounds with concrete circuit generation and blockwise compilation
using Qiskit in Section 6.3, reporting numerical Toffoli and CNOT gate counts for prime-field sizes
ranging from 64 to 512 bits. Finally, in Section 6.4, we incorporate signed-window scalar multiplication
and the associated table look-ups into the complete Shor’s ECDLP circuit. This yields an overall Toffoli
complexity of 1008n 3/log 2 n+O(n 2).For thesecp256k1curve, our construction requires 835 logical
qubits and 230.88 Toffoli gates.
1.3 Open questions
Our work leaves several open questions for future investigation:
•Gate-count optimization.Our construction prioritizes logical-qubit efficiency and gives ex-
plicit reversible circuits for all arithmetic components. However, several building blocks, especially
location-controlled arithmetic, length-register updates, and controlled modular operations, may still
admit substantial improvements of their gate counts.
•Depth analysis and space-depth trade-offs.This paper focuses primarily on the number of
logical qubits and Toffoli/CNOT gate counts, and does not provide a detailed analysis of circuit
depth. A natural next step is to study the depth of our modular inversion and point-addition
circuits, identify which parts of the computation can be parallelized, and quantify the resulting
trade-offs between space, gate count, and depth.
7
