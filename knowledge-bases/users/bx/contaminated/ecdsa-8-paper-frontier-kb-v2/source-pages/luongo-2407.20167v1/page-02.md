---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 2
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 2

The text below is a page-delimited extraction of the unchanged source PDF.

A realistic implementation of the above gate will, in principle, involve a number k of auxiliary
qubits which get mapped in a garbage state |g(x)⟩ as follows:
eUf : |x⟩n |0⟩m |0⟩k 7→ |x⟩n |f(x)⟩m |g(x)⟩k . (3)
The auxiliary qubits are entangled with the other registers and must be uncomputed, i.e.
restored to their original value, in order to get a reversible out-of-place implementation of f. Such
uncomputation can be achieved in several ways. A first solution, due to [Ben73], simply prescribes
copying the output |f(x)⟩m into an auxiliary m-qubit register via a set of m CNOT gates and then
apply eU†
f . Therefore, one can implement Uf as in figure 1. This strategy doubles the resource cost
|x⟩n
˜Uf ˜Uf
†
|x⟩n
|0⟩m |0⟩m
|0⟩k |0⟩k
|0⟩m |f(x)⟩m
Figure 1: Bennet’s garbage uncomputation.
of the reversible computation of f, also requiring m more ancillary qubits. Alternatively, one could
look for an out-of-place implementation of the garbage function Ug, seeing g as a function of x and
f(x). When this unitary is available, one can implement Uf as in figure 2.
|x⟩n
˜Uf
|x⟩n
Ug†
|x⟩n
|0⟩m |f(x)⟩m |f(x)⟩m
|0⟩k |g(x)⟩k |0⟩k
Figure 2: Garbage gate uncomputation.
In principle, invoking the garbage circuit Ug can be quite resource intensive. Therefore, it is nec-
essary to develop techniques to optimize the synthesis of quantum circuits and their uncomputation.
Arithmetic Circuits. Effective implementations of binary arithmetic are fundamental to many
quantum algorithms, such as quantum algorithms for factoring [Sho94; GE21] and discrete loga-
rithm [Eke18], quantum walks [Chi02], and for algorithms that construct oracles for Grover’s search
and quantum phase estimation, e.g. [Ber+19; Dor+22; Agg+17]. Arithmetic operations like (modu-
lar) addition, subtraction, and comparison (by a constant) have been extensively studied, resulting
in numerous implementation strategies, each with its own tradeoffs. Many circuits for arithmetic
are based on the plain addition circuit defined by the operation |x⟩n |y⟩n
QADD
7− − − → |x⟩n |x + y⟩n+1 for
two n-qubit quantum registers. Other primitives can be derived by composing these circuits for
addition. However, there are often more efficient ways to build arithmetic primitives. Broadly, these
quantum circuits are designed for both quantum-quantum arithmetic functions, i.e., circuits of the
form |x⟩|y⟩ U7− → |x⟩|f(x, y)⟩, and quantum-classical arithmetic functions, i.e., circuits of the form
|x⟩
U(a)
7− − − → |x⟩|f(x, a)⟩.
In the computation of our function f, intermediate values may need to be appropriately
uncomputed. For example, any ripple carry addition algorithm, analogously to the schoolbook
addition method, requires computing the carry bitwise starting from the least significant bits of the
two addends.
2
