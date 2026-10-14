---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 36
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 36

The text below is a page-delimited extraction of the unchanged source PDF.

6.4 Resource estimates for Shor’s ECDLP circuit
For the full ECDLP attack, we do not repeat the controlled point-addition circuit bit-by-bit for all 2n
control bits. Instead, we follow the signed-window technique of [HJN +20, Section 5.1]. Namely, we
partition the 2ncontrol bits arising in the double-scalar multiplication into windows of sizew, and
implement each window by one signed windowed point addition.
In the signed-window construction, one of thewbits is used as a sign bit, while the remainingw−1
bits address a precomputed table of point multiples. As shown schematically in Fig. 10 of [HJN +20],
one such windowed point addition uses the arithmetic core of an affine Weierstrass point addition. The
coordinates of the selected precomputed point are obtained through three table queries, and its sign is
handled by one modular negation. In our space-optimized circuit, these three queries are implemented
by five sequential table look-ups. 3 Since the dominantn 2 term in our Toffoli accounting comes from
modular divisions, multiplications and squaring, replacing the classically known addend by an addend
obtained from the look-up table does not change the asymptotic scaling.
To obtain a clean asymptotic bound, we choose window sizew= 2 log 2 n. The five sequential ta-
ble look-ups contribute 5·2 w Toffoli gates to each windowed point addition. The full double-scalar
multiplication uses approximately 2n/wwindows, so its dominant Toffoli count becomes
2n
w

1003n2 + 5·2 w +O(nlog 2 n)

= 1008 n3
log2 n +O(n 2).
Forn= 256, following the analysis in [BZG +26], the Toffoli count of the complete Shor ECDLP
circuit is estimated as
28·

5·2 16 +Q A

.(8)
Here,Q A denotes the Toffoli count of a single controlled affine point-addition circuit. For a window size
ofw= 16, the number of signed-window point additions is 2n
w −4 = 28. The five sequential table look-ups
described above incur an additional 5·2 w Toffoli gates per window, which becomes 5·2 16 whenw= 16.
Substituting our concrete value ofQ A(256) shows that our algorithm requires 2 30.63 Toffoli gates for the
curve secp256k1.
Finally, we note that compression techniques and multi-run tradeoffs [Eke19] could potentially yield
further improvements to the constant factors in our overall resource estimates.
Acknowledgments
We thank Pierre-Luc Dallaire-Demers for pointing out an error in an earlier version of the EEA step bound
proof, which we have replaced with a matrix–continuant proof based on a finite polyhedral antinorm
certificate; see Appendix A.1. This work was supported by the Innovation Program for Quantum Science
and Technology (Grant Number 2024ZD0300500). ZY, ZW, YS and TL are supported by the National
Natural Science Foundation of China (Grant Numbers 62372006 and 92365117).
3The circuit first queries (x 2, y2), thenx 2, and finally (x 2, y2). If two freen-qubit registers were available, the two
coordinates in each (x 2, y2) query could be loaded together. Since only one freen-qubit register is available in our space-
optimized circuit, each (x2, y2) query is split into two sequential look-ups, giving 2 + 1 + 2 = 5 look-ups in total.
36
