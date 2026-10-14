---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 18
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 18

The text below is a page-delimited extraction of the unchanged source PDF.

Lemma 4.21. Let T(n,s) be the tree in Corollary 4.18 andm be the largest left depth of any
node inT(n,s) and m′ be the largest left-depth of any node inT(n′,s). If m′>m then n′>n.
Proof. Assume thatn′≤n. By Lemma 4.20 for allL<m , T(n,s) and T(n′,s) must have the same
number of leaf nodes with left depthL. This means thatT(n,s) must have at leastn−n′more
leaves with left depthm than T(n′,s) has with left depth at leastm. We construct a new tree
T∗
(n′,s) by takingT(n,s) and removingn−n′leaves with left depthm by replacing their parent
with its right child. The treeT∗
(n′,s) represents a valid binary tree and its cost is less than that of
T(n′,s) since the two trees have the same total number of nodes, the same number of leaves with
any left depth less thanm, andT∗
(n′,s) has no leaves with left depth larger thanm. This implies
that T(n′,s) was not constructed according to Corollary 4.18, giving us a contradiction.
Lemma 4.22. Let T(n,s) be the tree in Corollary 4.18 andn be the smallest value such that
T(n,s) contains a node with left depthm+ 1. Then T(n−1,s) contains exactly
(m+s−2
s−2
)
leaves with
left depthm and n= 1 +
(m+s−1
s−1
)
.
Proof. Assume for the sake of contradiction thatT(n,s) contained at least two nodes with left
depth m+ 1. By our choice ofn we know thatT(n−1,s) contains no nodes with left depthm+ 1.
By Lemma 4.20 we know thatT(n,s) and T(n−1,s) have the same number of leaves with each left
depth less thanm. This means the difference in cost betweenT(n,s) and T(n−1,s) must be at
least m.2 But there is another treeT∗
(n,s) that costs onlym−1 more thanT(n−1,s) constructed
by replacing the leftmost leaf ofT(n−1,s) with an intermediate node whose children are both
leaves. SinceT∗
(n,s) has cost less thanT(n,s), we get a contradiction.
Now T(n,s) must contain exactly one node with left depthm+ 1. By Lemma 4.20 this means
that it contains exactly
(L+s−2
s−2
)
leaves with left depthL, so the total number of leaves inT(n,s)
is:
n= 1 +
m∑
L=0
(
L+ s−2
s−2
)
= 1 +
(
m+ s−1
s−1
)
This means thatT(n−1,s) must have
(m+s−1
s−1
)
leaves. All of these leaves have left depth at most
m by Lemma 4.21. So Lemma 4.20 gives us thatT(n−1,s) has:
(
m+ s−1
s−1
)
−
(m−1∑
L=0
(
L+ s−2
s−2
))
=
(
m+ s−1
s−1
)
−
(
m+ s−2
s−1
)
=
(
m+ s−2
s−2
)
leaves with left depthm.
Lemma 4.23. Let T(n,s) be the tree in Corollary 4.18 and
(m+s−1
s−1
)
≤n. Then the cost ofT(n,s)
is Ω(mn).
2T(n,s) must have two leaves with left depthm + 1while T(n−1,s) has one fewer node that must have left depth
m. Since T(n,s) has one more intermediate node, its cost is at leastm more thanT(n−1,s).
18
