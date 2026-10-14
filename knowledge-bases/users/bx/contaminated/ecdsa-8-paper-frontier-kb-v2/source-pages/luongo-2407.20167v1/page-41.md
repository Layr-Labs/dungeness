---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 41
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 41

The text below is a page-delimited extraction of the unchanged source PDF.

using sCOMP ancillas and rCOMP Tof gates. Let us assume we also have access to C-Q′
COMP, with
|c⟩1 |x⟩n |y⟩n |t⟩1
C-Q′
COMP
7− − − − − → |c⟩1 |x⟩n |y⟩n |t ⊕ c · 1[x < y]⟩1
using s′
C-COMP ancillas and r′
C-COMP Tof gates. Then, there is a circuit that performs the operation
QIN RANGE
|x⟩n |y⟩n |z⟩n |t⟩1
QIN RANGE
7− − − − − − → |x⟩n |y⟩n |z⟩n |t ⊕ 1[x ∈ (y, z)]⟩1
using s = 1 + sCOMP ancillas and r = 1.5rCOMP + r′
C-COMP Tof gates.
Proof. We begin by first checking if y < x
|0⟩s |x⟩n |y⟩n |z⟩n |t⟩1
QCOMP
7− − − − →|0⟩s−1 |x⟩n |y⟩n |z⟩n |1[y < x]⟩|t⟩1
Next we compute whether x < zcontrolled on 1[y < x], and store the output in our target. We
know that 1[x ∈ (y, z)] ≡ (1[y < x] · 1[x < z]), and since we have both the comparator values stored
in memory
|0⟩s−1 |x⟩n |y⟩n |z⟩n |1[y < x]⟩|t⟩1
Q′
C-COMP
7− − − − − → |0⟩s−1 |x⟩n |y⟩n |z⟩n |1[y < x]⟩1 |t ⊕ 1[x ∈ (y, z)]⟩1 .
We finally uncompute the intermediate value 1[y < x] using QCOMP
|0⟩s−1 |x⟩n |y⟩n |z⟩n |1[y < x]⟩1 |t ⊕ 1[x ∈ (y, z)]⟩1
QCOMP
7− − − − →|0⟩s |x⟩n |y⟩n |z⟩n |t ⊕ (1[y < x] · 1[x < z])⟩1 .
Therefore, we get a cost of r = 2rCOMP + r′
C-COMP. This cost can be decreased by applying the MBU
lemma on the QCOMP uncomputing 1[y < x], thus leading to a cost of r = 1.5rCOMP + r′
C-COMP.
Acknowledgement
This work started when AS was working at Inveriant Pte. Ltd. AS is supported by Innovate
UK under grant 10004359. AMM has received funding from the European Union’s Horizon 2020
research and innovation programme under the grant agreement N°101034324 and has been partially
supported by the Italian Group for Algebraic and Geometric Structures and their Application
(GNSAGA–INdAM). This work is supported by the National Research Foundation, Singapore,
and A*STAR under its CQT Bridging Grant. We also acknowledge funding from the Quantum
Engineering Programme (QEP 2.0) under grants NRF2021-QEP2-02-P05 and NRF2021-QEP2-02-
P01. We thank Anupam Chattopadhyay and Zeyu Fan for useful discussions. AMM and AL thank
Niels Benedikter for the hospitality at Universit` a degli Studi di Milano.
References
[Agg+17] Divesh Aggarwal, Gavin K Brennen, Troy Lee, Miklos Santha, and Marco Tomamichel.
“Quantum attacks on Bitcoin, and how to protect against them”. In: arXiv preprint
arXiv:1710.10377 (2017).
[Bab+18] Ryan Babbush, Craig Gidney, Dominic W Berry, Nathan Wiebe, Jarrod McClean,
Alexandru Paler, Austin Fowler, and Hartmut Neven. “Encoding electronic spectra
in quantum circuits with linear T complexity”. In: Physical Review X 8.4 (2018),
p. 041015.
[Bea02] Stephane Beauregard. “Circuit for Shor’s algorithm using 2n+ 3 qubits”. In: arXiv
preprint quant-ph/0205095 (2002).
41
