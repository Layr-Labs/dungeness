---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 16
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 16

The text below is a page-delimited extraction of the unchanged source PDF.

Theorem 4.13.For any line of lengthn, any pebble bounds, and any positive integerm where
n≥
(m+s−2
s−2
)
+ 1, a spooky pebbling of that line with at mosts pebbles uses at leastΩ(mn) steps.
One difficulty in analyzing our recurrence relation is that the choice ofk that minimizes this
expression is not obvious, making it difficult to directly compute this function. Instead we will
describe a family of related recurrence relations for a fixed choice ofn and s using trees withn
leaf nodes and right-depths−1 to determine the choices ofk. The lowest valued recurrence in
this family gives us the value ofT(n,s).
Definition 4.14.Let T be a binary tree,T .l be the left subtree, andT .r be the right subtree.
Let |T |L be the number of leaves in a given binary tree. If|T |L = n then we can define the
recurrence relation:
TT (n,s) =



2 s≥1 and n= 1
∞ s< 2 and s<n
2|T .l|L −2 + TT .l(|T .l|L,s) + TT .r(|T .r|L,s −1) o.w.
(2)
We can think of this as being Equation (1) except thatk is selected as the number of leaves
in the left sub-tree rather than the value that minimizes the expression. This lets us fixn and
s in order to see how different choices ofk lead to different values for the recurrence. Then the
minimum of TT (n,s) over all trees must equal toT(n,s). Instead of directly computing the
recurrence, we can computeTT (n,s) for a specific treeT by assigning a cost function to binary
trees that is equal toTT (n,s).
Definition 4.15.Let N be any node in a tree. We letR(N) denote the right-depth ofN, which
is equal to the number of times you must take right children to reachN from the root. We
likewise defineL(N) as the left-depth ofN.
Definition 4.16.For any depth bounds, thecost of a binary treeCs(T ) is equal to the sum
of the costs of its nodes. Each non-leaf node of a tree has cost−2. Any leaf nodeN where
R(N) <s has a cost of2L(N) + 2 while a leaf node whereR(N) ≥s has a cost of∞.
Lemma 4.17.The cost of the treeCs(T ) is equal toTT (|T |L,s).
Proof. We prove this by structural induction on the tree. In the base case we have a tree that
is a single leaf. Then Cs(T ) = TT (n,s) = 2 as desired. Now consider an arbitrary treeT .
By the inductive hypothesis we can assume thatCs(T .l) = TT .l(|T .l|L,s) and Cs−1(T .r) =
TT .r(|T .r|L,s −1). Given that the cost of a tree is the sum of the costs of its nodes,Cs(T ) =
2|T .l|L −2 + Cs(T .l) + Cs−1(T .r), as all nodes inT .l have their left depth increased by one, all
nodes inT .r has their right depth increased by one, and the root ofT has a cost of−2. By our
inductive hypothesis, this implies that
Cs(T ) = 2|T .l|L −2 + TT .l(|T .l|L,s) + TT .r(|T .r|L,s −1) = TT (|T |L,s).
If we have a tree with a leaf node whereR(N) ≥s then the tree has a cost of infinity and
TT (n,s) must reach the base case wheres≤1 and s<n when evaluating that node.
Corollary 4.18. Let T(n,s) be the tree withn leaf nodes that minimizes Cs(T(n,s)). Then
T(n,s) = Cs(T(n,s)).
It is easier to reason aboutCs(T(n,s)) than T(n,s) as we can start with an arbitrary tree with
nleaf nodes and show how it would be possible to mutate that tree and reduce its cost without
computing the full value of the recurrence relation.
16
