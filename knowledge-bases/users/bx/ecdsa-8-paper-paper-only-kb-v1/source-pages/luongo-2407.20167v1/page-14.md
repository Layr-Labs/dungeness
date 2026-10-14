---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 14
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 14

The text below is a page-delimited extraction of the unchanged source PDF.

Corollary 2.10 (Controlled adder - n extra ancillas and n extra Tof gates). Let QADD be a quantum
circuit that performs an n-bit quantum addition as per definition 2.1 using s ancillas, and r Tof
gates. Then, there is a circuit implementing a controlled quantum adder as per definition 2.8 using
n + s ancilla qubits and r + n Tof gates.
Although theorem 2.9 and corollary 2.10 can be used with any general adder, Gindey [Gid18]
adapted his temporary logical- AND construction to give an adder that uses only an additional n
Tof gates, and a single extra ancilla. We present his construction below.
Proposition 2.11 (Controlled adder - Gidney - with 1 extra ancilla [Gid18]) . There is a circuit
implementing an n-bit controlled quantum addition as per definition 2.8 using n + 1 ancilla qubits
and 2n Tof gates.
Proof. Figure 15 is taken from Gidney’s construction of a controlled adder building block. Here, we
can isolate what happens in the case of a single MAJ − UMA pair, and show what is the resultant
state. Apart from the Tof gates of the n MAJ blocks, we also require a Tof gate per UMA block to
perform the controlled addition, leading to 2 n Tof gates in total to execute a controlled adder in
this case.
· · ·
control control
ci ci
xi xi
yi (yi + (xi + ck) · control)
ci+1 ci+1
Figure 15: The controlled adder building block by Gidney [Gid18]
We now show a version of the CDKPM adder that can perform controlled addition with a single
ancilla qubit.
Theorem 2.12 (Controlled adder - CDKPM - with 1 ancilla) . There is a circuit implementing an
n-bit controlled quantum addition as per definition 2.8 using 1 ancilla qubit and 3n Tof gates.
Proof. Controlled addition can be achieved by slightly modifying the CDKPM circuit (see figure 8)
substituting the UMA gates with their controlled version given by figure 16. Overall, the consecutive
c
U
M
A
=
Figure 16: Controlled Unmajority gate.
application of MAJ and C-UMA gates acts as figure 17, thus determining the sought implementation
of a controlled addition.
While the Draper adder (as defined in corollary 2.7 employing three QFT’s) fits into the general
framework of corollary 2.10, an alternate construction can be derived using only a single ancilla.
14
