---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 35
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 35

The text below is a page-delimited extraction of the unchanged source PDF.

Qiskit subblocks, including constant-coordinate updates, controlled modular additions and subtractions,
modular doubling and halving, and the shared-register EEA wrapper. We then assemble larger arith-
metic blocks from these counted components with their exact multiplicities. For example, a modular
multiplication block containsncontrolled modular additions andn−1 modular doublings, while its in-
verse containsncontrolled modular subtractions andn−1 modular halvings. The squaring block reuses
the same multiplication count and adds the explicit CNOT cost for copy and uncompute. This yields a
complete compiled gate count for the point-addition circuit while preserving the block multiplicities.
In addition to compiling and counting the reusable subblocks, we apply a local template-based op-
timization before each subblock count is stored and reused. The optimizer performs local cancellation
and Qiskit template replacement on small reversible segments. To make the template identities directly
applicable, we restrict these segments to the gate library{X,CX,CCX}. A rewritten segment is accepted
only if its gate count does not increase.
To improve efficiency and preserve the circuit structure, we apply the optimization segment by seg-
ment. We scan each decomposed subblock linearly and collect consecutiveX, CX, and CCX gates into
one reversible segment. When the scan reaches any other instruction, the current segment is optimized,
the out-of-library instruction is counted directly, and a new segment is started. Thus, in circuits with mea-
surements and feed-forward phase corrections, these operations are not rewritten. They simply separate
the neighboring reversible segments. If a segment exceeds the runtime limits, it is counted unchanged.
To validate the implementation, we developed test suites for both the modular-inversion and point-
addition circuits. The tests include representative examples over prime fields withpranging from small
values such asp= 3 to 512-bit primes, and with circuit widthsnranging up to 512. They additionally
verify register layouts, circuit schedules, arithmetic sub-blocks, and compiled block assembly.
The corresponding circuit implementation is included in our open-source codebase.2 For each problem
sizen, we generated the full circuit instance up to the theoretical upper bound on the number of cycles
derived in this work, transpiled it into theCCX,CX, andXbasis, and recorded the resulting gate counts.
We report results forn∈ {64,128,160,192,224,256,384,512}. The numerical values are listed in Table 6.
n Modular inversion Point addition
Toffoli (×106) CNOT (×10 6) Toffoli (×106) CNOT (×10 6)
64 2.41 3.32 5.39 7.98
128 8.47 11.82 19.17 28.97
160 12.63 17.80 28.75 43.92
192 17.70 25.04 40.41 62.05
224 23.57 33.43 53.96 83.99
256 30.59 43.39 70.10 108.09
384 65.97 94.31 152.00 237.44
512 115.81 165.63 267.27 416.32
Table 6: Gate counts for modular inversion and point addition circuits overn-bit prime fields.
2GitHub repository: https://github.com/ZeroWang030221/Space-Efficient-Quantum-Algorithm-for-Elliptic-Curve-
Discrete-Logarithms-with-Resource-Estimation
35
