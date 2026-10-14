---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 10
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 10

The text below is a page-delimited extraction of the unchanged source PDF.

on the exponent registers can be replaced by a semiclassical variant [GN96]. This semiclassical Fourier
transform performs measurements during the computation, reusing qubits and applying conditional phase
rotations based on previously observed outcomes. The overall quantum circuits of Shor’s algorithm for
ECDLP using QFT (resp. semiclassical QFT) are shown in Figure 2 (resp. Figure 3).
|0⟩ H • ··· ···
QFT2n+1
|0⟩ H • ··· ···
...
...
...
|0⟩ H ··· • ···
|0⟩ H ··· • ···
QFT2n+1
|0⟩ H ··· • ···
...
...
...
|0⟩ H ··· ··· •
|O⟩ /2n +[20]P +[21]P ··· +[2n]P +[20]Q +[21]Q ··· +[2n]Q
Figure 2: The overall quantum circuit of Shor’s algorithm for solving ECDLP using QFT. The qubits,
from top to bottom, correspond to the exponent registers containingkandℓin Equation 2 (ordered from
lower-order bits to higher-order bits), and to the register that stores the elliptic curve point accumulator.
µ0 µ1 µ2n+1
|0⟩ H • H |0⟩ H • Rθ1 H ··· |0⟩ H • Rθ2n+1 H
|O⟩ /2n +[20]P +[21]P ··· +[2n]Q
Figure 3: The overall quantum circuit of Shor’s algorithm for solving ECDLP using semiclassical QFT.
The gatesR θi denote rotation gates with rotation angleθ i = Pi−1
j=0 2i−jµj, where the valuesµ j ∈ {0,1}
are outcomes obtained in previous measurements. By employing the semiclassical QFT, the exponent
register requires only a single qubit, resulting in a reduction of 2n+ 1 qubits compared to the standard
implementation.
3 Space-Efficient Extended Euclidean Algorithm
As discussed in previous sections, the dominant cost in designing quantum circuits for solving ECDLP via
Shor’s algorithm arises from coherent group additions on elliptic curve points. Among these operations,
modular inversion is the most resource-consuming component. In this section, we present a space-efficient
and reversible algorithm for modular inversion based on the Extended Euclidean Algorithm. This design
is suitable for further translation into a quantum circuit, as detailed in Section 4.
Suppose thatp > xare two positive integers. The well-knownEuclidean algorithmcan be used to
compute the greatest common divisor (GCD) ofpandx. The algorithm initializesr 0 :=pandr 1 :=x,
and for iterationsi= 1,2, . . ., it repeatedly dividesr i−1 byr i to obtain the quotientq i =⌊r i−1/ri⌋and
10
