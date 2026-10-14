---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 23
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 23

The text below is a page-delimited extraction of the unchanged source PDF.

We now explore constructions for comparing a quantum register with a classical value.
Definition 2.33 (Quantum comparison with a classical constant). We define a quantum comparator
with a classical constant a ∈ {0, 1}n as any unitary gate implementing the n strings comparison
with a according to the following circuit
|x⟩n ·< a |x⟩n
|t⟩1 |t ⊕1[x < a]⟩1
where 1[x < a] coincides with the most significant bit of x − a i.e is 1 when x < aand 0 otherwise.
Proposition 2.34 (Comparator by a classical constant) . Let QCOMP be a circuit performing the
n-bit comparator operation as per definition 2.24 using r Tof gates and s ancillas. Then, there is a
circuit implementing an n-bit comparator by a classical constant as per definition 2.33 using the r
Tof gates and s + n ancillas, with an additional 2|a| NOT gates.
Proof. Similar to the idea in proposition 2.16, we first use an n qubit register to load our constant
a into memory by applying |a| NOT gates (one for each bit ai ̸= 0), giving the state
|0⟩s+n |x⟩n |t⟩1
Load7− − − → |0⟩s |a⟩n |x⟩n |t⟩ .
Now, we apply the comparator circuit with inputs |a⟩|x⟩ on target |t⟩
|0⟩s |a⟩n |x⟩n |t⟩1
QCOMP
7− − − − → |0⟩s |a⟩n |x⟩n |t ⊕ 1[a > x]⟩
The ancilla is then uncomputed by applying the previous sequence of NOT gates a second time
|0⟩s |a⟩n |x⟩n |t ⊕ 1[x > y]⟩1
Unload7− − − − → |0⟩s+n |x⟩n |t ⊕ 1[x < a]⟩1 .
Similar to the construction in proposition 2.25, a comparator by a classical constant can be
constructed by using an adder and a subtractor, as shown below.
Theorem 2.35 (Comparator with a classical constant - using an adder by a constant and a
subtractor by a constant) . Let QADD(a) be a circuit performing an n-bit addition by a constant
as per definition 2.15, using rADD Tof gates and sADD ancillas. Also, let QSUB(a) be a circuit
performing an n-bit subtraction by a constant as per definitions 2.15 and 2.21, using rSUB Tof
gates and sSUB ancillas. Then, there is a circuit implementing an n-bit comparator by a classical
constant as per definition 2.33 using r = rADD + rSUB Tof gates, an additional CNOT gate and
s = 1 + max(sADD, sSUB) ancilla qubits
Proof. The idea is similar to proposition 2.25 giving a comparator using an adder and a subtractor.
Now, theorem 2.35 can be applied specifically to the case of the Draper adder to give the theorem
below.
Proposition 2.36 (Comparator by a classical constant - Draper/Beauregard [Bea02]) . Let x ∈
{0, 1}n, a∈ {0, 1}n be two bit strings. There is a circuit implementing a comparator by a classical
constant:
|x⟩n |t⟩1 7→ |x⟩n |t ⊕ 1[x < a]⟩1 .
using a circuit with 1 CNOT, 2 QFTn+1, 2 IQFTn+1, 1 ΦSUB(a) and 1 ΦADD(a) gates, and a single
ancilla qubit.
23
