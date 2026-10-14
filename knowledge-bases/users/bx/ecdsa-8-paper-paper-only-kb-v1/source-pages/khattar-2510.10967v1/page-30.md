---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 30
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 30

The text below is a page-delimited extraction of the unchanged source PDF.

30
(a) ZX graph for a Parity Control Toffoli gate, which computes the AND of the parity of two sets of control qubits and flips one more
target qubits. For the specific example, the Parity Control Toffoli flips 4 target qubits (on the right) based on
(x1 ∨ x2 ∨ x3 ∨ x4) ∧ (y1 ∨ y2 ∨ y3 ∨ y4). Here is quirk link that shows how a Parity Control Toffoli can be implemented by consuming 4|T⟩
states.
(b) Lattice surgery diagram for compiling two Parity Control Toffoli gates, each acting on two sets of10-qubit control registers (middle
and right) and one10-qubit target register (on the left). Green boxes correspond to Y basis initialization or measurement [53]. Gray boxes
correspond to the reaction time for decoder to process the measurement results. Pink boxes correspond to space available for magic state
cultivation [51]. Every|T⟩ state has3 × 2 × d3 spacetime available for cultivation. Withd = 21, this is enough to cultivate|T⟩ states with
a logical error rate of2 × 10−9. The space cost is3 × (2.5b + 9)and amortized time cost per Parity Control Toffoli is1.5d rounds.
FIG. 3: Lattice surgery compilation for two Parity Control Toffoli gates using magic state cultivation. See [52,
Figure 1] and Appendix C for more discussion on Parity Control Toffoli gates. Acts as a building block for compiling
quantum-quantum multiplication (GF2Mul) circuits for GF(2b).
