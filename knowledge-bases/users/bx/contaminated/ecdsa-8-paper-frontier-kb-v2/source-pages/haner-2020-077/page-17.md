---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 17
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 17

The text below is a page-delimited extraction of the unchanged source PDF.

The advantage of the comb technique is that it saves precomputation. We only precompute one
table and use it for the entire computation. Unfortunately for the quantum case, precomputation is
essentially free because it is entirely classical, but look-ups are expensive. The comb technique does
not reduce the number of table look-ups, since we must do a separate look-up for each index kj.
Further, eﬃcient in-place point doubling is unlikely, since it implies eﬃcient in-place point
halving. Thus, doubling points in the comb would require some pebbling technique which would
likely add signiﬁcant depth or width costs.
B Modular division and addition
For elliptic curve addition, we only need to divide integers and copy the result to a blank output,
but other applications may wish to construct a circuit that, given registers containing x, y, and z,
will compute yx−1 + z.
We might simply invert, multiply, and then add the output of the multiplication instead of
copying. However, doubling the output to correct the pseudo-inverse while uncomputing will also
multiply z by a factor of 2 2n−k. To correct for this, we can repeatedly halve z during the forward
computation of the modular inverse. This means that while we compute the modular inverse, we
control a modular halving of the register containing z by the counter, which will halve z exactly
2n−k times. Then we multiply the pseudo-inverse by y and add the result to the register with z,
producing the state
⏐⏐x−122n−k mod p
⟩
|y2n mod p⟩
⏐⏐z22n−k + x−1y22n−k mod p
⟩
. (4)
From here, if we perform controlled modular doublings of the register containing zas we uncompute
the inversion circuit, this will correct both z and the pseudo-inverse of x, producing the desired
output.
C Analysis of windowed arithmetic
A quantum look-up to N elements requires 4N T-gates [2]. To optimize window costs, we balance
this cost against the operations we save.
Multiplication. Section 4.1 describes a single windowed multiplication round. For n-bit integers
with window size k, repeating this round ⌈n/k⌉times performs the full multiplication. Since the
quantum look-up will cost 4 ·2k T gates [2] and uncontrolled n+ k-bit addition costs O(n+ k) T
gates, we expect the optimal window size to be approximately k= O(lg n). The total multiplication
cost is still O(n2) because we only window addition by p, not addition of the quantum register
y. Compared to un-windowed add-and-halve multiplication, windowing should save a factor of
roughly 1
2 + O( 1
lg n). Similar reasoning suggests savings of 1
2 + O( 1
lg lgn) in depth.
Numerical estimates show a window size of k= c1 lg n+ c2 optimizes T-count, where 0.68 ≤
c1 ≤0.75 and 0.12 ≤c2 ≤0.78, and 1.97 lg lgn−1.11 optimizes T-depth. At the scale we estimate,
this is only noticeable in the leading coeﬃcient of the cost. We found a 22% reduction in T-depth
at 384 bits, for example.
Windowing adds a signiﬁcant cost of roughly n+ k auxiliary qubits, but the full elliptic curve
point addition circuit has enough unused auxiliary qubits during any multiplication that this does
not make a diﬀerence.
Point addition. Windowing requires 2 extra registers as the cache to load the precomputed
points. We use the components of the second point three times during point addition (see Figure
9). We could perform the look-up once and keep the values, increasing total circuit width by two
registers. Alternatively, we can ﬁt the look-ups within the existing space. As Figure 9 shows, at
every point where x2 or y2 are added, the circuit has spare auxiliary qubits available. Thus, we can
17
