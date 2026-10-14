---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 12
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 12

The text below is a page-delimited extraction of the unchanged source PDF.

so we extrapolated from the costs for smaller lookup tables. With Q#, we calculated the cost of
a point addition on the three NIST curves [ 34] P256, P384 and P521, using 8-bit look-ups, then
subtracted the cost of six 8-bit look-ups and added the cost of six ℓ-bit look-ups to get the cost of
point addition with an ℓ-bit window. We multiplied this cost by the number of windows dividing
2n to get the full cost of Shor’s algorithm for ECDLP. From this we manually selected optimal
window sizes. We can use n instead of n+ 1 because the order of each NIST curve is less than its
modulus [34].
Table 1 shows our results together with those of RNSL [ 27] for comparison. Their circuits use
fewer than 2 Toﬀoli gates per time step on average, so we assume that with 8 extra qubits (c.f.
Section 3) they can use Toﬀoli gates of T-depth 1. Our optimization for the number of qubits is
shown in the row labeled Low W. Since RNSL optimize for the same metric, those results allow a
direct comparison. We were able to improve on RNSL’s circuit in all metrics. For P256, we reduce
the number of logical qubits from 2338 to 2124, while reducing the T-depth and T-count by factors
of 54 and 119, respectively.
Additionally, we report more signiﬁcant improvements over RNSL’s work in depth and T-count
when optimizing for those. For 521-bit moduli, the improvement is a factor of 13,792 in depth for
an increase of 22% in qubits, or a 463 factor reduction in T-gates for a 12% increase in qubits.
Circuit Window Gates Depth Width
Size Cliﬀords Measure T Total T All gates Qubits
256-bit modulus
RNSL – – – 1.60 ·239 – 1.69 ·236 – 2338
Low W 19 1.32 ·234 1.76 ·226 1.72 ·232 1.45 ·235 1.98 ·230 1.89 ·232 2124
Low T 19 1.75 ·233 1.95 ·227 1.08 ·231 1.80 ·234 1.44 ·229 1.85 ·231 2619
Low D 15 1.04 ·234 1.61 ·228 1.34 ·232 1.40 ·234 1.12 ·224 1.40 ·227 2871
384-bit modulus
RNSL – – – 1.44 ·241 – 1.51 ·238 – 3492
Low W 21 1.46 ·236 1.23 ·229 1.51 ·234 1.57 ·237 1.68 ·232 1.77 ·234 3151
Low T 19 1.05 ·235 1.28 ·229 1.74 ·232 1.10 ·236 1.21 ·231 1.31 ·233 3901
Low D 15 1.73 ·235 1.34 ·230 1.13 ·234 1.17 ·236 1.23 ·225 1.48 ·228 4278
521-bit modulus
RNSL – – – 1.81 ·242 – 1.91 ·239 – 4727
Low W 22 1.85 ·237 1.59 ·230 1.82 ·235 1.98 ·238 1.99 ·233 1.09 ·236 4258
Low T 20 1.45 ·235 1.49 ·230 1.00 ·234 1.57 ·236 1.40 ·232 1.54 ·234 5273
Low D 15 1.10 ·237 1.70 ·231 1.43 ·235 1.48 ·237 1.13 ·226 1.27 ·229 5789
Table 1: Resource estimates for Shor’s full algorithm to compute the ECDLP. RNSL results are
taken from [27]. Rows labeled Low W/Low T/ Low D show estimates for circuits minimizing width,
T gate count and total depth, respectively.
Asymptotic formulas. We ran resource estimates for the various components of the elliptic
curve point addition circuits on a range of input bit sizes. We then determined models for ﬁtting
the data with linear regression and deduced asymptotic formulas for the costs of these operations
parameterized by the bit size n. Tables 2, 3 and 4 in Appendix D show the results of our experiments.
Table 4 also shows such formulas for a full signed windowed elliptic curve point addition and the
full circuit of Shor’s algorithm using such point addition. The results show that our circuit optimized
for low width can solve the ECDLP on an n-bit elliptic curve with about 8 n+ 10.2 ⌊lg n⌋−1 logical
qubits using roughly 436n3 −1.05 ·226 T-gates at a T-depth of 120n3 −1.67 ·222. The total number
of gates is 2900 n3 −1.08 ·231 with depth 509n3 −1.84 ·227.
Our circuits optimized for a low number of T gates require about 10 n+ 7.4 ⌊lg n⌋+ 1.3 qubits
and need 1115n3/lg n−1.08 ·224 T gates with T depth 389n3/lg n−1.70 ·222. Optimizing for low
12
