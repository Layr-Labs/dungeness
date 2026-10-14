---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 14
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 14

The text below is a page-delimited extraction of the unchanged source PDF.

{ti}is monotonically increasing. This complementary behavior allows both values to occupy the same
quantum register at different stages of computation, thereby reducing the overall space requirement. The
identity
ri−1ti +r iti−1 =p
implies that two quantum registers, each consisting of (n+ 2) qubits, are sufficient: one to store the pair
(ri−1, ti) and the other to store (r i, ti−1).
We extend this register-sharing idea further. Specifically, we observe that a single quantum register
of (n+ 2) qubits can be used to store the triple (r i−1, ti, qi) simultaneously, including the intermediate
states that arise during phases 2 and 3 of the algorithm. These phases are responsible for computing
qi =⌊r i−1/ri⌋and updating the variables
ri−1 ←r i−1 −q iri, ti−1 ←t i−1 +q iti.
The detailed allocation of quantum registers is described as follows, and illustrated in Figure 4.
•Work1register (of(n+ 3)qubits).The left-mostℓ t + 1 qubits encode the valuet:=t i in little-
endian order (here we append a zero to the rightmost position oftin order to simplify the circuit
implementation). The followingℓ q qubits store the intermediate quotient valueq:=q ′ (only the
effective most significant bits) in phases 2 and 3, in big-endian order. The remaining qubits hold
the valuer:=r i−1 (or its updated formr:=r i−1 −q ′ri) in big-endian order.
•Work2register (of(n+ 3)qubits).The right-mostℓ r′ qubits storer ′ :=r i in big-endian order,
while the remaining qubits store the valuet ′ :=t i−1 (and its intermediate updatet ′ :=t i−1 +q ′′ti)
in little-endian order. During phases 2 and 3, this register may be circularly shifted left byℓ s
positions. In such cases, the valuet ′ may span both ends of the register, effectively splitting into
two contiguous parts.
•Lengthregisters.Four auxiliary registers are used to manage variable-length storage. Each of
them contains⌊log 2 n⌋+ 1 qubits. They store the length indicatorsℓ t, ℓq, ℓr′, and the shift counter
ℓs respectively. TheseLengthregisters mark the logical boundaries within theWork1andWork2
registers and enable coherent manipulation of superposed inputs of varying lengths.
•Controlregisters.Two single-qubitPhaseregisters indicate the current phase of the four-phase
algorithmic framework, and one single-qubitIterregister that records the parity of the current
EEA iteration number. Additionally, there are two auxiliary single-qubit registers,SignandCtrl,
used for intermediate flag and control operations.
We next describe the behavior of the system when performing comparison, addition, and subtraction
operations on the register pairs (r, r′) and (t, t′). The arithmetic betweenrandr ′ is relatively straight-
forward: a left shift byℓ s positions corresponds to multiplyingr ′ by 2ℓs. In contrast, the arithmetic
involvingtandt ′ requires a more careful interpretation. A convenient way to view this operation is
that a left shift ofℓ s positions can be regarded as dividingt ′ by 2ℓs, where the integer part is placed
in the left-most portion ofWork2, and the fractional part occupies the right-most portion. Whentis
added to the integer part oft ′ (which is properly aligned), the arithmetic relation can be expressed as
14
