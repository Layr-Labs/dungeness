---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 4
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

4
techniques like Karatsuba multiplication [8, 9] and Itoh-Tsujii inversion [9, 10]). Crucially, we analyze the
classical hardness in this setting, confirming that the problem remains intractable against known classical attacks
like Prange’s algorithm [11] and a novel variant, the Extended Prange’s algorithm (XP), tailored for extension
fields.
2. Optimized Quantum Circuits for the Extended Euclidean Algorithm: We introduce two distinct
compilation strategies for the EEA, each achieving minimal qubit overhead while being tailored for different
algorithmic requirements. These strategies are general and shall offer substantial improvements for other quan-
tum algorithms utilizing the EEA, such as those in elliptic curve cryptography [12–14] and DQI with EEA-based
decoders for other codes like algebraic geometry codes [15] and RS codes with prime fields [4].
• For scenarios requiring explicit access to the Bézout coefficients, we present an improved synchronized
circuit for the classic Euclidean algorithm [12, 16]. By storing quotients in-place within shared registers
and merging arithmetic cycles, we deterministically achieve a leading-order space complexity of2nb qubits
and substantially reduce gate counts.
• For scenarios whereimplicit access is sufficient, we introduce the novelDialog representation. This data
structure records the execution trace of a constant-time EEA, allowing our circuits to capitalize on the
low gate costs of modern, division-free EEA algorithms [17] without incurring their typically large qubit
overhead [14, 18].
3. Holistic Reversible Reed-Solomon Decoder Design:We construct end-to-end reversible quantum circuits
for the full RS decoder that integrate our optimized EEA modules. Our design is compatible with both the
explicit and implicit EEA approaches and fully accounts for the resource costs of the subsequent decoding
stages—Chien Search and Forney’s algorithm—when operating on the compact, shared-register data structures
produced by our EEA implementations.
We synthesize these techniques to construct end-to-end quantum circuits and provide detailed resource estimates
using Qualtran [19]. Our results demonstrate that classically intractable instances of OPI (requiring> 1023 classical
trials) can be solved with modest quantum resources. For instance, an(m = 4095, n= 70, b= 12) instance requires
approximately 5.72 × 106 Toffoli gates and 1885 logical qubits. This is roughly 1000x fewer Toffolis than that
required for factoring 2048-bit RSA integers [20], suggesting that DQI may offer a compelling near-term path to
practical, verifiable quantum advantage in optimization. We also provide a physical resource estimate showing that
the (m = 4095 , n= 70 , b= 12) OPI instance can be solved using eight hundred thousand physical qubits and1
hour of runtime under standard assumptions for superconducting architectures: a square grid of qubits with nearest
neighbor connections, a uniform gate error rate of 0.1%, a surface code cycle time of 1 microsecond, and a control
system reaction time of 10 microseconds.
II. METHODS FOR OPTIMIZED IMPLEMENTATION
We begin by presenting an improved, space-efficient construction of the DQI quantum circuit. We then present new
techniques for compiling the Extended Euclidean Algorithm (EEA) for the two regimes—first, where one needs to
explicitly compute the Bézout coefficients in memory, and second, where an implicit access to the Bézout coefficients
is sufficient. For both scenarios, our goal is to find a construction that minimizes the qubit counts. For the first case,
we make several improvements to the classical reversible EEA construction by [12, 16], resulting in lower qubit and
gate counts. For the second case, we first formalize the idea of having implicit access to the Bézout coefficients and
show how one can take advantage of the low gate counts for constant-time division-free variants of EEA [17, 21] while
avoiding the high ancilla overhead. In both cases, we achieve the theoretical minimum leading order space complexity
of 2nb + O(log2(n)). We believe these improved techniques for compiling the Extended Euclidean Algorithm will
be useful beyond DQI, especially in the context of Elliptic Curve Cryptography [14, 22]. We then specialize the
discussion to the Optimal Polynomial Intersection (OPI) problem over binary extension fields, motivated by the fact
that arithmetic circuits over binary extension fields are significantly cheaper to compile. In the end, we show how the
decoding problem for Reed-Solomon codes can be solved using the Extended Euclidean Algorithm, along with other
subroutines like Chien Search [23] and Forney’s algorithm [24]. We present optimized quantum circuits to account for
the cost of these subroutines. Table II provides a reference for the key parameters used throughout our analysis.
