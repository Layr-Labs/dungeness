---
kind: source-page
source_id: arXiv:2410.00899v1
source_pdf: raw/2410.00899v1.pdf
source_page: 2
---

# Quantum schoolbook multiplication with fewer Toffoli gates - source page 2

The text below is a page-delimited extraction of the unchanged source PDF.

Figure 1: Toffoli counts of quantum circuit for addition with (a) and without (b) carry-out, subtraction (c), controlled addition
with (d) and without (e) carry-out, and controlled add-subtract with (f) and without (g) carry-out. In these circuits, |ctrl⟩refers
to control qubits and |cin⟩refers to input carry qubits.
= 2xy + 22n −2n(x + 1 +y) + y .
Some corrections need to be performed to obtain the
intended result xy. We first add 2n(x + 1) using an
n-qubit adder with the input carry set to 1. Then we
perform a 2n-qubit subtraction of 22n + y, and finally
an n-qubit addition of 2ny. We divide the resulting
number by two by simply relabeling the qubits. This
results in a schoolbook multiplication circuit with only
n2 + 4n + 3 Toffoli gates.
Modular multiplication mod 2n. The naive school-
book multiplication circuit consists of n controlled n-bit
adders with carry-out. A naive modular multiplication
circuit mod 2n can be obtained by replacing the j-th
controlled adder with a controlled (n + 1−j)-bit adder
without carry-out, as shown in Fig. 2c. This results in
a Toffoli count of n2.
In the circuit in Fig. 2d, we use controlled add-
subtracts with carry-out instead of controlled adders
without carry-out. The intermediate result is a 2n + 1-
bit number corresponding to the intermediate result of
the schoolbook multiplication mod 2n+1, i.e.,
2xy + 22n −2n(x + 1 +y) + y mod 2n+1
= 2xy −2n(x + 1 +y) + y mod 2n+1 .
The required correction operations are cheaper com-
pared to the previous schoolbook multiplication, as they
are performed modulo 2n+1. This turns the addition of
2n(x + 1) into an addition ofx0+1, where x0 is the least
significant bit of x. As this corresponds to a controlled-
NOT gate conditioned on x0 followed by a NOT gate, it
does not contribute to the Toffoli count. Similarly, the
addition of 2ny turns into an addition of y0. The sub-
traction of 22n + y turns into a subtraction of y, which
contributes n Toffoli gates to the total Toffoli count of
0.5n2 + 1.5n.
Modular multiplication modp. An out-of-place mod-
ular multiplication construction is described in Refs. [6,
7] for the case that the modulus is a prime number p.
It assumes that the factors are stored in Montgomery
representation [8]. The circuit is shown in Fig. 3a. It
consists of n/w ModMultStep operations that each con-
tribute w qubits to a garbage register, followed by two
additions of a constant for modular reduction each con-
tributing n Toffoli gates. If necessary, the garbage regis-
ter can be uncomputed by copying the multiplication re-
sult into a separate register using controlled-NOT gates,
and then uncomputing the entire multiplication. Each
ModMultStep consists of w controlled additions with
carry-out contributing 2w(n + 1) Toffoli gates, a 2w-
item lookup table contributing 2w Toffoli gates [9], an
2
