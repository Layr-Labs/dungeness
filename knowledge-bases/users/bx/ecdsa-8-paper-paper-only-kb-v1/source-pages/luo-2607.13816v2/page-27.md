---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 27
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 27

The text below is a page-delimited extraction of the unchanged source PDF.

k≤ℓ t ≤J≤Kfrom the active window under consideration. For eachj∈[k, K], define the masked bit
aj =Ctrl∧[j≤J]∧u j.
Also define bits
zj =
K^
h=j
¬ah.
Thusz j = 1 means that no valid nonzero bit occurs among positionsj, j+ 1, . . . , K. If the highest valid
nonzero position ism, then
zK =···=z m+1 = 1, z m =···=z k = 0.
If no valid nonzero bit exists in the window, then allz j are equal to 1.
The highest position can be written using a telescoping XOR. We first XOR the classical constant
Kinto the length register. Then, forj=K, K−1, . . . , k+ 1, wheneverz j = 1, we change the current
candidate fromjtoj−1 by XORing the classical constantj⊕(j−1). Finally, ifz k = 1, then the entire
window contains no valid nonzero bit, and we clear the remaining candidatekby XORingk. Equivalently,
the value written by the subroutine is
Lnew =K⊕
KM
j=k+1
zj ·

j⊕(j−1)

⊕z k ·k,
where a term such asz j ·Cmeans that the classical bit stringCis XORed into the length register
controlled onz j. If the highest valid nonzero position ism, the expression telescopes tom. If no such
position exists, it telescopes to zero.
It remains to implement the constant writes controlled by the bitsz j without storing all of them in
clean ancillae. Borrow dirty qubitsg k, . . . , gK, which will be restored at the end. Forj > k, letVj denote
the Clifford operation that XORs the classical constantj⊕(j−1) into the length register, and letV k
denote the operation that XORsk. Since eachV j is a product of CNOT gates,V 2
j =I. Assume for the
moment that we can perform the transformation
gj ←g j ⊕z j (j=k, . . . , K).
Then the desired controlled write is implemented by placing this transformation between two uses ofV j
controlled by the borrowed qubit:
V gj
j , g j ←g j ⊕z j, V gj
j .
Indeed, if the initial value of the borrowed qubit isG j, then the two controlled writes are
V Gj
j V Gj⊕zj
j =V zj
j ,
so the unknown initial value cancels. After all constant writes are completed, we perform the same
transformation again to restore everyg j to its original value. Figure 12 illustrates this method for the
examplek= 5 andK= 7.
27
