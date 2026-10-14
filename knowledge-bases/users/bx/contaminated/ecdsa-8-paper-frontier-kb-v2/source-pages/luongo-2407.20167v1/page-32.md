---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 32
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 32

The text below is a page-delimited extraction of the unchanged source PDF.

Now, we need to add back p to those states whenever x + a < p. Notice that ( x + a − p)n, i.e. the
most significant bit of x + a − p is 1 only when x <(p − a). Controlled on ( x + a − p)n, we add
back p
|0⟩s−1 |x + a − p⟩n+1
C-QADD(p)
7− − − − − − →|0⟩s−1 |x + a mod p⟩n |1[x + a < p]⟩1 .
Now, as we have seen many times before, we have to find an operation that uncomputesd = 1[x+a <
p]. We notice that 1[x + a < p] ≡ 1[x + a mod p ≥ a] since x + a mod p = x + a + (d − 1) · p.
Therefore, we can use a constant comparator ( · < a) followed by a NOT to perform the required
reset/uncomputation
|0⟩s−1 |x + a mod p⟩n |1[x + a < p]⟩
QCOMP(a)
7− − − − − − →1
|0⟩s−1 |x + a mod p⟩n |1[x + a < p] ⊕ 1[x + a mod p < a]⟩1
= |0⟩s−1 |x + a mod p⟩n |1⟩
QNOT
7− − − →1 |0⟩s |x + a mod p⟩n .
3.3 Controlled modular addition by a constant
Definition 3.16 (Controlled modular addition by a constant) . Given x, a, p∈ {0, 1}n (with a, p
classically known), and a control c ∈ {0, 1} with 0 ≤ a, x < p. We will denote controlled modular
addition by a constant a (with modulus p) with the following circuit
|c⟩1 |c⟩1
|x⟩n MODADDp(a) |x + c ·a mod p⟩n
A simple way to perform a controlled modular addition by a constant is by using a quantum
modular adder as per definition 3.1.
Theorem 3.17 (Controlled modular adder by a constant) . Let QMODADDp be a quantum circuit
that performs an n-bit quantum modular addition as per definition 3.1 using s ancillas, and r Tof
gates. Then, there is a circuit C-QMODADDp (a) implementing an n-bit controlled quantum modular
addition by a constant as per definition 3.16 using n + s ancilla qubits and r Tof gates, and an
additional 2|a| CNOT gates.
Proof. The technique is similar to what we have used in many previous cases when an operation by
a constant is involved. We first take an unused n qubit register, and load the value a (controlled on
c) using |a| CNOT gates
|0⟩s+n |x⟩n
Load7− − − →|0⟩s |c · a⟩n |x⟩n .
We now perform the required modular addition
|0⟩s |c · a⟩n |x⟩n
QMODADDp(a)
7− − − − − − − − →|0⟩s |c · a⟩n |x + c · a mod p⟩n .
We have to finally unload the constant a
|0⟩s |c · a⟩n |x + c · a mod p⟩n
Unload7− − − − →|0⟩s+n |x + c · a mod p⟩n .
32
