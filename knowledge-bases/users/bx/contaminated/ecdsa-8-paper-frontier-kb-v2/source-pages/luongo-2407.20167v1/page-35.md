---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 35
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 35

The text below is a page-delimited extraction of the unchanged source PDF.

Lemma 4.1 (Measurement-based uncomputation lemma). Let g : {0, 1}n → {0, 1} be a function,
and let Ug be a self-adjoint (n + 1)-qubit unitary that implements g as follows:
Ug |x⟩A |b⟩G = |x⟩A |b ⊕ g(x)⟩G .
There is an algorithm performing the mapping
X
x
αx |x⟩A |g(x)⟩G 7→
X
x
αx |x⟩A |0⟩G
using with 1/2 probability Ug, 2 H gates, and 1 NOT gate. It also involves one single-qubit
computational basis measurement and a single H gate.
Proof. The algorithm is described in figure 24. We first apply the Hadamard gate on the register G
and measure it in the computational basis. Since g(x) ∈ {0, 1}, the resulting outcomes is 0 or 1 with
equal probabilities. If we obtain 0, we successfully uncomputed the register, leaving the registers in
the state P
x αx |x⟩A |0⟩G. On the other hand, if we get the outcome 1, the state at this point isP
x αx(−1)g(x) |x⟩A |1⟩G . We then apply another Hadamard to G, followed by Ug. This performs a
phase kickback, leaving the quantum computer in the state
X
x
αx(−1)g(x) |x⟩A
|0 ⊕ g(x)⟩G − |1 ⊕ g(x)⟩G√
2 =
X
x
αx(−1)g(x)⊕g(x) |x⟩A |−⟩G .
Applying on G another Hadamard and a NOT gate results in the final state P
x αx |x⟩A |0⟩G.
4.1 Modular addition
|x⟩n
ADD ·> ·
|x⟩n
|01⟩|y⟩n ·< p SUB(p) |y + x mod p⟩n |0⟩1
|0⟩1 H H H |0⟩1
compute (x + y) mod p uncompute ancilla
Figure 25: Implementation of a MBU modular addition. The double dotted lines represents the uncomputation of the
ancilla, controlled on the measurement value.
Theorem 4.2 (MBU modular adder - VBE architecture) . Let
• QADD be a quantum circuit that performs a quantum addition using sADD ancillas, and rADD
Tof gates;
• QCOMP(p) be a quantum comparator using sCOMP ancillas, rCOMP Tof gates;
• C-QSUB(p) be a quantum circuit that performs a (controlled) subtraction by a constant p using
sC-SUB ancillas, and rC-SUB Tof gates;
• Q′
COMP: be a quantum comparator using ( s′
COMP ancillas, r′
COMP Tof gates).
There is a circuit, QMODADDp , performing the n-bit modular addition operation as per definition 3.1
using r = (rADD + rCOMP + rC-SUB + (r′
COMP/2)) Tof gates in expectation and
s = 2 + max(sADD, sCOMP, sC-SUB, s′
COMP)
ancillas.
35
