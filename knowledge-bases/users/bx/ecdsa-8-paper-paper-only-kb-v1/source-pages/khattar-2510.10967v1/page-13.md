---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 13
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 13

The text below is a page-delimited extraction of the unchanged source PDF.

13
• As a result of the subtraction and a subsequent logical right-shift ofb(z), the rightmostb qubits of the
register (previously holdingb0) become free.
• This newly freed block ofb qubits is immediately removed from the poly register and appended at the
end of the dialog register, thus immediately re-purposing to store the computed coeff, which is the next
element of the Dialog.
Crucially, at any intermediate step i of the algorithm, the poly and dialog registers contain a complete, holistic
representation of the EEA’s state. The growing dialog register holds the partially constructed Dialog (from step
1 to i), while the shrinking poly register holds the coefficients of the current remainder polynomials,ri−1(z) and ri(z).
From these two registers of total size2nb, one can always reconstruct the full mathematical state: the remainders are
available directly, and the corresponding Bézout coefficients,ui(z) and vi(z), can be computed by playing back the
partial Dialog. After the full2n iterations, the original polynomials have been completely reduced, and the Dialog
has expanded to occupy the entire2nb qubits. The final state of the system is the complete Dialog, from which
the gcd and the final Bézout coefficients can be derived implicitly. This in-place architecture, detailed in Fig. 11 of
Appendix F, successfully constructs the full Dialog representation using a leading-order qubit cost of only2nb.
C. Optimal Polynomial Intersection (OPI) over binary extension fields
While the original DQI paper focused on the Optimal Polynomial Intersection (OPI) problem over prime fieldsFp,
we now study the problem defined over binary extension fields, GF(2b). The primary motivation for this is the prospect
of substantially more efficient quantum circuits. Arithmetic in fields of characteristic 2 is often less resource-intensive
to implement on a quantum computer. For instance, addition is a simple bitwise XOR, implementable with a linear
number of CNOT gates. Quantum-Classical multiplication and Squaring are linear reversible circuits that can also
be implemented using only the CNOT gates. Quantum-quantum multiplication based on Karatsuba algorithm [8]
uses O(blog2 3) Toffoli gates,O(b2) CNOT gates, and no ancilla. Inversion can be reduced to onlyO(log2 b) quantum-
quantum multiplications, resulting in low Toffoli counts [10, 36]. Appendix C details our optimized implementations
of arithmetic circuits forGF(2b). This reduction in the cost of the underlying field arithmetic translates directly to
lower resource requirements for the overall DQI algorithm.
The OPI problem and the DQI algorithm generalize naturally to this setting, as discussed in [4, Section 14]. The
problem can be stated analogously:
Definition II.1 (OPI over GF(2b)). Let q = 2b. Given integersn < q− 1, an instance of the Optimal Polynomial
Intersection problem over GF(2b) is as follows. For each non-zero elementy ∈ F∗
q, letFy be a subset of the finite field
Fq. The problem is to find a polynomialQ ∈ Fq[y] of degree at mostn − 1 that maximizes the objective function:
fOPI (Q) = |{y ∈ F∗
q : Q(y) ∈ Fy}|
For a general OPI instance, the subsetsFy can be arbitrary. As described in Section IIA, implementing the DQI
algorithm requires constructing constraint-encoding gatesGi that prepare a superposition related to these sets. For
an arbitrary setFy, this step would require a generic quantum state preparation, costing roughlyO(q) gates for each
of them constraints.
To reduce the gate cost of the constraint encoding step while maintaining the classical hardness of the problem,
we focus our resource analysis on a specific, structured variant of OPI where the setsFy are chosen to allow for
highly efficient implementations of theGi gates. Specifically, we introduce and analyze theTwisted Bent Target
OPI (Definition III.5). In this variant, the setsFy are constructed from Maiorana-McFarland bent functions. This
structure ensures that each gateGi can be implemented with a gate cost that scales asO(log q) rather thanO(q).
D. Decoding Reed Solomon Codes using the Extended Euclidean Algorithm
Having developed efficient quantum circuits for the EEA under both explicit and implicit access models, we now
apply them to the central challenge of our work: constructing a complete, reversible decoder for Reed-Solomon (RS)
codes. This decoder is the computational core of the DQI algorithm when applied to the OPI problem. Syndrome
decoding of Reed-Solomon codes addresses the problem of recovering an error patterne = [e0, e1, . . . , em−1], where
each ei ∈ Fq and the number of non-zero errors|e| is at mostℓ. The input to the decoder is a list of known syndromes,
which are represented as the coefficients of a syndrome polynomial,S(z) = s0 + s1z + ··· + sn−1zn−1. The full
decoding procedure involves three main stages: first, solving thekey equation using the EEA; second, finding the
error locations using a Chien search; and third, finding the error values using Forney’s algorithm.
