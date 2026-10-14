---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 12
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 12

The text below is a page-delimited extraction of the unchanged source PDF.

Proposition 2.5 (Draper’s plain adder [Dra00]) . Let x ∈ {0, 1}n, y∈ {0, 1}n be two bit strings
stored in register X and Y of size n and n + 1 respectively (the most significant bit of register Y is
set to 0). Also, let |ϕ(y)⟩n+1 := QFTn+1 |y⟩n+1. There is a circuit ΦADD performing the operation
|x⟩n |ϕ(y)⟩n+1
ΦADD
7− − − → |x⟩n |ϕ(x + y)⟩n+1
using zero ancilla qubits, and count(ΦADD) = {(C-R(θ1), n)} ∪ {(C-R(θi), n+ 2 − i) | i ∈ [2, n+ 1]} .
Proof. We denote as ϕi(y) the i-th qubit of ϕ(y). For ϕi(y), the following operations are performed
in Draper’s circuit (see figure 14). Consider eUi = CX0-RYi (θ1)CX1-RYi (θ2) ··· CX0-RYi (θi+1), the
unitary acting on |ϕi(y)⟩1. The transformation on |ϕi(y)⟩1 is as follows:
|x⟩n |ϕi(y)⟩1
eUi
7− →CX0-RYi (θ1)CX1-RYi (θ2) ··· CX0-RYi (θi+1) |x⟩n

|0⟩ + exp
2πiy
2i+1

|1⟩

= |x⟩n

|0⟩ +


iY
j=0
exp
 2πixj
2i−j+1

exp
2πiy
2i+1

|1⟩


= |x⟩n

|0⟩ + exp

2πi
iX
j=0
xj
2i−j+1

exp
2πiy
2i+1

|1⟩


= |x⟩n

|0⟩ + exp

 2πi
2i+1
iX
j=0
2jxj

exp
2πiy
2i+1

|1⟩


= |x⟩n

|0⟩ + exp

 2πi
2i+1
n−1X
j=0
2jxj

exp
2πiy
2i+1

|1⟩


= |x⟩n

|0⟩ + exp
2πix
2i+1

exp
2πiy
2i+1

|1⟩

= |x⟩n

|0⟩ + exp
2πi(x + y)
2i+1

|1⟩

= |x⟩n |ϕi(x + y)⟩1 .
We see that the ith qubit of the target register |ϕ(y)⟩n+1, that is |ϕi(y)⟩1, now holds the ith qubit of
the Fourier transformed sum i.e. |ϕi(x + y)⟩1. Hence, generalising the above result on the entire
state of the target register, we conclude that the Draper adder performs the operation
|x⟩n |ϕ(y)⟩n+1 = |x⟩n
nO
j=0
|ϕj(y)⟩1 7→ |x⟩n
nO
j=0
|ϕj(x + y)⟩1 = |x⟩n |ϕ(x + y)⟩n+1 .
The ΦADD circuit on n qubits has the same structure as a QFT circuit, excluding a C-R(θ1) gate
and all the H gates. Therefore, the gate count of the ΦADD circuit is:
count(ΦADD) = {(C-R(θ1), n)} ∪ {(C-R(θi), n+ 2 − i) | i ∈ [2, n+ 1]} .
Remark 2.6. Resource-wise, ΦADD is bounded above by the cost of a QFTn+1 gate.
In Draper’s original circuit, he considers the register |ϕ(y)⟩n+1 = QFTn+1 |y⟩ to be prepared
beforehand, and the final output to be in the state |ϕ(x + y)⟩n+1 = QFTn+1 |x + y⟩n+1 after the
addition. However, to stay consistent with definition 2.1, we must take into account the cost of the
QFTn+1 to prepare |ϕ(y)⟩n+1, and the cost of the QFTn+1 to return back to the computation basis
at the end of the addition. Hence, we derive the following corollary.
12
