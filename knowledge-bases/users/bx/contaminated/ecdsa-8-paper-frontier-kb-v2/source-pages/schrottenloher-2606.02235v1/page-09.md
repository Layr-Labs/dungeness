---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 9
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 9

The text below is a page-delimited extraction of the unchanged source PDF.

is the core component of the circuit. Notice that the inverse circuit will multiply
byx −1 instead. So, using the same circuit, we can implement both in-place mul-
tiplication steps found in Algorithm 1. The remaining multiplication, a modular
squaring at Step 10, is out-of-place, and therefore easier to implement.
We explain how to build this circuit from basic modular and non-modular
arithmetic circuits. The idea is taken from [14], which optimizes extended Eu-
clidean algorithms (EEA) usingdialogrepresentations. As we do not use the
same representation, we will not use the term “dialog” but the idea remains the
same.
3.1 Euclidean Algorithm
We start from a simple, but efficient, implementation of the Euclidean algorithm.
The key of this implementation is that, contrary to the usual Extended Euclidean
algorithm, it does not construct the B´ ezout coefficients (r, s). Instead, it just
remembers the choices that were made at each loop iterate, packing them into a
garbage bit-vector. Then, we canlaterreconstruct (r, s), gaining space compared
to a direct implementation. This is the first key idea from [14].
Algorithm 2Euclidean Algorithm
Parameters:number of iterations
Input:Integersu, v,uodd
Output:Garbage bit-vectorg
1:forA fixed number of iterationsdo
2:b 0 :=vmod 2
3:b 1 :=u > v
4: Storeb 0&b1 andb 0 ing
5:ifb 0&b1 then
6:u, v=v, u
7:end if
8:ifb 0 then
9:v−=u
10:end if
11:v=v/2
12:end for▷At the end,v= 0 andu= 1
We review the important properties of Algorithm 2.
First, its number of iterations. Letnbe the starting bit-size ofuandv.
Intuitively, each iteration will at least remove one bit of the registers at Step 11,
and with probability 1/2 depending on the value ofb 0, it will remove another bit
at Step 9. This means that on average, (uv) is multiplied by 1
2 × 1
2 + 1
2 × 1
4 = 3
8 .
So, the average number of iterations should beℓsuch that: 2n−ℓlog 2(8/3) =
0 =⇒ℓ= 2n
3−log2 3 ≃1.413n.
Experiments show that this is indeed the case. In addition, the number of
iterations follows a normal distribution with standard deviation≃0.6 √n. In
9
