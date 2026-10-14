---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 8
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 8

The text below is a page-delimited extraction of the unchanged source PDF.

Automatic optimization. The multiply-then-add operation is a very costly component in the
point addition circuit. We explore what is possible when reducing its T-depth and T-gate count.
Appendix E shows the results for a compilation using the method from [ 19] after automatic
optimization [ 33] of a logic network generated from the operation. We achieve extremely low
T-depth and T-count, but the number of logical qubits increases signiﬁcantly. We leave further
exploration of such techniques for future work.
4.2 Modular inversion
Modular inversion uses variants of the extended Euclidean algorithm (EEA). The EEA repeatedly
divides integers. For two n-bit integers, we might expect each division requires O(n2) operations
and, in the worst case, we need O(n) divisions. In practice the complexity is smaller, because
the complexity of the divisions becomes smaller in the course of the algorithm. Unfortunately, to
exploit this fact, the circuit must be dynamic: The number of divisions and the circuit for each
division depend on the inputs. We cannot build such a quantum circuit, since we cannot observe
the input (it may be in superposition).
We considered several approaches, but found that RNSL’s circuit is the best. Appendix A.2
details our reasoning. However, we found several improvements to it. Their circuit models an
algorithm of Kaliski [ 18], which applies a round operation (Algorithm 7a) for up to 2 n iterations.
Conditional logic selects one of four diﬀerent cases that can occur in each round. As a quantum
circuit, this requires applying all four possible rounds, each with a diﬀerent control. Algorithm 7b
shows our alternative formulation based on swaps.
Figure 6a shows the round operation of RNSL’s quantum circuit implementation of Kaliski’s
algorithm. This circuit repeats the controlled additions, doublings, and halvings, with diﬀerent
registers playing the role of input or output. Our method performs each of these operations once,
using controlled swaps to arrange inputs and outputs for the respective case. The lower auxiliary
bit and |mi⟩uniquely specify the round and we use these bits to control a swap. This leads to
Figure 6b. A controlled n-bit swap is approximately the same cost as a controlled n-bit cyclic shift.
Correcting pseudo-inverses in parallel. Classically, the Kaliski algorithm uses only k rounds,
with n≤k≤2n for n-bit integers. RNSL’s quantum circuit executes 2 n rounds, controlled in such
a way that only k actually modify the input. This produces an auxiliary qubit counter with a value
of 2n−k and a pseudo-inverse output of x−12−n+k mod p for an input x. We want to output the
Montgomery inverse x−12n mod p, which requires correcting the pseudo-inverse.
Instead of a separate doubling circuit like the one RNSL use, we add a doubling operation to
each division round. After copying out the pseudo-inverse, during the subsequent uncomputation
we use the same control that the round operation uses: in each of the 2 n rounds, either we double
the output register or perform a division round. These can be done in parallel, which improves the
depth without increasing the total gate count. The result is that we compute 2 n−k doublings,
exactly what is needed to correct the pseudo-inverse.
Modular division. In elliptic curve point addition, the inversion is only necessary to compute a
division. To divide an integer xby y modulo a prime p, RNSL ﬁrst invert y in an auxiliary register,
perform the multiplication by the result, then invert y again to uncompute the auxiliary qubits as
shown in Figure 8a.
Because the inversion uses Bennett’s method, we pebble in the same way as the multiply-then-
add circuit. To save qubits, we notice that after the inversion, three registers contain known values
of 0, 1, and the modulus p. We can clear these auxiliary qubits with at most 3 n parallel X gates,
then re-use them for modular multiplication. Denoting the inverse and multiplication operations
with auxiliary qubits by invA and mulA, respectively, Figure 8b depicts a full modular division.
The pseudo-inverse correction is compatible with modular division.
8
