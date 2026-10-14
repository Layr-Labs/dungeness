---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 28
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 28

The text below is a page-delimited extraction of the unchanged source PDF.

28
B. Physical Costs
For estimating physical costs, we assume one large rectangular grid of physical qubits with nearest neighbor con-
nections, a uniform gate error rate of 0.1%, a surface code cycle time of 1 microsecond, and a control system reaction
time of 10 microseconds. With these assumptions, the imagined physical layout of the algorithm will consist of a
compute region using hot storage and a memory region using cold storage. The compute region will store logical
qubits “normally", as distanced surface code patches using2(d+1)2 physical qubits. The cold storage memory region
will store qubits more densely, by using 2D yoked surface codes [50]. Since our Toffoli gate counts are low enough,
magic state cultivation [51] will suffice to prepare|T⟩ states with low enough error rates, and thus we will not any
dedicated space for magic state factories.
As an example, let us look at compiling the instance(m = 4095, n= 70, b= 12). The dominant subroutines in the
decomposition of the circuit are primitives to do arithmetic over Galois Field, like quantum-quantum multiplication
(GF2Mul) and synthesizing a linear reversible circuit (SynthesizeLR) for quantum-classical multiplication and squar-
ing. For these two primitives, we provide hand optimized lattice surgery layouts in Fig. 4 and Fig. 2 with magic state
cultivation in-place.
Referring to [20, Figure 6], note that a distance 21 patch is sufficient for normal surface code patches to reach a
per-patch per-round logical error rate of10−13. So our hot patches will use2 · (21 + 1)2 = 968 physical qubits per
logical qubit. For the cold storage, again referring to [20, Figure 6], yoking with a 2D parity check code reaches a
logical error rate of10−13 when using350 physical qubits per logical qubit. So cold logical qubits will be roughly triple
the density of hot logical qubits. For(m = 4095, n= 70, b= 12), the algorithm uses1885 logical qubits. We propose
to allocate a40×48 cold storage region with1920 logical qubits using 2D Yoked Surface codes. We also propose a thin
3 × 40 = 120 qubit hot storage region. Our mockup for GF multiplication forb = 12 fits in a3 × (2.5b + 9) = 3 × 39
region, including ancilla patches and space needed for cultivation. Thus, our layout uses120×968+1920 ×350 ≈ 800k
physical qubits. A mockup of the high-level spacial layout is shown in Fig. 5.
Now let’s come to time. In the decomposition of logical circuit for(m = 4095, n= 70, b= 12), there are58215
calls to GF2Mul and687564 calls to SynthesizeLR. We define the Parity Control Toffoli gate as a generalization of
the Toffoli gate that computes the Boolean AND of the XOR of a subset of controls and updates a subset of targets
[52, Figure 1]; we employ such gates since they can be implemented efficiently using lattice surgery Fig. 3. Our
GF2Mul compilation from Fig. 4 requires1.5d rounds per Parity Control Toffoli gate (PCTOF). Forb = 12, using
optimized GF2 arithmetic circuits from Appendix C, there are51 PCTOF gates. Therefore, it takes1.5 · 51 ≈ 77d
rounds for one quantum-quantum multiplication of field elements. For SynthesizeLR, we present a hand-optimized
layout in Fig. 2 that takes10d rounds and 3 × 23 surface code patches forb = 12. Therefore, with d = 21, these
two combined give us58215 · 77 · 21 + 687564 · 10 · 21 = 2 .4 × 108. To provide a conservative estimate of the total
runtime, we multiply this number by a factor of four: doubling it once to account for overhead from other smaller
operations and routing, and doubling it a second time to account for the time needed to move qubits between cold
and hot storage. Thus, we estimate a total of1 × 109 rounds. We need to protect1920 + 120 = 2040 logical qubits
for a total of1 × 109 rounds. With an LER of 10−13, this gives us a no-logical-error shot rate ofplattice surgery =
(1 − 10−13)2040·1·109
= (1 − 10−13)2×1012
≈ 81.5% and a per shot runtime of 16 minutes. To account for error
due to cultivation, we cultivate|T⟩ states with a fidelity of2 × 10−9. For a total Toffoli count of5.72 × 106, this
gives us apcultivation = (1 − 2 × 10−9)4×5.72×106
≈ 95.5%. Combining the two success probabilities above, we have
a per-shot success rate ofpcultivation × plattice surgery ≈ 77.9%, which means about 4 retries are sufficient for boosting
the probability of a successful shot close to 1. Therefore, the total runtime would be≈ 1 hour.
To summarize, we estimate that solving a classically intractable instance of the OPI problem using DQI requires
≈ 800k physical qubits and≈ 1 hour of runtime. This estimate assumes a quantum computer with a surface code
cycle time of 1 microsecond, a control system reaction time of 10 microseconds, a square grid of qubits with nearest
neighbor connectivity, and a uniform depolarizing noise model with a noise strength of 1 error per 1000 gates.
