---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 6
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 6

The text below is a page-delimited extraction of the unchanged source PDF.

Using this code, one can for example build the point addition circuit, simulate
it on random inputs and check that the error probability is small. We note that
for efficiency reasons, the simulation does not descend at the gate level. Instead
it replacesexactarithmetic circuits (addition, subtraction, comparison. . . ) by
their classical functions.
2 High-Level Structure
This section details the reduction from Shor’s algorithm for discrete logarithms
to thewindowed point additioncircuit on elliptic curves, and gives the high-level
structure of the circuit.
LetE(F q) be an elliptic curve defined over a prime field, whereqis a prime
number of bit-sizen(q <2 n). The curve is defined by an equationy 2 =x 3 +
ax+b. In particular, thesecp256k1curve uses:
q= 2 256 −4294968273, a= 0, b= 7.
A point on the curve inaffine coordinatesis either of the form (x, y), or the
point at infinityO. From an implementation perspective, these representations
can be unified by a triple (x, y, b)∈Fq ×Fq ×{0,1}whereb= 0 andx=y= 0 if
the point isOandb= 1 otherwise. Points on the curve form an additive group
whereOis the neutral element.
Quantum Circuits.We describe quantum algorithms in the quantum circuit
model. We refer to [17] for an overview, and assume familiarity with the notions
of gates, qubits, and the ket notation|·⟩of quantum states.
We focus on the optimization oflogicalquantum circuits, without taking
into account the error correction layer of fault-tolerant quantum architectures.
At the logical layer, we are interested in minimizing the number of logical qubits,
and the gate count, especially the non-Clifford gates, due to the higher difficulty
of implementing them in fault-tolerant quantum computing. In previous works,
Toffoli gates or T gates have been used as the main metric. In this paper, we
use circuits which contain Toffoli gates or AND gates, which are decomposed
differently in the Clifford+T gate set. Both are counted together as a single
“Toffoli gate” metric. These are the only non-Clifford gates in the circuits. Other
gates include not (X), controlled not (CX), Hadamard, phase flips (CZ).
All arithmetic circuits described in this paper can be efficiently simulated,
despite using specific quantum effects like measurement-based uncomputation.
Babbush et al. [2] notice this for their circuits, and describe a class of “kickmix”
circuits which operate using classical gates, phases and measurements. More gen-
erally, the property we require (which is satisfied throughout this paper) is that
simulating the circuit, starting from any valid input (a single basis state), pro-
duces a quantum state with a sparse support, having always at most a constant
number of basis states. With measurement-based uncomputation, like in [8], one
typically applies Hadamard gates followed immediately by measurements, so the
quantum state remains supported by two basis states only.
6
