---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 19
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 19

The text below is a page-delimited extraction of the unchanged source PDF.

Proof. By Lemma 4.20, Lemma 4.21, and Lemma 4.22, we know that for allL∈{0,1,2,...,m }
the number of leaf nodes with left depthL is
(L+s−2
s−2
)
. Thus the cost of these leaf nodes is at
least:
m∑
L=0
(2L+ 2)
(
L+ s−2
s−2
)
.
Expanding the above summation yields:
2(m+ 1)(m(s−1) + s)
s(s−1)
(
m+ s−1
s−2
)
.
Using that
(n
k−1
)
= k
n−k+1
(n
k
)
and s≥2, this is at least:
2(m(s−1) + s)
s
(
m+ s−1
s−1
)
= 2
(m(s−1)
s + 1
)(
m+ s−1
s−1
)
≥(m+ 2)
(
m+ s−1
s−1
)
.
By Lemma 4.20 and Lemma 4.22, ifn=
(m+s−1
s−1
)
+ k then the remainingk leaves must all have
left depth larger thanm. Thus the total cost of the leaves is at least:
(m+ 2)
(
m+ s−1
s−1
)
+ 2(m+ 1)k≥(m+ 2)n.
There aren−1 intermediate nodes with cost−2 so the total cost of the tree must be at least:
(m+ 2)n−2(n−1) = mn−2.
Which isΩ(mn) as desired.
By applying Lemma 4.23 to lower bound the cost of trees and Lemma 4.17 to apply this
lower bound to Equation (1), we obtain the following corollary:
Corollary 4.24.The number of steps needed to unghost a line of lengthn≥
(m+s−1
s−1
)
with s
pebbles isΩ(mn).
By applying Theorem 4.11 to Corollary 4.24, we get Theorem 4.13.
5 Spooky pebbling beyond the line
In Section 3 and Section 4 we discussed how the spooky pebble game can be applied to simulate
arbitrary irreversible sequential computation on a quantum computer. While this gives us very
general results, additional structure on the classical computation can lead to more efficient
simulation. Here we consider computation that can be expressed using a dependency graph—
such as boolean circuits, straight line (or oblivious) programs, and data-independent memory
hard functions (e.g. [35, 36, 37, 3, 38, 7, 39]). When considering a pebbling of a DAG, each
pebble represents only a single word rather than an entire copy of the computation’s state.
It turns out that there is a close relationship between the number of pebbles required in the
irreversible and spooky pebble games.
19
