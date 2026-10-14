---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 11
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 11

The text below is a page-delimited extraction of the unchanged source PDF.

c0 = 0
M
A
J
c0
U
M
A
c0 = 0
x0 x0 ⊕ c0 x0
y0 y0 ⊕ c0 s0
M
A
J
c1
U
M
A
x1 x1 ⊕ c1 x1
y1 y1 ⊕ c1 s1
c2
...
...
M
A
J
cn−2
U
M
A
xn−2 xn−2 ⊕ cn−2 xn−2
yn−2 yn−2 ⊕ cn−2 sn−2
M
A
J
cn−1
xn−1 xn−1 ⊕ cn−1 xn−1
yn−1 yn−1 ⊕ cn−1 sn−1
sn = cn sn
Figure 13: Gidney’s logical- AND adder. The qubit C0 starts in the state |0⟩ and doesn’t change value throughout the
computation, therefore it can be omitted to reduce the ancilla count by 1 [Gid18].
Proposition 2.4 (Gidney adder [Gid18]). There is a circuit implementing an n-bit quantum adder
as per definition 2.1 using n ancilla qubits and n Tof gates.
Proof. An adder block in the temp logical- AND adder is constructed as shown in figure 12. The full
circuit is shown in figure 13, it uses n MAJ blocks, (n − 1) UMA blocks, and 2 additional CNOTs.
We require 1 less UMA block with respect to the CDKPM implementation because the final MAJ
block computes the most significant carry bit cn which also happens to the be most significant bit
of the addition sn = (x + y)n. We only use the two additional CNOT’s for restoring the values of
xn−1 and computing the second most significant bit of the sum i.e. sn−1 = (x + y)n−1.
Draper implementation While the implementations described in the previous sections use
essentially classical algorithms for addition and convert them to reversible quantum circuits,
Draper [Dra00] came up with a quantum-specific way of addition using QFT gates.
... ... ...
... ... ...
...
... ... ...
... ... ...
... ... ...
... ... ...
... ...
... ... ...
... ... ...
xn−1 xn−1
xn−2 xn−2
...
...
x1 x1
x0 x0
ϕn(y) 2 3 n n+1 ϕn(x+ y)
ϕn−1(y) 1 2 n-1 n ϕn−1(x+ y)
...
...
ϕ1(y) 1 2 ϕ1(x+ y)
ϕ0(y) 1 ϕ0(x+ y)
Figure 14: Draper’s plain adder [Dra00]. It performs the operation |x⟩n |ϕ(y)⟩n+1
ΦADD
7− − − → |x⟩n |ϕ(x + y)⟩n+1. See
figure 3 for the definition of the gates in the figure. Initially, yn = |0⟩ to account for the overflow of the addition
11
