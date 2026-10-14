---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 6
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 6

The text below is a page-delimited extraction of the unchanged source PDF.

that guarantees a deterministic register bound for all inputsx∈F p. This reduces the additional space
overhead toO(logn) while preserving exact correctness.
Finally, starting from a baseline reversible realization of this space-efficient EEA, we introduce a se-
quence of algorithmic optimizations in Section 3.3 that reorganize the update rules and eliminate redun-
dant arithmetic operations. We provide complete pseudocode (Algorithm 3) together with representative
classical execution traces (Table 4), which illustrate the reversibility and correctness of each step and
clarify how the procedure can be translated into a quantum circuit.
Explicit quantum circuit construction for modular inversion (Section 4).To show that our
modular inversion algorithm admits an explicit quantum circuit implementation, we present a detailed
construction based on Algorithm 3. We begin with the overall circuit architecture (Figures 5 and 6 in
Section 4.1), where location-controlled operations arise as key non-standard components.
Before giving their explicit implementations, we establish the necessary tools. In Section 4.2, we
introduce step-dependent active windows, which restrict the relevant index range at each step and thereby
reduce gate complexity. We then introduce unary iteration (Section 4.3) as a primitive for implementing
controlled indexed operations, which enables the realization of these location-controlled components.
Finally, in Section 4.4, we present explicit constructions of the location-controlled circuit blocks,
including swap, addition/subtraction, and length-update operations (Figures 9, 10, 12, and 13). In
addition to the circuit diagrams, we provide detailed explanations of the underlying techniques and
design rationale.
Affine point addition with mid-circuit measurements (Section 5).We further show that affine
point addition can be implemented using our EEA inversion circuit with only 3n+O(logn) logical qubits
by allowing mid-circuit measurements and classical feed-forward operations. The main issue is the in-place
division step
|x⟩X|y⟩Y |0⟩A 7−→ |x⟩X|y/x⟩Y |0⟩A.
To perform this map, the EEA inversion circuit in Equation (1) is first applied tox. This requires one
cleann-qubit registerAand leaves the forward EEA state Γ(x) to be cleared later. After the quotient
y/xhas been written intoA, however, the registerAis no longer clean, so the inverse EEA circuit has
no availablen-qubit workspace.
As shown in Figure 15, we resolve this problem by measuring the register containing the old value
yin the Hadamard basis and resetting it to zero. This makes the registerYavailable as the clean
workspace for the inverse EEA circuit, which recoversxand clears Γ(x). This measurement is valid
because, aftery/xhas been written intoA, the old valueyis redundant and can be recovered fromxand
y/x. Measuring|y⟩in the Hadamard basis gives a uniformly random outcomeb∈ {0,1} n, and the only
effect on the remaining registers is the phase (−1) b·y. Thus measuring the registerYdoes not destroy
coherence. The phase is removed by recomputingyfromxandy/x, applying the corresponding Pauli
Zcorrections, and uncomputing the recomputation. The same measurement and correction procedure
gives an in-place multiplication circuit. Consequently, affine point addition can be implemented using
threen-qubit registersX,Y, andA, together with theO(logn) auxiliary qubits required by the EEA
6
