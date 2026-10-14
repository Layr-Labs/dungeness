---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 4
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

not. When a series of quantum transformations are applied to a quantum system, it results in a
unitary transformationU being performed on the system. So long as no measurements are taken,
the original state of the quantum system can be restored from the final state by applying the
inverse U† [23]. Thus measurement-free quantum computation must be reversible. This means
that implementing classical algorithms using a quantum computer often implicitly involves the
additional step of making the algorithm reversible.
Reversible computation is also important when considering energy-efficient classical compu-
tation. Thermodynamics gives computation an energy lower bound ofkT ln 2 per irreversible
step—a barrier that can be circumvented by making computation reversible [24, 25]. Unfor-
tunately, all known general techniques for converting irreversible algorithms to reversible ones
feature an asymptotic time or space overhead [9, 26, 27, 28]. In fact, relative to random ora-
cles there is a provable separation between time-space trade-offs for reversible and irreversible
computation [29].
Of the strategies for making classical computation reversible, the most widely used method is
the reversible pebble game [9]. In the reversible pebble game, steps of an irreversible algorithm
are simulated reversibly by placing and removing pebbles on a line, or more generally, any
directed acyclic graph (DAG). The largest number of pebbles placed at any time corresponds
to the space needed for the simulation and the number of steps corresponds to the time of the
simulation.
Uncomputation Recycling space is key to space efficiency. But while irreversible algorithms
can simply erase values whenever they are no longer needed, such values require more care to
dispose of in reversible and quantum computation. In order to erase a value in a reversible
manner, it is necessary to end up in a state where it would be possible to efficiently recompute
the deleted value. Thusuncomputation, the reversible analog of deletion, requires access to the
same information needed to compute the deleted value. The importance of uncomputation in
quantum circuits it twofold: (1) qubits are an expensive resource for quantum algorithms so it
is important to design them so that they can run on as few qubits as possible and (2) failing
to uncompute values in a quantum circuit results in entangled garbage that prevents desired
interference patterns [30].
We say a quantum circuituncomputes a functionf if it can perform the following mapping
on any quantum state where thexi are all distinct:
∑
i
αi|xi⟩|f(xi)⟩→
∑
i
αi|xi⟩|0⟩
Note that the standard unitaryUf for computing f, which mapsUf |x⟩|b⟩= |x⟩|b⊕f(x)⟩is
also a unitary that uncomputesf. Carefully balancing computation and uncomputation is vital
for designing space and time efficient quantum algorithms.
Ghosting Gidney points out that full uncomputation is not always necessary for recycling
qubits when simulating classical algorithms in superposition. Instead of full uncomputation, he
developed a clever scheme using intermediate measurements to “compress” qubits into classical
bits [11]. We say that a quantum circuitC ghosts a register if it can perform the following
mapping on any quantum state where thexi are all distinct:
∑
i
αi|xi⟩|yi⟩ C− →
∑
i
αi(−1)b·yi |xi⟩|0⟩
and b is a classical bitstring returned by the circuit. In [11] Gidney calls this(−1)b·yi phase
a ghost of y, as the logical value of this register has been erased and replaced with a phase.
4
