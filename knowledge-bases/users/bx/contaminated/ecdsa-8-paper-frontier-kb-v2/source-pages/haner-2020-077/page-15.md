---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 15
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 15

The text below is a page-delimited extraction of the unchanged source PDF.

RNSL use a similar round-based construction, which implements a reversible binary extended
Euclidean algorithm. As with multiplication, the primary diﬀerence between the PZ division and
the RNSL division is that PZ’s is based on doubling and integer long division, while RNSL’s is
based on halving and binary operations. The PZ inversion leaves only O(lg n) auxiliary qubits,
while RNSL creates 2 n+ O(lg n) auxiliary qubits, but PZ has a higher depth and gate cost.
Naively, the PZ approach uses 5 n qubits, though they show that, with ﬁdelity loss on the order
of O(n−3) per round, they require only 2 n+ 8√n+ O(log n) qubits. The RNSL approach uses 6 n
qubits. We choose to use the RNSL algorithm. It is exactly correct, so it can be used for higher
depth algorithms, and the total T-cost and depth are less than half of the PZ approach.
A.3 Recursive GCD Algorithms.
There are several sub-quadratic GCD algorithms (such as [ 7]). These work by deﬁning a series of
2 ×2 matrices Tn such that TnTn−1 ···T1(u,v)T will map integers u and v to the nth step of the
Euclidean algorithm. These can be computed and multiplied together recursively.
Adapted to quantum circuits, these approaches require quantum matrix multiplication. We
could ﬁnd no eﬃcient method to do this in-place, meaning that each recursive call would require a
new set of auxiliary qubits to store the matrix output. This would quickly overwhelm our qubit
budget. The base case of [7] is nearly identical to our approach for a single round.
One of the primary advantages of [ 7] is that the recursive process allows much of the arithmetic
to be done with small integers which ﬁt into the registers of classical CPUs. All the qubits in our
model of a quantum computer are identical, so it has no caching or register issues. If quantum
technologies arise with diﬀerent kinds of qubits (perhaps a “memory” with higher coherence times
but lower gate ﬁdelity), then recursive GCD algorithms should be revisited. It is also possible
that the speciﬁc structure of the matrices in this approach permit an easy, in-place multiplication
circuit. We leave this to future work.
A.4 Alternate curve representations
Projective coordinates. Projective coordinates use equivalence classes ( X : Y : Z) of triples
(X,Y,Z ) to represent an elliptic curve point, where ( X1,Y1,Z1) ∼(X2,Y2,Z2) iﬀ there is some
non-zero constant c such that X1 = cX2, Y1 = cY2, and Z2 = cZ2. These can be used with
many diﬀerent families of curves. Projective coordinates lend themselves to eﬃcient, inversion-free
arithmetic, which is appealing for classical computers.
Projective coordinates do not give a unique representation of each point, which Shor’s algorithm
requires to ensure history independence and thus proper interference of states in superposition.
Dividing by the Z coordinate produces a unique representation but requires an expensive division.
It is an open problem to provide a unique projective representation with division-free arithmetic.
Another issue is that the classical elliptic curve formulas, naively adapted to quantum circuits,
operate out-of-place. An out-of-place addition circuit is easy to adapt into an in-place addition
circuit. If we can construct a circuit U+Q to add a point Q, we can construct a circuit U−Q, and
we can construct an in-place point addition as shown in Figure 11 up to a ﬁnal swap of the two
qubit registers. This doubles the cost of point addition.
⏐⏐P
⟩
|0⟩
n
n +Q −Q† |0⟩
⏐⏐P + Q
⟩
Fig. 11: An in-place point addition from out-of-place.
This technique requires a unique representation. If ( P + Q) −Q does not have the same
representation as P, we cannot cancel them out. Thus, for any current algorithm to compute
15
