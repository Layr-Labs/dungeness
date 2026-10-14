---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 24
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 24

The text below is a page-delimited extraction of the unchanged source PDF.

where the subscriptℓ q denotes the temporary register storingJ.
This operation can be implemented directly using unary iteration. We first reversibly transform the
ℓq register as|ℓ t⟩|ℓq⟩ 7−→ |ℓt⟩|ℓt +ℓ q + 1⟩. UsingCtrlas the global control, pruned unary iteration over
the labelsk, k+ 1, . . . , Kthen produces, one value at a time, the control bitej =Ctrl∧[J=j]. When
this unary control is active, we swapSignandu j. After it finishes we restore theℓ q register to its original
value. Figure 9 illustrates this construction for the examplek= 5 andK= 8.
|Ctrl⟩
|ℓt⟩
|ℓq,>3⟩
|ℓq,3⟩
|ℓq,2⟩
|ℓq,1⟩
|ℓq,0⟩
|Sign⟩
|u5⟩
|u6⟩
|u7⟩
|u8⟩
+ +1 −1 −
Figure 9: Location-controlled swap circuit fork= 5 andK= 8. After computingJ=ℓ t +ℓ q + 1, pruned
unary iteration over the labels 5,6,7,8 selects the work qubit to be swapped withSign.
The unary iterator contributesK−k+O(1) Toffoli gates and 2(K−k) +O(1) CNOT gates, the
controlled swaps contributeK−k+O(1) Toffoli gates and 2(K−k) +O(1) CNOT gates. The reversible
transformations of theℓ q register contributeO(log 2 n) Toffoli/CNOT gates. Thus the location-controlled
Swapcircuit uses 2(K−k) +O(log 2 n) Toffoli gates and 4(K−k) +O(log 2 n) CNOT gates.
Location-controlledAdd,Subcircuit.We next describe the location-controlled addition and subtrac-
tion circuits. As a representative example, consider the operation
(Sign, r)←(Sign, r)−2ℓsr′,(3)
whereSignrecords the sign of the subtraction result. In terms of physical positions in the twoWork
registers, this operation acts only on the interval
L=ℓ t +ℓ q + 2, R=n+ 3−ℓ s.
That is, the relevant qubits areu L, . . . , uR inWork1andv L, . . . , vR inWork2; outside this interval all
qubits are left unchanged. The shift byℓ s is already reflected in the endpointR=n+ 3−ℓ s, so the
aligned bitsv L, . . . , vR represent the contribution of 2ℓsr′ to the subtraction. For a known active window
[k, K], we promise thatk≤L≤R≤K.
If the endpointsLandRwere fixed, the subtraction could be implemented by a ripple-carry subtractor
on the qubit pairs (uj, vj) forj∈[L, R] with a dedicated carry qubitcinitialized to|0⟩. For the subtraction
24
