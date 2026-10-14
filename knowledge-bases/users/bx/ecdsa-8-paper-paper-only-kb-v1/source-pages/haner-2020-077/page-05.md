---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 5
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

ctrl
ck
xk
yk
ck+1 ··· ck+1
ck
xk
(x+ y)k
Fig. 1: Controlled addition block, adapted from [12].
An alternative is to “curry” the quantum addition circuit. In the DKRS adder, the qubits of
one of the two inputs are only used as controls for CNOT and Toﬀoli gates. We can replace these
with X and CNOT gates which are conditionally applied according to the bits of the classical
integer. A controlled classical addition with this method needs to control the entire curried circuit
(see Figure 2b), but we found that this is the most eﬃcient approach with the DKRS adder.
|0⟩
|x⟩
|ctrl⟩
n
n
c
+
c |0⟩
|x+ c⟩
(a) Copying the classical constant c is con-
trolled, followed by uncontrolled addition.
|x⟩
|ctrl⟩
n +c |x+ c⟩
(b) The addition circuit is curried for the
constant c, then the full circuit is con-
trolled.
Fig. 2: Two methods for controlling addition by a constant c.
Comparing integers. An addition circuit immediately gives a comparator by the one’s comple-
ment trick. For integers x and y represented in binary, if we let x′denote the one’s complement
(all bits ﬂipped), then ( x′+ y)′= x−y. If y >x, then x−y <0 and the leading bit of ( x′+ y)′
will be 1. Thus, to construct a comparator, we simply ﬂip all bits in x, compute the ﬁrst half of an
addition circuit, copy out the carry, then uncompute the addition circuit. With a control, we only
need to control the ﬁnal copy of the carry bit. We use this technique for comparators based on the
previous adders. DKRS provide a comparator which we did not use for ease of implementation.
Fan-out and fan-in of control qubits. When a single qubit controls multiple parallel gates,
they must be performed sequentially. To avoid this increase in depth, we opt to allocate extra
qubits and fan-out the control [ 22] to these qubits using CNOTs. Then these qubits can control all
the gates in parallel before we clear them again. For n simultaneous controlled gates, this requires
n auxiliary qubits and at most 4 n CNOT gates in depth ⌈lg n⌉, but no T gates. Our low-width
optimization does not do this.
The fanned-out auxiliary control qubits could be retained to control many gates, depending
on the application. Because the Q# language allocates qubits in a stack, this is often diﬃcult. A
function that allocates clean auxiliary qubits must restore them to the |0⟩state before returning.
Because of this diﬃculty and the low gate cost of fan-out, we do not make such optimizations.
To control a single gate with the logical AND of n qubits requires a fan-in of control qubits.
For low width, we use Barrenco et al.’s method [ 3], as RNSL did. This performs a multi-AND
in-place but with 8 n Toﬀoli gates and linear depth. If we instead allocate n−1 auxiliary qubits
and “compress” the controls with a tree of AND gates, it requires only n−1 AND gates and
AND-depth ⌈lg n⌉.
5
