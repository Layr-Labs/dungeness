---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 5
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

dialogin [14], which used this for polynomials, because it can contain a division
by 2, an inversion (swapping the integers), or an addition. The second circuit is a
B´ ezout reconstructionalgorithm which takes as input the sequence of operations
from the Euclidean algorithm, as well as a pair (r, s) (which should start at
(1,0) if we are invertingxmoduloq), and applies the appropriate operations
on (r, s). Essentially, this two-step process is splitting the EEA between the
input part and the B´ ezout coefficients. This has many advantages which are
detailed in Section 3: not only is the space reduced, but this point of view
allows to directly implement the in-place multiplication, saving several modular
multiplications.
The total space complexity of the point addition ends up being dominated by
the B´ ezout reconstruction step. As we observe in Section 3, in the most space-
optimized implementation, the sequence of steps of the EEA can be stored on
2.12n+O( √n) qubits. During the B´ ezout reconstruction step, one needs to store
in addition a pair of integers moduloq, ofnbits each. Therefore the circuit uses
at least 4.12n+O(√n) qubits. In our implementation, we use slightly more space
than this, leading to our 4.36n+O( √n) asymptotic. One should note that the
constant in theOcontrols the success probability of the algorithm on random
inputs, and we optimize it following experimental results.
Arithmetic Circuits.At this point, the cost of the point addition circuit will
depend on trade-offs in the circuits for unsigned arithmetic (in the Euclidean al-
gorithm) and modular arithmetic (in the B´ ezout reconstruction and elsewhere).
For unsigned arithmetic, we simply switch between the CDKM adder [5], the
Gidney adder [7] and a hybrid between the two, depending on the number of
ancilla qubits available. We also rely on Gidney’s low-space classical-quantum
adder [8]. For modular arithmetic, we introduce two levels of optimization which,
to the best of our knowledge, have not been described before, and could have ap-
plications in other quantum cryptanalysis circuits relying on modular arithmetic.
Contrary to most recent works [13,11,15], we do not rely on the Montgomery
representation of modular integers, instead optimizing the circuits as much as
possible under a standard representation of integers. The components that we
optimize are modular doubling and controlled modular addition, taken from [20].
We give a first batch of optimizations working for any modulusq, where com-
parisons are simplified by comparing the most significant bits only: the amount
of MSBs determines the success probability of the circuit. Then, we observe that
the prime insecp256k1is apseudo-Mersenneprime, of the form 2 u −fwhere
f≪2 u. This allows to further simplify the modular reductions which appear in
these circuits. The difference between these two levels of optimization explains
the difference betweensecp256k1and “any prime” reported in Table 1.
Implementation.We provide a complete implementation of the circuits described
in this paper using the python library Qarton. Our code is available at:
gitlab.inria.fr/capsule/qarton-projects/ec-point-addition
5
