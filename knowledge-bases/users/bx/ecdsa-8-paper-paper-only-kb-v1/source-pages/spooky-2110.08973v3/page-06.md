---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 6
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 6

The text below is a page-delimited extraction of the unchanged source PDF.

1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17
1 1 1 1 1 1
2 2 2
3 3 3
4 4
5
a
b
c
d
e
Figure 4: Qubit efficient computation ofF(x) = f5 ◦f4 ◦f3 ◦f2 ◦f1(x) using ghosting. Again the•on the
classical wire above theEfi gates represents a controlled application of the componentZ gate rather than a
controlled application of an entire module.
Figure 4 shows how theseG and Ef gates can be applied to compute a function with less
qubits than would be possible using reversible simulation. This application is general: we
can think of a functionf as mapping a computer from its current logical configuration to its
configuration at the next time step. Since the measured valuebmust be stored from the time a
value is ghosted until the time when its ghost is removed, we are not able to reduce the overall
space complexity of the simulation; we are only able to reduce the number of required qubits.
Gidney’s original formulation of the spooky pebble game only produced a ghost when the
returned valueb ̸= 0 since when b = 0 no phase is added [11]. However, we will apply theG
gate on groups (registers) of qubits and the probability that all measured qubits yield zero will
be negligibly small. As such, we say that a ghost is always created when we apply theG gate.
Pebble games The concept of interweaving computation, uncomputation, and ghosting to
efficiently simulate classical computation can be perfectly encapsulated by an appropriate pebble
game. In a pebble game we are given a DAG where the nodes represent the variables involved in
a computation and the edges show the dependencies for computing these variables. For example
the computationc= a+ b can be represented with three nodes fora,b,c and edgesa→c and
b →c. A pebble can be placed on a node to indicate that the variable is currently stored in
a register for the computation. Thus a pebble can be placed on nodec only when there are
already pebbles ona and b. Additional restrictions on when pebbles can be placed or removed
create different pebble games that can be used to simulate irreversible, reversible, or quantum
computation with ghosting.
Such graph representations naturally characterize computations such as straight line pro-
grams, circuits, and data-independent cryptographic functions acting on words (registers) of
size w. In this setting, pebble games directly model time-space trade-offs—as a pebbling of the
DAG for a functionf with s pebbles placed concurrently andτ steps corresponds to a way to
compute f with O(ws) bits inO(τ) steps.
While pebble games are defined for general DAGs, it is possible to think of each pebble
as representing a snapshot of the entire state of an arbitrary sequential computation and then
represent the computation as a pebble game on a line. If you can construct a pebblingPn that
works on the line of lengthnin τn steps and uses at mostsn concurrent pebbles, this leads to a
naive way to simulate a computation that requiresT time andS space inO(S·τT) steps1 and
O(S·sT) space (or qubits). A more clever way to apply pebbling to simulation involves assigning
S states to each pebble, which lets us pebble a shorter line without increasing the asymptotic
space needed per pebble or the time needed per step.
1There is a multiplicative term ofS here because each state must be copied before simulating the next step.
6
