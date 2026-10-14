---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 3
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 3

The text below is a page-delimited extraction of the unchanged source PDF.

variant of Shor’s ECDLP algorithm based on residue-number-system arithmetic and compressed
projective-coordinate outputs. Their construction achieves the state-of-the-art asymptotic qubit
complexity among existing implementations, requiring only 3.12n+O( √n) logical qubits for an
n-bit prime field. However, this reduction in space comes at the cost of a sufficiently larger gate
count of eO(n4).
•In terms of gate complexity, Babbush et al. [BZG +26] reported substantially improved resource es-
timates for solving ECDLP of the curve secp256k1 using 1191 logical qubits and 2 26.27 Toffoli gates
in the space-optimized setting, or 1441 logical qubits and 2 25.94 Toffoli gates in the gate-optimized
setting. However, their circuit-level details are not publicly disclosed. Schrottenloher [Sch26] subse-
quently gave an explicit and reproducible point addition architecture with comparable performance
and slightly smaller Toffoli counts for secp256k1.
•In terms of circuit depth, Kim et al. [KJW +26] developed depth-optimized point-addition circuits
based on QCSA-based Montgomery multiplication and low-depth binary-EEA inversion. They
achieved the lowest circuit depth with adequate ancilla qubits. In terms of the product of qubit
count and full depth, their qubit-optimized version achieves a 37%–40% improvement compared to
the previous result by H¨ aner et al. [HJN+20].
In this work, we study the space complexity of ECDLP. In particular, our focus is the modular
inversion subroutine, which is the dominant source of workspace in affine-coordinate point addition. Our
goal is to answer the following question:
Can the quantum space requirements for solving the ECDLP be further reduced in practice?
1.1 Contributions
The idea of reducing the space complexity of quantum ECDLP algorithms can be traced back to Proos
and Zalka [PZ03], who introduced a register-sharing strategy and obtained an asymptotic space bound
of 5n+O( √n) for solving the ECDLP over ann-bit prime field. However, their analysis was given at a
high level of abstraction and did not provide explicit reversible circuit constructions or detailed resource
estimates; in particular, issues such as reversible implementation and ancilla management were not fully
addressed, and the approximate treatment of modular inversion introduces a fidelity loss ofO(n −1).
Our main contribution is to turn this low-space strategy into an exact and fully explicit circuit-
level construction. Since modular inversion is the dominant contributor to the overall space, we focus on
designing a more space-efficient reversible implementation of this component. Building on the algorithmic
framework and register-sharing idea of Proos and Zalka, we refine the representation of the EEA state,
introduce length registers and location-controlled arithmetic, and provide explicit circuit constructions
with detailed resource estimates. As summarized in Table 1, our construction achieves the best asymptotic
logical-qubit complexity reported so far for ECDLP in the standard quantum circuit model.
Second, we provide resource estimates for our quantum circuit implementation. Specifically, we show
that a modular inversion circuit can be implemented using at most 217n 2 +O(nlog 2 n) Toffoli gates
and 274n2 +O(nlog 2 n) CNOT gates. By integrating this modular inversion circuit into an affine point
3
