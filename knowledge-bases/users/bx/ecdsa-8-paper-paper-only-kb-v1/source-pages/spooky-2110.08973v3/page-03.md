---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 3
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 3

The text below is a page-delimited extraction of the unchanged source PDF.

Source Game Pebbles Steps
irreversible 2 O(n)
[11] spooky 3 O(n2)
Corollary 3.8 spooky 2 + 1/ε O (n1+ε/ε)
[9] reversible O(ε21/εlog n) [14] O(n1+ε)
[11], Corollary 3.9 spooky O(log n) O(nlog n)
[15] reversible O(nε) O(21/εn)
Corollary 3.7 spooky O(nε)† O(n/ε)
Lemma 3.5 spooky s O (mn)‡
† When (2/ε)2/ε ≤n
‡ Where
(m+s−2
s−2
)
≥n
Figure 1: Summary of results on pebbling the line of lengthn. All asymptotics
hold simultaneously forn→∞ and ε→0.
quadratic blowup in the running time, which is impossible for reversible computation [15]. The
spooky pebble game was recently extended to work on arbitrary DAGs in [19, 20], similar to the
reversible pebble game. These works developed a SAT solver that can compute the minimum
runtime necessary to solve the spooky pebble game on an arbitrary DAG. In [20] the authors
recently proved that deciding if a DAG can be pebbled withs pebbles is a PSPACE-complete
problem, although their hard case requires a DAG with maximum in-degrees−1.
Our results We build on the spooky pebble game framework introduced by Gidney ([11]) and
prove asymptotically tight upper and lower bounds on spooky pebbling the line. We do this by
proving that—for any pebble bound—there always exists an optimal strategy that has a specific
form, constructing such an algorithm, and analyzing a recurrence relation to lower bound the
runtime of such algorithms.
We delineate the entire achievable frontier of the spooky pebble game and our tight trade-off
bounds can be applied in many different regimes. For example, for anyε∈(0,1], any classical
computation that runs inT time withS space can be simulated on a quantum computer using
only O(T/ε) steps andO(T1+εS1−ε) qubits. This is an exponential improvement inε over the
reversible bound in [15]. We also show that any computation can be simulated inO(T1+εS−ε/ε)
steps with only O(S/ε) qubits, which is fewer qubit than would be possible (independent of
the time bound) with reversible pebbling [21, 22, 15]. Interestingly, whenε= 1/log(T/S), this
matches the (unobtained) lower bound for reversible pebbling proved in [15].
We then show that any irreversible pebbling can be converted to a spooky pebbling using
only one additional pebble. This gives us that, in general, the number of pebbles needed for
the spooky pebble game is PSPACE-hard to approximate. Finally we discuss the spooky pebble
game on directed acyclic graphs (DAGs) where we show that it is possible to spooky pebble the
complete binary tree of heighth(i.e., n= 2h−1 nodes) usingh+1 pebbles andO(nlog n) steps.
This is less pebbles than is possible in the reversible pebble game addressing an open question
posed in [20] regarding efficient algorithms for the spooky pebble game on trees.
2 Preliminaries
Reversible Computation We say that a computation isreversible if, after every time step,
there is a unique predecessor state for the computation; a Turing machine that moves from
left to right inverting the bits on its tape is reversible while one that sets its tape to zero is
3
