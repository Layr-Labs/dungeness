---
kind: source-page
source_id: arXiv:2410.00899v1
source_pdf: raw/2410.00899v1.pdf
source_page: 1
---

# Quantum schoolbook multiplication with fewer Toffoli gates - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

Quantum schoolbook multiplication with fewer Toffoli gates
Daniel Litinski @ PsiQuantum, Palo Alto
This paper presents a method for construct-
ing quantum circuits for schoolbook multipli-
cation using controlled add-subtract circuits,
asymptotically halving the Toffoli count com-
pared to traditional controlled-adder-based con-
structions. Controlled n-qubit add-subtract cir-
cuits, which perform an addition when the con-
trol qubit is one and a subtraction when it is
zero, require only n −1 Toffoli gates, instead
of the 2n −1 needed for controlled adders. De-
spite the existence of multiplication circuits with
better asymptotic scaling, schoolbook multipli-
cation yields the lowest Toffoli counts for small
register sizes, making it advantageous in practi-
cal applications. For example, the presented ap-
proach reduces the Toffoli count by up to around
30% in circuits for breaking 256-bit elliptic curve
keys compared to circuits with standard school-
book multipliers.
In the context of fault-tolerant quantum computa-
tion [1, 2], the cost of a quantum circuit is commonly
quantified in terms of the Toffoli count, i.e., the num-
ber of Toffoli gates in the circuit assuming that the
remaining gates are Clifford gates. We focus on quan-
tum circuits that implement the unitary U for quantum
multiplication in superposition where both factors are
stored in n-qubit quantum registers, i.e., U|x⟩|y⟩|0⟩=
|x⟩|y⟩|xy⟩. We also consider variations of this opera-
tion in which a modular reduction is performed on the
result. Our results are summarized in Tab. 1.
Controlled add-subtract. Using Gidney adders [3], a
quantum ripple-carry addition can be performed with
n Toffoli gates if the final carry qubit is kept, or with
n −1 Toffoli gates if it is discarded, which is referred
to as addition with and without carry-out in Fig. 1a/b
(see also Fig. 4). Subtraction can be performed using
the same circuit by flipping all bits of the subtrahend
(Fig. 1c). Similarly, a controlled addition with and
without carry-out can be performed with 2n + 1 and
2n −1 Toffoli gates, respectively (Fig. 1d/e). A con-
trolled adder performs an addition if the control qubit
is in the |1⟩state, and performs no operation if it is in
the |0⟩state. We consider a similar circuit that we refer
to as a controlled add-subtract. It performs an addition
if the control qubit is in the |1⟩state, and a subtraction
if it is in the |0⟩state. A controlled add-subtract can be
implemented with the same Toffoli count as an uncon-
trolled adder. As shown in Fig. 1f, a controlled add-
subtract merely requires two multi-target controlled-
NOT gates before and after a standard adder. There-
Mult. circuit Toffoli count
Schoolbook n2 + 4n + 3 (compared to 2n2 + n)
Modular mod 2n 0.5n2 + 1.5n (compared ton2)
Modular modp n 2 + 6n + n
w(2w + 3·2w/2 + 3n −3)
(compared to 2n2 + 4n + n
w(2w + 3·2w/2 + n −1))
Table 1: Toffoli counts of three different n-qubit schoolbook
multiplication circuits in this paper: a standard schoolbook
multiplication with a 2n-qubit result register, a modular multi-
plication circuit in which only n bits of the result are kept, and
a modular multiplication circuit in which a modular reduction
mod p is performed on the result, where p is a prime number.
For the latter, the Toffoli count depends on an integer w, which
is a tunable window size. The optimal value is approximately
w ≈log2
(
n
log2 n
)
+ 2.
fore, a controlled add-subtract with or without carry-
out has a Toffoli count of n or n −1 (Fig. 1f/g). If we
interpret all numbers in a controlled add-subtract with
carry-out as positive integers, then the circuit outputs
b+a if the control qubit is|1⟩and b+2n−a if it is |0⟩, as
shown in Fig. 1g. Controlled add-subtracts have previ-
ously been described in the literature in the context of
circuits for square roots [4] and controlled rotations [5].
Schoolbook multiplication. We first consider a mul-
tiplication operation that acts on two n-qubit registers
storing two integers |x⟩and |y⟩, and computes |xy⟩in
an additional 2n-qubit result register. Such a school-
book multiplication circuit can be implemented using
the circuit shown in Fig. 2a. The circuit straightfor-
wardly computes the product xy =
n−1∑
k=0
xk ·2ky. Each
addition of xk2ky can be performed with a controlled
addition controlled on xk (the k-th bit of x where x0
is the least significant bit) adding y shifted by k bits.
Therefore, the circuit consists of n controlled n-qubit
additions with carry-out, in which case it has a Toffoli
count of 2n2 + n.
Now consider the circuit in Fig. 2b. If we replace each
controlled addition with a controlled add-subtract, each
step will be adding (1 −xk)2n+k + (2xk −1) ·2k ·y. In
other words, for xk = 1 , the operation is adding 2ky
(as in a standard controlled adder), but for xk = 0, it
is adding 2n+k −2ky. After n controlled add-subtract
operations, the intermediate result is
n−1∑
k=0
(1 −xk)2n+k + (2xk −1) ·2ky
1
arXiv:2410.00899v1  [quant-ph]  1 Oct 2024
