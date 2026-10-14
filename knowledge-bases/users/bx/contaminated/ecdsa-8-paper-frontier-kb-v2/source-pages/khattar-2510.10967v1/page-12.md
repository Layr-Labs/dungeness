---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 12
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 12

The text below is a page-delimited extraction of the unchanged source PDF.

12
• Doubling: The operationb(z) ← b(z)/z corresponds to:
Mdouble =

1 0
0 1 /z

• Inversion: The operation(a(z), b(z)) ← (b(z), a(z)) corresponds to the matrix:
Minvert =

0 1
1 0

• Addition: The operationb(z) ← b(z) − c · a(z), wherec ∈ Fq, corresponds to the matrix:
Madd(c) =

1 0
−c 1

In this case, theDialog is simply the list of coefficientsci and the swap decisions from each step, such that it
defines the ordered list of transformation matricesτ i. The name Dialog itself is a mnemonic for the core arithmetic
operations involved: Doubling (or shifting),Inversion (or swap), andAddition/subtraction, and the representation
is similar to a logarithm because it makes multiplication and division easy but addition and subtraction hard. For
two input polynomials of degree up ton − 1, the Dialog consists of2n field elements.
A naïve quantum circuit for constructing the dialog would require2nb qubits to store and manipulate the remainder
polynomials r−1 = A(z), r0 = B(z), r1, . . . rm and another 2nb qubits to store the dialog, resulting in overall qubit
count of4nb + O(log2 n). In order to reduce the qubit counts to2nb + O(log2 n), we once again use a register sharing
technique by observing a key invariant of the constant-time EEA [17]:In each iteration, as one field element is
computed and appended to the Dialog, the total number of coefficients required to represent the active polynomials,
ri−1(z) and ri(z), decreases by one. This inverse relationship between the size of the Dialog and the size of the
remaining polynomial data allows for an elegant quantum circuit that dynamically reclaims and repurposes qubits.
Our construction uses a shared quantum register,poly, which stores the coefficients of the remainder polynomials
ri−1(z), ri(z) and another quantum register,dialog, that stores the growing Dialog. At any point in time, we have the
invariant: len(poly) + len(dialog) = 2n such that the total space occupied is2nb + O(log2 n). The architecture can
be described as follows:
1. Initialization: The poly register is initialized to hold the coefficients of the two input polynomials,a(z) and
b(z), stored from opposite ends of the register. This creates a layout with a central padded region:
[a0, a1, . . . , ana, 0, 0, 0, bnb, . . . , b1, b0]
2. Constant-Time Iteration Loop: The circuit proceeds for a fixed2n iterations, where n is the maximum
degree of the input polynomials. This ensures the algorithm completes for any input. Inside each iteration
i=1, 2, . . . ,2n:
• The control flow (e.g., the decision to swap the logical polynomials) is managed by the integer delta and the
constant term ofb(z) (i.e., poly[−1]). A swap is performed by efficiently reversing the entire poly register,
an operation implementable with a sequence of len(poly)// 2 CSWAP gates.
• The field element coeff for the update step is calculated from the constant terms of the active polynomials
(poly[0] and poly[−1]).
• The polynomial subtraction,b(z) ← b(z) − coeff · a(z), is performed in-place. As per [17, Theorem A.1],
after i iterations, we have
2 deg(ak) ≤ 2d − 1 − i + δn
2 deg(bk) ≤ 2d − 1 − i − δn
When coeff̸= 0, after the conditional swap, we always haveδi ≤ 0 such thatdeg(b(z)) > deg(a(z)). Thus,
in the shared register representation, we perform poly[n− j − 1] −= coeff∗ poly[j] ∀j ∈ [0, len(poly)+δi
2 ).
