---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 1
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

Tight Bounds on the Spooky Pebble Game: Recycling
Qubits with Measurements
Niels Kornerup*1, Jonathan Sadun, and David Soloveichik*2
1Department of Computer Science, The University of Texas at Austin, United States of America
2Department of Electrical and Computer Engineering, The University of Texas at Austin, United States of America
Pebble games are popular models for analyzing time-space trade-offs. In particu-
lar, reversible pebble game strategies are frequently applied in quantum algorithms
like Grover’s search to efficiently simulate classical computation on inputs in super-
position, as unitary operations are fundamentally reversible. However, the reversible
pebble game cannot harness the additional computational power granted by interme-
diate measurements, which are irreversible. The spooky pebble game, which models
interleaved Hadamard basis measurements and adaptive phase corrections, reduces
the number of qubits beyond what purely reversible approaches can achieve. While
the spooky pebble game does not reduce the total space (bits plus qubits) complexity
of the simulation, it reduces the amount of space that must be stored in qubits. We
prove asymptotically tight trade-offs for the spooky pebble game on a line with any
pebble bound. This in turn gives a tight time-qubit tradeoff for simulating arbitrary
classical sequential computation when using the spooky pebble game. For example,
for allε∈(0,1], any classical computation requiring timeT and spaceS can be im-
plemented on a quantum computer using onlyO(T/ε) gates andO(TεS1−ε) qubits.
Thisimprovesonthebestknownboundforthereversiblepebblegamewiththatnum-
ber of qubits, which usesO(21/εT) gates. For smaller space bounds, we show that the
spooky pebble game can simulate arbitrary computation withO(T1+εS−ε/ε) gates
and O(S/ε) qubits whereas any simulation via the reversible pebble game requires
Ω(S·(1 + log(T/S))) qubits.
We also consider the spooky pebble game on more general directed acyclic graphs
(DAGs), capturing fine-grained data dependency in computation. We show that for
an arbitrary DAG even approximating the number of required pebbles in the spooky
pebble game is PSPACE-hard. Despite this, we are able to construct a time-efficient
strategy for pebbling binary trees that uses the minimum number of pebbles.
1 Introduction
Pebble games provide a convenient abstraction for reasoning about space and time usage in
computation. Pebble games were first used in [1] to determine optimal register allocation for
computing straight line programs. In [2] the authors applied the irreversible pebble game to show
that any computation running on a Turing machine in timeT(n) can be executed on another
∗Research supported by Schmidt Science Polymath award
Accepted inQuantum 2025-01-16, click title to verify. Published under CC-BY 4.0. 1
arXiv:2110.08973v3  [quant-ph]  6 Feb 2025
