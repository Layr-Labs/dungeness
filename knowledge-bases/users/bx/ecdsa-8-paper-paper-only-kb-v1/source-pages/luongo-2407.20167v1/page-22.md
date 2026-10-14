---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 22
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 22

The text below is a page-delimited extraction of the unchanged source PDF.

c0 = 0 U
M
A
† c0 ⊕ x0 U
M
A
c0 = 0
y0 c0 ⊕ y0 y0
x0
U
M
A
† c1 ⊕ x1 U
M
A
x0
y1 c1 ⊕ y1 y1
x1 c2 ⊕ x2 x1
...
...
xn−3
U
M
A
† cn−2 ⊕ xn−2
U
M
A
xn−3
yn−2 cn−2 ⊕ yn−2 yn−2
xn−2
U
M
A
† cn−1 ⊕ xn−1
U
M
A
xn−2
yn−1 cn−1 ⊕ yn−1 yn−1
xn−1 cn xn−1
t = 0 0 cn
Figure 21: Comparator circuit based on the CDKPM adder.
Definition 2.29 (Controlled quantum comparison). We define a controlled quantum comparator
as any unitary gate implementing the n bits strings comparison according to the following circuit
|c⟩1 |c⟩1
|x⟩n
·> ·
|x⟩n
|y⟩n |y⟩n
|t⟩1 |t ⊕1[c ·x > y]⟩1
Proposition 2.30 (Controlled comparator - CDKPM - using half a subtractor [Cuc+04]) . There is
a circuit implementing an n-bit controlled comparator as per definition 2.29 using 0 ancilla qubits
and 2n + 1 Tof gates.
Proof. The comparator is controlled by a qubit |c⟩1. From proposition 2.27, we see that the output
of the comparator is computed as the most significant bit ( y − x)n of the subtraction of y and x.
The CNOT that copies the comparator value after the chain of UMA†’s needs to now be controlled,
thus leading to an extra Tof gate.
The previous quantum controlled comparator can also be executed using the temporary logical-
AND gate of Gidney, which consumes n more ancillas (to store the temporary logical AND) in
comparison to proposition 2.30 but requires fewer Tof gates.
Proposition 2.31 (Controlled comparator - Gidney - using half a subtractor) . There is a circuit
implementing an n-bit controlled quantum comparator as per definition 2.29 using n + 1 ancilla
qubits and n + 1 Tof.
When comparing registers, we note that they may not always be of equal size n. When registers
x ∈ {0, 1}n and y ∈ {0, 1}n′
with n < n′, one can circumvent this problem by padding the register
|x⟩n with an extra n′ − n qubits and perform the comparison on two n′ qubit registers. However,
there is a slightly more efficient solution available for the CDKPM and Gidney adders.
Remark 2.32. Assume that n′ = n + 1 without loss of generality. Let y[0,1,···,n−1] represent the first
n bits of y, notice that 1[x > y] ≡ 1[x > y[0,1,···,n−1]] ·(NOTyn). Therefore, the CNOT computing the
required comparison now becomes a Tof gate, with controls 1[x > y[0,1,···,n−1]] and (NOTyn). Thus
using a single extra Tof gate with no extra ancillas.
22
