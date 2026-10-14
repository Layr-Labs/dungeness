---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 18
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 18

The text below is a page-delimited extraction of the unchanged source PDF.

perform the look-up, add the point to the quantum register, then uncompute the quantum look-up
to free the qubits for the expensive modular division. This requires us six look-ups (including
uncomputing) rather than just two, but uses no extra registers.
With a window size of ℓ, including sign bit, each look-up costs 4 ·2ℓ−1 T gates and T-depth.
The windowing saves us ℓ−1 point additions. If point addition costs A T gates, we would expect
ℓ≈lg(A/24) to be the optimal value, leading to a factor ℓ reduction in T-gate cost.
D Numerical results and interpolations
We also estimated the costs for the basic operations that comprise the elliptic curve addition.
With Q#, we counted resources for arithmetic operations for all bit sizes from 4 up to 64, then
for random bit sizes between 65 and 2048. Based on theoretical analysis and examining the best ﬁt,
we decided on the best model and then ﬁt the data with linear regression. Tables 2 and 3 show the
results.
For modular arithmetic, we counted resources for all bit sizes from 4 to 64, then the common
elliptic curve bit sizes 110, 160, 224, 256, 384, and 521. These were the only larger bit sizes we
estimated due to the high computational cost of performing these estimates. With linear regression
we estimated only the leading term of the cost growth. Table 4 contains these costs.
We found that addition with the DKRS adder had very diﬀerent depths for numbers with an
odd bitlength compared to an even bitlength. This behaviour is likely due to the structure of the
binary tree for carry bit propagation. Odd bitlengths were much cheaper, so we opted to simply
allocate an extra qubit to add two numbers of even bitlengths.
We also noticed that addition and modular addition are substantially more expensive when
controlled, while constant addition and modular doubling costs increase only negligibly. The
T-depth of the uncontrolled DKRS adder increases monotonically with bitlength. The data for the
controlled DKRS adder is much noisier. Hence, the apparent growth of the lg nterm is slower than
the controlled DKRS adder, which is nonsensical; this is likely just an artifact of the noise.
For the ﬁnal set of formulas for the entire cost of Shor’s algorithm, we extrapolated the costs for
a single point addition, then performed the same optimization as Section 6 describes. Though the
exact cost was not convex, it should be O(n/lg n) times the cost of a single addition, and indeed
such a curve ﬁt the data well ( r2 >0.98 for the depth and gate costs).
E Automatic compilation for aggressive T-count and T-depth
reduction
In this section, we motivate automatic compilation methods to drastically reduce the T-count and
the T-depth if we allow a signiﬁcant increase in circuit width.
The modular multiplication followed by an addition is one of the most costly operations in
the overall algorithm. It is implemented as a unitary U : |x⟩|y⟩|z⟩|0⟩↦→| x⟩|y⟩|(xy+ z) mod p⟩|0⟩
that adds the result of the multiplication of two numbers x and y onto a third number z, all
in Montgomery form with bit-width n and modulus p. We apply the following procedure to
automatically obtain a quantum circuit for this operation:
1. We generate logic networks over the gate basis {AND,XOR,INV}, called Xor-And-inverter
Graphs (XAGs), for the functions xymod p, (x+ y) mod p, and (x−y) mod p, where xand y
are integers in Montgomery form.
2. We apply the logic optimization method described in [ 33] to minimize the number of AND
gates in the XAGs.
3. The optimized XAGs are then translated into out-of-place quantum circuits using the method
in [19], which requires 4 T gates for each AND gate in the XAG. Optimizing these circuits
for depth requires roughly 2 qubits for each AND gate in the XAG, by using the AND gate
construction from Section 3.
18
