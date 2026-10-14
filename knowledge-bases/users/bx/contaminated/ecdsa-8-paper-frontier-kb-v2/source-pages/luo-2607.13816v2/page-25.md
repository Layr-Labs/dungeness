---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 25
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 25

The text below is a page-delimited extraction of the unchanged source PDF.

in Equation (3), we first apply theUMA † cells from high to low, updateSignfrom the carry qubit, and
then apply theMAJ † cells from low to high to uncompute the carry.
It remains to coherently select the interval [L, R]. The endpoint registers storingLandRare obtained
from the length registers by reversible affine transformations, which are undone after the arithmetic block.
The circuit uses one accumulator bits, initialized to|0⟩. In theUMA † pass, the circuit scans the physical
positions from high to low, namelyj=K, K−1, . . . , k. For each scanned positionj, pruned unary
iteration on the endpoint registers coherently produces the two local controls
λj =Ctrl∧[R=j], µ j =Ctrl∧[L=j].
The circuit first updates the accumulator bys←s⊕λ j. If the updated value ofsis 1, the circuit
appliesUMA †(c, uj, vj); otherwise it does nothing on (c, uj, vj). After this controlled arithmetic cell, the
circuit updates the accumulator bys←s⊕µ j. Therefore, when the scan reachesj=R, the bitλ j flips
sfrom 0 to 1 before the arithmetic cell, so theUMA † cell atj=Ris applied. For positions strictly
inside the interval, the accumulator remains equal to 1, so the corresponding arithmetic cells are also
applied. When the scan reachesj=L, theUMA † cell is still applied, and thenµ j flipssback to 0. The
same update rule is used for every scanned positionj∈[k, K]. Before the active interval is reached, all
arithmetic cells are disabled, so the carry qubitcremains equal to 0 at the interval entrance.
After theUMA † pass,cstores the carry bit of the selected subtraction. We updateSignby
Sign←Sign⊕c.
TheMAJ † pass visitsj=k, k+ 1, . . . , K. At each position, the accumulator is first updated by
s←s⊕µ j. If the updated value ofsis 1, the circuit appliesMAJ †(c, uj, vj). It then updates the
accumulator bys←s⊕λ j. Therefore theMAJ † cells are applied exactly forj∈[L, R], andsandcare
restored to|0⟩at the end.
Figure 10 illustrates the complete pattern for the examplek= 5 andK= 7.
Finally, we explain how the controlledMAJandUMAcells used above are implemented. We do not
add the location-control bit to every gate in the cell; only the Toffoli gate that updates the carry qubit
is controlled. Figure 11 shows the corresponding controlled cells.
The gate count consists of the following contributions:
•Generating [L=j] and [R=j] during both scans requires four applications of unary iteration.
They use 4(K−k) +O(1) Toffoli gates and 8(K−k) +O(1) CNOT gates in total.
•Applying one controlledUMA † cell at each position in the high-to-low scan uses 4(K−k) +O(1)
Toffoli gates and 2(K−k) +O(1) CNOT gates.
•Applying one controlledMAJ † cell at each position in the low-to-high scan uses 3(K−k) +O(1)
Toffoli gates and 2(K−k) +O(1) CNOT gates.
•ComputingLandRfromℓ q andℓ s, and subsequently restoring these registers, usesO(log 2 n)
Toffoli and CNOT gates.
25
