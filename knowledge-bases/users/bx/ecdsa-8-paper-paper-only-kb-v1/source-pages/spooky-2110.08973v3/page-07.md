---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 7
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 7

The text below is a page-delimited extraction of the unchanged source PDF.

Proposition 2.1(Implicit in [9]). Let M be an irreversible sequential machine that computes a
function f with T steps usingS bits. Let PT/S be a (spooky) pebbling strategy for the line of
length T/S that runs inτT/S steps and uses at mostsT/S concurrent pebbles. Then there exists
a quantum circuit that can computef with O(S·τT/S) gates andO(S·sT/S) qubits.
We now more formally define the irreversible, reversible, and spooky pebble games that we
will use throughout this paper. Here the△operator denotes the symmetric difference.
Definition 2.2.The irreversible pebble game is a one player game on a DAGG= (V,E) where
the goal is to place a pebble on exactly the nodesT ⊆V called targets with out-degree zero. A
pebbling (strategy) is a list of subsets ofV. P = [P0,..., Pτ] where P0 = ∅and Pτ = T. A
strategy is valid as long as
• ∥Pi△Pi+1∥= 1, and
• If v∈Pi+1 \Pi, then parents(v) ⊆Pi.
We can analyze a pebbling by looking at the number of pebbles and steps it requires.
Definition 2.3.The number of stepsT(P) in a pebbling strategyP = [P0,..., Pτ] is τ.
Definition 2.4. The number of pebbles S(P) in a pebbling strategy P = [ P0,..., Pτ] is
maxi∈[τ]∥Pi∥.
When restricted to reversible computation, we can modify Definition 2.2 to get a pebble
game that naturally models the restrictions imposed by reversibility.
Definition 2.5.The reversible pebble game has the same setup as the irreversible pebble game
in Definition 2.2. A strategy is valid as long as
• ∥Pi△Pi+1∥= 1,
• If v∈Pi+1 \Pi, then parents(v) ⊆Pi, and
• If v∈Pi \Pi+1, then parents(v) ⊆Pi.
The pebble game capturing ghosting admits better pebbling strategies than are possible in
the reversible pebble game, assuming we are concerned with the number of qubits rather than
the total space complexity. Given an irreversible pebbling, we can exactly characterize when it
produces a ghost.
Definition 2.6.The ghosting sequenceG(P) = [G0,..., GT(P)] is defined recursively byG0 = ∅
and Gi+1 = (Gi ∪{v∈Pi|parents(v) ̸⊆Pi}) \Pi+1.
The ghosting sequence cumulatively tracks the locations where pebbles were removed without
access to their parents. These are exactly the steps that prevent a strategy from being a valid
strategy for the reversible game; a valid reversible pebble game strategy is exactly a strategy
with a ghosting sequence consisting only of empty sets. The spooky pebble game relaxes this
condition to only requiring thelast ghost set to be empty. Note that ghosts can be removed by
placing a pebble over them.
Definition 2.7.The spooky pebble game has the same setup as the irreversible pebble game in
Definition 2.2. A strategy is valid as long as
• ∥Pi△Pi+1∥= 1,
• If v∈Pi+1 \Pi, then parents(v) ⊆Pi, and
• In the ghosting sequenceG(P), the final ghost setGτ = ∅.
7
