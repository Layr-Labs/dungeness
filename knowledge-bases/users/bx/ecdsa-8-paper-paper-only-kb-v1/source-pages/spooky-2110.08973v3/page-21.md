---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 21
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 21

The text below is a page-delimited extraction of the unchanged source PDF.

Spooky pebbling the binary tree graph
While finding the minimum number of pebbles needed in the spooky pebble game is PSPACE-
hard to approximate in general, it is possible to find pebble and step efficient strategies for
specific graph topologies. The binary tree with directed edges from the leaves to the root is a
natural topology for algorithms like divide and conquer, where a problem is solved by combining
the results of two smaller sub-problems. Concrete algorithms with this structure include floating
point pairwise summation and computing Merkle trees [42, 43].
It is known thath+ 1 pebbles and Θ(n) steps are both necessary and sufficient to pebble
a binary tree of height h with n = 2 h −1 nodes in the irreversible pebble game [44]. In
[15], Král’ovič showed that(h+ Θ(log∗h)) pebbles are necessary and sufficient this task in the
reversible pebble game, wherelog∗ is the iterated logarithm function. Despite this there are
no known polynomial time pebbling strategies for the binary tree using the optimal number of
pebbles; the best known tradeoff is a strategy that uses(1 + ε)h pebbles and runs innO(log 1/ε)
steps [45]. We show the existence of a spooky pebbling strategy for the binary tree that uses the
same number of pebbles as the most efficient irreversible pebbling while only being aO(log n)
factor slower. Thus the spooky pebble game is almost as efficient as the irreversible pebble game
and is provably more efficient than the reversible pebble game on binary trees.
Theorem 5.5. There exists a spooky pebbling algorithm on the complete binary tree with
n= 2h −1 nodes that usesh+ 1 pebbles andO(nlog n) steps.
Proof. Before getting to the algorithm, we present the following subroutine:
1 fast_pebble (T ,h): // T is the root and h is the height of the tree
2 if( h= 1):
3 place (T )
4 else :
5 run fast_pebble ( T .l,h −1)
6 run fast_pebble ( T .r,h −1)
7 place (T )
8 remove (T .l)
9 remove (T .r)
The above subroutine uses at mosth+ 1 pebbles and2h+1 −1 steps to place a pebble at the
root of the tree while leaving ghosts at all other internal nodes. We will now use fast_pebble to
construct a recursive unpebbling algorithm for a complete binary tree with rootT and depthh:
1 U(T ,h) :
2 remove (T )
3 run fast_pebble ( T .l,h −1)
4 run fast_pebble ( T .r,h −1)
5 place (T )
6 remove (T )
7 remove (T .r)
8 run U(T .l,h −1)
9 run U(T .r,h −1)
We note thatU(T ,h) uses at mosth+ 1 pebbles; we do not need to removeT .l before step8 as
the pebble on this nodes is removed at the beginning of the recursive call. The number of steps
this algorithm takes follows the recurrence relation:
T(h) ≤2T(h−1) + 2h+2 + 2
21
