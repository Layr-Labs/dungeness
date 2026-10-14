---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 30
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 30

The text below is a page-delimited extraction of the unchanged source PDF.

According to proposition 3.9, there is a circuit performing the operation
|c⟩1 |x⟩n |y⟩n
C-QMODADD
7− − − − − − − → |c⟩1 |x⟩n |c · x + y mod p⟩n
using r = ( rC-ADD + rCOMP + rC-SUB + r′
C-COMP) = (2 n + n + n + (n + 1)) = 5 n + 1 Tof gates
and s = 2 + max(sC-ADD, sCOMP, sC-SUB, s′
C-COMP) = 2 + max(n + 1, 2n + 1, 2n + 1, n+ 1) = 2n + 3
ancillas.
3.2 Modular addition by a constant
Definition 3.12 (Modular addition by a constant) . Let x ∈ {0, 1}n. Assume to know classically
p, a∈ {0, 1}n with 0 ≤ a, x < p. We will denote modular addition by a constant a (with modulus p)
with the following circuit
|x⟩n MODADDp(a) |x + a mod p⟩n+1
A simple way to perform a modular addition by a constant is by using a quantum modular
adder as given by definition 3.1.
Proposition 3.13 (Modular adder by a constant) . Let QMODADDp be a quantum circuit that
performs an n-bit quantum modular addition as per definition 3.1, using s ancillas, and r Tof gates.
Then, there is a circuit QMODADDp (a) implementing an n-bit quantum modular addition by a constant
as per definition 3.12 using n + s ancilla qubits and r Tof gates, and an additional 2|a| NOT gates.
Proof. Similar to the proposition 2.16, We first take an unused n qubit register, and load the value
a using |a| NOT gates
|0⟩s+n |x⟩n
Load7− − − →|0⟩s |a⟩n |x⟩n
We now perform the required modular addition
|0⟩s |a⟩n |x⟩n
QMODADD
7− − − − − − →|0⟩s |a⟩n |x + a mod p⟩n
Finally, we unload the constant a
|0⟩s |a⟩n |x + a mod p⟩n
Unload7− − − − →|0⟩s+n |x + a mod p⟩n .
The above construction works for any modular adder construction that performs the operation
|x⟩n |y⟩n
QMODADDp
7− − − − − − → |x⟩n |y + x mod p⟩n. However, when examining the VBE architecture, we can
modify certain subroutines to enable a different approach to performing constant modular addition.
Theorem 3.14 (Modular adder by a constant - in VBE architecture) . Let
• QADD(a) be a quantum circuit that performs a constant quantum addition using sADD ancillas,
and rADD Tof gates;
• QCOMP(p) be a quantum comparator using sCOMP ancillas, rCOMP Tof gates;
• C-QSUB(p) be a quantum circuit that performs a (controlled) subtraction by a constant p using
sC-SUB ancillas, and rC-SUB Tof gates;
• Q′
COMP(a): be a constant quantum comparator using ( s′
COMP ancillas, r′
COMP Tof gates).
30
