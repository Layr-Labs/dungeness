---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 7
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 7

The text below is a page-delimited extraction of the unchanged source PDF.

7
Sequential Syndrome Computation:We now iteratei from 1 to m, utilizing a singleb-qubit ancilla register:
(2a) Check if marked in Sparse Dicke State:Check whether indexi is contained in the Sparse Dicke state
and record the outcome in a qubityi. Naively, this requires performing ab-bit comparison with each of
the ℓ registers per iteration, requiring a total ofm · ℓ · b gates acrossm iterations. However, since we are
sequentially comparing each of theℓ registers in the Sparse Dicke State with consecutive classical constants
i = 1, 2, . . . , m, we can use a unary iteration [30, 31] circuit to merge adjacent comparisons and get a total
cost ofm · ℓ gates across allm iterations.
(2b) Error Generation:Apply Gi on thei-th qubit of the mask register|yi⟩ to temporarily generate thei’th
error term|ei⟩b using theb-qubit ancilla register.
(2c) Syndrome Update: Compute the contribution ofei to the syndrome register|s⟩ by coherently adding
bi · ei to |s⟩ (where bi is thei-th column ofBT ).
(2d) Measurement-Based Uncomputation: Immediately uncompute the ancilla|ei⟩ using MBU [25, 26].
The b qubits are measured in the X basis, recording the classical outcomeci. This resets the ancilla for
the next iteration but introduces a known phase kickback(−1)ci·ei.
At the end of the iteration, we simply do a measurement-based uncomputation of the Sparse Dicke state and
perform phase fixups corresponding to the error locations during the reversible decoding step. By reusing a
single ancilla register across allm iterations, we avoid themb-qubit overhead of the original DQI construction.
The final state of the system is
lX
k=0
wkqm
k

X
|e|=k
 mY
i=1
˜gi(ei)(−1)ci.ei
!
|BT e⟩nb. (6)
• Stage 3: Phase Fixups via Reversible Decoding: In the original DQI construction [4], a reversible
decoder was used to uncompute the explicit error register|e⟩. In our construction, the error register was already
uncomputed via MBU in Stage 2. However, we must now correct the phase errors(−1)c·e introduced by the
measurements. Here, we perform reversible decoding using the syndrome register|s⟩ = |BT e⟩. We sequentially
compute each decoded error termei and use the measurement resultsci to fix the phase error(−1)ci.ei. For
the Optimal Polynomial Intersection (OPI) problem, this requires a reversible implementation of a decoder
for Reed-Solomon codes, like the Berlekamp-Massey algorithm [6] or the Extended Euclidean Algorithm-based
decoder [7, 32]. The final state of the system after this step is:
lX
k=0
wkqm
k

X
|e|=k
 mY
i=1
˜gi(ei)
!
|BT e⟩nb ≡ |]P(f)⟩nb (7)
• Stage4: FinalTransformationandMeasurement: Afterthesuccessfulphasefixups, thesyndromeregister
is left in a state that is the Quantum Fourier Transform of the desired output state. To obtain the final state, an
Inverse Quantum Fourier Transform (IQFT) is applied to then qudits of the syndrome register. This produces
the final DQI state:
|P(f)⟩ =
X
x
P(f(x))|x⟩. (8)
B. Efficient Quantum Circuits for Extended Euclidean Algorithm
TheExtendedEuclideanAlgorithm(EEA)isacornerstoneofcomputationalnumbertheoryandacriticalsubroutine
in algorithms for both classical and quantum computing [33]. While often introduced for integers, its principles
generalize to other Euclidean domains like univariate polynomials with coefficients in a finite field, which is relevant
to Reed-Solomon decoding. Given two polynomials,A(z) andB(z), Euclid’s algorithm iteratively generates a sequence
of remainder polynomialsri(z) using the recurrenceri−2(z) = ri−1(z)qi(z)+ ri(z), wherer−1(z) = A(z), r0(z) = B(z)
and the quotientqi(z) is chosen such thatdeg(ri(x)) < deg(ri−1(x)). The EEA is an extension to Euclid’s algorithm,
which, alongside this sequence, also maintains two corresponding cofactor sequences,ui(z) and vi(z), that are updated
at each step to preserve a crucial linear relationship known as Bézout’s identity. At every iterationi, the triplet
(ri(z), ui(z), vi(z)) satisfies the invariant:
A(z)ui(z) + B(z)vi(z) = ri(z). (9)
