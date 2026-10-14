---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 45
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 45

The text below is a page-delimited extraction of the unchanged source PDF.

The upshot is that given any classical circuit implementing n strings addition, one can implement
signed integer arithmetic, encoding them in 2’s complement.
Proposition A.6. For any two n bits strings x|n, y|n, corresponding to the signed integers x and y
in the 2’s complement convention, one has x|n + y|n = (x + y)|n+1, where the the left-hand side
is the n strings addition and the right-hand side is the string corresponding to the signed integer
(x + y) in the 2’s complement convention.
Proof. One has to consider four separate cases. In the first case x, y≥ 0, one gets the usual unsigned
addition. When x ≥ 0 and y <0 one has
lhs = x + |y| = x − |y| = (x − |y|)|n+1 (12)
employing proposition A.5 in the last equality. Similarly, when x <0 and y ≥ 0, one has
lhs = |x| + y = |y| −x = (y − |x|)|n+1 . (13)
At last, when x, y <0, one notice that
lhs = |x| + |y| = |x| + |y| + 1 = |x| −|y| = |x| + |y| . (14)
45
