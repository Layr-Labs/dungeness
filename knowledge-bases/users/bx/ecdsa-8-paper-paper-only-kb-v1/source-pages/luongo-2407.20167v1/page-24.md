---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 24
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 24

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. Using QADD = IQFTn+1ΦADD(a)QFTn+1 and QSUB = IQFTn+1ΦSUB(a)QFTn+1 in theo-
rem 2.35, we require only a single ancilla.
Definition 2.37 (Controlled comparison by a classical constant) . We define a controlled quantum
comparator with a classical constant a ∈ {0, 1}n as any unitary gate implementing the n strings
comparison with a according to the following circuit
|c⟩1 |c⟩1
|x⟩n ·< a |x⟩n
|t⟩1 |t ⊕1[x < c·a]⟩1
Theorem 2.38 (Controlled comparator by a classical constant - CDKPM - using half a subtractor) .
There is a circuit implementing an n-bit controlled comparator by a classical constant as per
definition 2.37 using n + 1 ancilla qubits and 2n Tof gates
Proof. The previous statement follows by using a comparator with classical constant (proposi-
tion 2.34) and using an ancilla register for writing (controlled on the register |c⟩) the value of a
using |a| CNOTs, which gets uncomputed after using the comparator.
Remark 2.39. Given any circuit implementing the comparison (x > y) as defined in definition 2.24
one can get the opposite comparison (x ≤ y) by simply postcomposing the first circuit with an X gate
acting on register T.
3 Quantum modular addition
In this section, we detail and build on the methods of Vedral et. al [VBE96] for constructing
modular adders as a suitable combination of the circuits for addition, subtraction and comparison
introduced in section 2.
Definition 3.1 (Modular addition). Let x ∈ {0, 1}n, y∈ {0, 1}n be two bit strings, and p ∈ {0, 1}n
classically known with 0 ≤ x, y < p. We define a quantum modular adder as any unitary gate
implementing the n strings addition modulo p according to the following circuit
|x⟩n
MODADDp
|x⟩n
|y⟩n |y + x mod p⟩n
The following implementation is a slight modification of [VBE96] and [Lit23].
Proposition 3.2 (Modular adder - Vedral’s architecture [VBE96]) . Let
• QADD be a quantum circuit that performs a quantum addition using sADD ancillas, and rADD
Tof gates,
• QCOMP(p) be a quantum comparator with a classical constant p using sCOMP ancillas, rCOMP
Tof gates,
• C-QSUB(p) be a quantum circuit that performs a (controlled) subtraction by a constant p using
sC-SUB ancillas, and rC-SUB Tof gates,
• Q′
COMP: be a quantum comparator using ( s′
COMP ancillas, r′
COMP Tof gates).
24
