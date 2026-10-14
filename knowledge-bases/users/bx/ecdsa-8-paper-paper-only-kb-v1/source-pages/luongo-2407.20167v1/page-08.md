---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 8
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 8

The text below is a page-delimited extraction of the unchanged source PDF.

C
A
R
R
Y
≡
S
U
M =
Figure 4: CARRY and SUM gate decomposition for the VBE adder [VBE96]. The CARRY gate performs the mapping
|ck, xk, yk, ck+1⟩ 7→ |ck, xk, yk ⊕ xk, ck+1 ⊕ maj(xk, yk, ck)⟩ where maj is defined in equation (5) of section 1.3. The
SUM gate performs the mapping |ck, xk, yk⟩ 7→ |ck, xk, yk ⊕ ck ⊕ xk⟩
Proposition 2.2 (VBE plain adder [VBE96]) . There is a circuit implementing an n-bit quantum
addition as per definition 2.1 using n ancilla qubits and 4n Tof gates.
Proof. The sought circuit is given by figure 5 together with the definition of the gates CARRY and
SUM in figure 4.
c0 = 0 C
A
R
R
Y
C
A
R
R
Y
† S
U
M
c0 = 0
x0 x0
y0 s0
c1 = 0 C
A
R
R
Y
C
A
R
R
Y
† S
U
M
c1 = 0
x1 x1
y1 s1
c2 = 0 c2 = 0
...
...
cn−2 = 0 C
A
R
R
Y
C
A
R
R
Y
† S
U
M
cn−2 = 0
xn−2 xn−2
yn−2 sn−2
cn−1 = 0 C
A
R
R
Y
S
U
M
cn−1 = 0
xn−1 xn−1
yn−1 sn−1
yn = 0 sn
Figure 5: Adder circuit based on Vedral et al. [VBE96]
1. The circuit is initiated in the state
|c⟩n |x⟩n |y⟩n+1 = |c0, x0, y0, . . . ci, xi, yi, ci+1, . . . cn−1, xn−1, yn−1, yn⟩
where ci = 0 for any 0 ≤ i ≤ n.
2. The first part of the circuit consists of a chain of n carry gates. The i-th gate computes the
carry ci+1 through the recursive equation (5) storing its value in register Ci+1. At last, it
computes the most significant bit of the result x + y, expressed by the carry cn = yn, storing
it in the qubit Yn, added to take into account the possible overflow. More precisely, the state
after the chain of the n different CARRY gates is:
C0 ← 0,
...
Ci ← maj(xi−1, yi−1, ci−1)
Xi ← xi
Yi ← xi ⊕ yi
...
Yn ← yn ⊕ maj(xn−1, yn−1, cn−1) .
8
