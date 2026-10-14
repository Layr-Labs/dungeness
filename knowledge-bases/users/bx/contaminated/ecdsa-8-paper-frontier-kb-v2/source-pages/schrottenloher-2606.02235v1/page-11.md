---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 11
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 11

The text below is a page-delimited extraction of the unchanged source PDF.

X
X
Fig. 1.“Compression” circuit mapping 3 pairs (b0, b0&b1) into 5 bits. On valid inputs,
the last bit is always 0 and can be reused.
The second key idea of [14] is that these updates are alllinearoperations
controlled by the bitsb 0 andb 0&b1. Therefore, if we start from (r, s) := (y,0) for
anyymoduloq, we will end up with (r, s) = (0, yx−1 modq): we have performed
both the inversionandan in-place multiplication without additional cost.
Algorithm 3B´ ezout reconstruction algorithm.
Parameters:primeq, number of iterations
Input:Integersr, s, garbage bit-vectorg
1:foriin reversed(range(iterations))do
2: Obtainb 0 andb 0&b1 for iterationifromg
3:s←2smodq
4:ifb 0 then
5:s←s+rmodq
6:end if
7:ifb 0&b1 then
8:r, s←s, r
9:end if
10:end for
Our implementation follows Algorithm 3. We read the bits in the reversed
order in which they were produced. The consequence is that, on input (y,0), we
obtain (0, yxmodq) and notyx −1. Notice that in this reconstruction algorithm,
we need modular arithmetic operations, contrary to the original EEA.
Remark 1.Running side by side Algorithm 2 and Algorithm 3 essentially gives
a reasonably efficient variant of binary GCD algorithm as used in previous im-
plementations of elliptic curve point addition [15,11]. However these implemen-
tations needed to run the algorithm once forwards, obtain a modular inverse,
and run the algorithm backwards to erase the garbage. The out-of-band recon-
11
