---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 44
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 44

The text below is a page-delimited extraction of the unchanged source PDF.

Remark A.2 (Binary encoding of a positive integer) . Any bit string can be understood as the
binary representation of a given positive integer number via the following bijective function
{0, 1}n ↔ {0, 1, . . . ,2n − 1}
x 7→
n−1X
k=0
xk2k
If not stated differently, we shall often equate the decimal and binary representation of a given
positive integer number. Note that bit string addition is precisely built in such a way that the string
x + y corresponds to the positive natural number x + y; the extra bit is added to take into account
the overflow of the carry when (x + y) ≥ 2n. Moreover, one can easily check that x + x = (2n − 1).
Proposition A.3. Given x, y∈ {0, 1, . . . ,2n − 1} two positive integer, one has that (x − y)n+1 =
(x < y).
Proof. Assume that xj = yj for any k < j < nand the k-th bit is the most significant one such
that xk ̸= yk. According to definition 1.5, one has dj = bj = bk+1 for any k < j≤ n. Therefore
if x > yone must have xk = 1 and yk = 0, thence dn+1 = bk+1 = 0. On the contrary, one has
dn+1 = bk+1 = 1.
Remark A.4 (Binary encoding of signed integer) . Any signed integer number can be encoded as a
bit string via the following bijective function
{0, 1}n+1 ↔ {−2n, . . . ,0, 1, . . . ,2n − 1}
x 7→ −xn2n +
n−1X
k=0
xk2k
y|2 ←[ y
where y|n+1 denotes the string encoding the signed integer y in the 2’s complement, i.e.
y|n+1 =
(
y y ≥ 0
|y| y <0 ,
(10)
and y and |y| are the string encoding the positive numbers y and |y| according to remark A.2.
According to this convention, the most significant bit of the string encodes sign (y).
Proposition A.5. For any two n bits strings x, y with corresponding unsigned integers x and y,
one has
x − y = (x − y)|n+1 , (11)
where the left-hand side is the n strings subtraction and the right-hand side is the string corresponding
to the signed integer (x − y) in the 2’s complement convention.
Proof. One has to check two separate cases. First case, when x ≥ y, one has that ( x − y) is a
positive number and x − y correspond to the string (x − y). In the other case, when x < y, one
gets from the definition of n strings subtraction that
x − y = x + y
= y + x + 1
= (y − x) + 1
= (y − x)
= |x − y| .
44
