---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 8
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 8

The text below is a page-delimited extraction of the unchanged source PDF.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
0
a b c d e
Figure5: Aspookypebbling
of the line. Here◦indicates
a pebble and∼indicates a
ghost.
Note that by construction, the spooky pebble game always lies
somewhere between the reversible and irreversible pebble games.
Therefore it is natural to compare it to these other pebble game
and investigate when its behavior is closer to that of reversible or
irreversible pebbling.
Figure 5 gives an example of a spooky pebbling on the line of
length 5 using only 3 pebbles. Note that this models the same
computation performed in Figure 4. Each numbered step in Figure 5
corresponds to the state of the quantum circuit in Figure 4 after the
corresponding numbered gate is applied; a wire on row c in Figure 4
occurs exactly at the same numbered steps as a pebble at column
c in Figure 5 and corresponds to storing the valuef3 ◦f2 ◦f1(x) in
quantum memory within both models. In the reversible pebbling
game, this task requires 4 pebbles. The ability to ghost pebbles
and remove the ghosts at later steps lets us use one fewer pebble,
showing that the spooky pebble game can be used to save qubits.
Rather than describe a pebbling as a list of pebbled nodes, we
will sometimes describe algorithms that generate these lists. These
algorithms feature the functions “place” and “remove”. Thet’th call
to these functions defines the value ofPt from Pt−1 as follows:
• place(vi): (Pt) = (Pt−1 ∪{vi})
• remove(vi): (Pt) = (Pt−1 \{vi})
Intuitively, the place instruction creates a pebble on a node while the remove instruction destroys
that pebble. For the spooky pebble game, ghosts are implicitly created by remove instructions
according to Definition 2.6.
3 Spooky pebbling the line
Before constructing spooky pebbling algorithms, we first define two useful related pebbling tasks.
Definition 3.1.An unpebbling is a sequence of place and remove instructions that, assuming
the graph starts with pebbles exactly on all nodes with out-degree zero (and no ghosts), results in
the graph having neither pebbles nor ghosts on any of its nodes.
An unghosting is a sequence of place and remove instructions that, assuming the graph starts
with ghosts exactly on all target nodes (nodes with out-degree zero) and no pebbles, results in the
graph having neither pebbles nor ghosts on any of its nodes.
While an unghosting assumes that the graph only starts with ghosts on nodes with out-
degree zero, these sequence of place and remove instructions will remove any additional ghosts
that start elsewhere on the DAG, as pebbles must be placed on all nodes in the graph to remove
ghosts on the out-degree zero nodes. In the rest of this section we restrict our attention to
the line graphG= ({v1,...,v n},{(v1,v2),..., (vn−1,vn)}). We will canonically refer toP as a
pebbling algorithm,U as an unpebbling subroutine, andUg as an unghosting subroutine.
The spooky pebbling algorithms we discuss in this paper all have a similar recursive form.
They start by using a sequence of alternating place and remove instructions to place a pebble on
some vertexvk, leave a pebble on this vertex to recursively pebble the rest of the line, and use an
unpebbling subroutine to remove the pebble placed atvk. In Section 4 we prove the existence of
8
