---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 25
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 25

The text below is a page-delimited extraction of the unchanged source PDF.

25
In A1 we prove thatE[Pm
i=1 Xi] < (1
2 + n
m )m = ( 1
2 + R)m. Asymptotically limb→∞ t = ( 1
2 +
q
R
2 (1 − R
2 )m leading
to the asymptotic scaling
lim
b→∞
P
 mX
i=1
Xi ≥ t
!
≤ exp

−2
 s
R
2

1 − R
2

− R
!2
m

 (116)
In the regime whereR = n
m ≈ 0.10557, we get an exponential lower bound on the number of trials of
#trials ≥ e0.02786m (117)
IV. ASYMPTOTICALLY OPTIMAL QUANTUM SPEEDUP
To achieve the speedup of Theorem I.1, we have to use methods for the circuit implementation that are not
necessarily optimal at the smaller problem sizes we envision for near-term applications. We describe these alternative
implementations in Section IVA. Then in Section IVB we observe Theorem I.1 as a corollary of this implementation
(on the quantum side) along with the lower bounds on runtime of XP that was shown in Theorem III.7.
A. Asymptotically Optimal Implementation
While Section II focused on optimizing constant factors for finite-size implementations, we now analyze the asymp-
totic complexity of DQI applied to the OPI problem. We demonstrate that under certain conditions, the DQI
algorithm can be implemented using a quantum circuit with a number of gates that is nearly linear in the problem
size m. We use the notationeO(m) to hide factors polylogarithmic inm.
We first establish the complexity of the key algebraic subroutines required. These complexities are well-established
in classical computer algebra and apply over arbitrary finite fieldsFq.
Lemma IV.1 (Fast Algebraic Subroutines). Let m be the problem size parameter. The following tasks can be
computed reversibly usingeO(m) field operations inFq:
1. Multipoint Polynomial Evaluation (MPE): Evaluating a polynomial of degree< mat m points.
2. Reed-Solomon (RS) Decoding: Decoding an RS code of lengthm up to half its minimum distance.
Proof.
1. Fast algorithms for MPE utilize a divide-and-conquer strategy. The complexity isO(M(m) logm) field opera-
tions, where M(m) is the cost to multiply two degreem polynomials [42, Chapter 10]. SinceM(m) = eO(m)
using fast multiplication algorithms [43–45], the total cost iseO(m) field operations.
2. The key equation for RS decoding can be solved using the Fast Extended Euclidean Algorithm (Fast EEA),
which runs inO(M(m) logm) = eO(m) field operations [42, Chapter 11]. Subsequent steps (root finding and
error evaluation) also takeeO(m) field operations using fast MPE [46].
These algorithms are algebraic and can be implemented reversibly on a quantum computer.
We now analyze the overall complexity of DQI. The result depends critically on the efficiency of the objective
function implementation and the size of the field relative tom.
Theorem IV.2. Consider the Optimal Polynomial Intersection (OPI) problem overFq with m constraints and
n = Rm variables (whereR ∈ (0, 1) is constant). The DQI algorithm can be implemented by a quantum circuit using
eO(m) elementary quantum gates, provided that:
1. The field sizeq satisfies log q = O(polylog(m)) (i.e., the bit lengthb = eO(1)).
2. The subsetsFi are structured such that an oracleUi for objective functionfi, defined asUi |x⟩ = fi(x) |x⟩, can
be implemented by a quantum circuit usingeO(1) gates.
