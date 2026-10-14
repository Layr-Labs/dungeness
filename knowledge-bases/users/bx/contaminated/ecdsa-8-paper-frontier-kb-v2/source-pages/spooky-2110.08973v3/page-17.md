---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 17
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 17

The text below is a page-delimited extraction of the unchanged source PDF.

Now that we have established the equivalence between the cost of a treeT(n,s) and T(n,s),
we want to prove some things about the structure of this tree. Whens< 2 and s<n we know
that T(n,s) = ∞, so whenever possible a tree will never have a sub-tree with such parameters
as nodes. This means that any treeT(n,2) must haveT(1,1) as its right child. By construction,
this means that the right-depth of any node in the treeT(n,s) is at mosts−1. Note that the
cost of all the intermediate nodes is only a function of the total number of nodes in the tree.
What follows is a collection of technical lemmas that give the number of nodes inT(n,s) with
specific left and right depths. Together they let us characterize the number of leaves inT(n,s)
with each cost. This lets us construct a lower bound on the cost ofT(n,s), which in turn is a
lower bound on the total number of steps needed to unghost a line of lengthn using at mosts
pebbles.
Lemma 4.19. Let T(n,s) be the tree in Corollary 4.18. LetX be a leaf ofT(n,s) with the largest
value forL(X), m= L(X), andX′be any other leaf whereL(X′) <m −1. Then R(X′) = s−1.
Proof. Assume thatR(X′) < s−1. Note thatX must be a left child, as it is the node with
largest left depth. Then we could replace the parent ofX with its other child and replaceX′
with an intermediate node whose left child isX and right child isX′. Doing so must reduce the
left depth ofX by at least one and does not change the left depth of any other node in the tree,
so the new tree has a lower cost. But this is a contradiction sinceT(n,s) is supposed to be the
tree with the lowest cost.
The above lemma tells us a surprising amount about the structure ofT(n,s). Since all nodes
X where L(x) <m −1 and R(X) <s −1 cannot be leaves, these nodes all have left and right
children. We can therefore derive exactly how many leavesT(n,s) must have with each left depth
less thanm.
Lemma 4.20.Let T(n,s) be the tree in Corollary 4.18 andm be the largest value ofL(N) for
N ∈T(n,s). If m> 1, then we know that the number of leaf nodesT(n,s) possesses with left depth
L<m is
(L+s−2
s−2
)
.
Proof. By Lemma 4.19 we know that no node with a left depth less thanm−1 and a right
depth less thans−1 can be a leaf. Thus all such nodes must have left and right children. We
will identify each node with a string ofl’s andr’s indicating which directions are taken from the
root of the tree to arrive at that node. Since all nodes with right depths or larger have cost
infinity, we know that all nodes with right depths−1 must be leaf nodes. Thus each leaf node
with left depth less thanm−1 must be a right child (otherwise, their sibling would have right
depth s) and be identified with a string ending in anr. There are
(L+s−2
s−2
)
strings containingL
copies ofl and s−1 copies ofr that end in anr. This exactly corresponds to the number of leaf
nodes with left depthL<m −1; each of these leaf nodes must exist in the tree because none of
their ancestors can be leaves by Lemma 4.19, and there can be no other leaves with this left
depth unless there is a leaf with cost∞.
Since, by Lemma 4.19, all nodes with left depthL= m−2 and right depthR<s −1 must
exist in the tree and cannot be leaves, each of these nodes has a left child. There is a bijection
between the number of leaves with left depthL= m−1 and these children, as their rightmost
descendants are exactly the leaf nodes with left depthm−1. Since there are
(m+R−2
R
)
nodes
with left depthm−2 and right depthR<s −1, there are
s−2∑
R=0
(
m+ R−2
R
)
=
s−2∑
R=0
(
m+ R−2
m−2
)
=
(
m+ s−3
m−1
)
=
(
L+ s−2
s−2
)
leaf nodes with left depthm−1.
17
