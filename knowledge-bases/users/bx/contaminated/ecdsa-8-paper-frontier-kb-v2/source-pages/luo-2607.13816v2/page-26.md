---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 26
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 26

The text below is a page-delimited extraction of the unchanged source PDF.

|Ctrl⟩|ℓt⟩|ℓq,>3⟩|ℓq,3⟩|ℓq,2⟩|ℓq,1⟩|ℓq,0⟩|ℓs,>3⟩|ℓs,3⟩|ℓs,2⟩|ℓs,1⟩|ℓs,0⟩
|0⟩|Sign⟩|c= 0⟩|u7⟩|v7⟩|u6⟩|v6⟩|u5⟩|v5⟩
+
n+ 3−ℓs
+2
UMA†
UMA†
UMA†
UMA†
UMA†
UMA†
MAJ†
MAJ†
MAJ†
MAJ†
MAJ†
MAJ†
n+ 3−ℓs
−2 −
Figure 10: Location-controlled subtraction circuit fork= 5 andK= 7. TheUMA † pass computes the
carry,Signis updated fromc, and theMAJ † pass restores the carry qubit.
|s⟩
|a⟩
|b⟩
|c⟩
|s⟩
(a) ControlledMAJcell.
|s⟩
|a⟩
|b⟩
|c⟩
|s⟩ (b) ControlledUMAcell.
Figure 11: Controlled arithmetic cells used in the location-controlled add/sub circuits.
Adding these terms, the location-controlledSubcircuit implementing Equation (3) uses 11(K−k) +
O(log2 n) Toffoli gates and 12(K−k) +O(log 2 n) CNOT gates.
Location-controlled length-update circuit.Finally, we describe the length-update circuit. We
focus on updatingℓ t; the circuit for updatingℓ r′ is analogous. At the end of one EEA iteration, after the
full swap ofWork1andWork2, the left part ofWork1stores the current value oft, while the left part of
Work2stores the current value oft ′. LetL new = len(t), Lold = len(t′). Since the value stored inℓ t before
the update isL old, it suffices to implement
ℓt ←ℓ t ⊕L old ⊕L new.
Thus the length update is reduced to two serial constant-XOR writes: first XOR the old length, and then
XOR the new length.
We first describe the subroutine for XORingL new intoℓ t. This subroutine finds the highest valid
nonzero position among the qubitsu k, . . . , uK. Only positions in the left region not occupied byr ′
should be inspected. LetJ=n+ 3−ℓ r′ be the right boundary of this valid region with the promise
26
