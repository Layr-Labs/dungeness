---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 20
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 20

The text below is a page-delimited extraction of the unchanged source PDF.

Spooky pebbling from irreversible pebbling
We start by showing a general strategy that can be used to convert any irreversible pebbling
into a spooky pebbling that uses at most one additional pebble. This result is a special case of
Theorem 1 in [19, 20] which presents a generalization of this argument for DAGs with multiple
target nodes (nodes with out-degree zero). For completeness we show the proof below.
Lemma 5.1. If a DAGG with n nodes and one target can be pebbled in the irreversible pebble
game usingT steps ands pebbles, then it can be spooky pebbled usingO(nT) steps and at most
s+ 1 pebbles.
Proof. Let P be an irreversible pebbling ofGthat usesspebbles. We will construct the following
spooky pebblingPs that uses at mosts+ 1 pebbles. Ps first simulatesP, which since we are
operating in the spooky pebble game, may leave some ghosts behind. Additionally the first time
that Ps places a pebble at any nodevi, we pushvi onto an initially empty stack. OncePs has
placed a pebble at the target nodevt, it removes all other pebbles (leaving a large number of
ghosts) and repeats the following procedure until the stack is empty: We pop the top element
off of our stack and call itvg. If vg does not contain a ghost, we continue to the next element in
the stack. Once we find avg that contains a ghost, we havePs simulate P until vg is pebbled
again, leaving ghosts on some nodes.Ps then removes the pebble atvg (without creating a
ghost) and then removes all pebbles other thanvt, possibly addling ghosts. By our choice of
vg, future iterations of this procedure cannot result in a ghost on a priorvg, so this procedure
terminates in less thann iterations with pebbles only onvt and no ghosts. SincePs is replaying
steps fromP with at most one additional pebble onvt, it will use at mosts+ 1 pebbles.
Note that sinceT is without loss of generalityΩ(n), we can say that the above procedure
also runs in timeO(T2). Since any spooky pebbling is also an irreversible pebbling, the above
lemma is sufficient to give us a nearly tight two sided bound on the minimum number of pebbles
needed in the spooky pebble game.
Corollary 5.2.Let G be a DAG that requiress pebbles in the irreversible pebble game. The
fewest pebbles needed for the spooky pebble game onG is eithers or s+ 1.
DemaineandLiuprovedthatdeterminingthefewestpebblesneededintheirreversiblepebble
game is PSPACE-hard to approximate.
Proposition 5.3(Theorem 13 in [40]). The minimum number of pebbles needed in the irreversible
pebble game on DAGs withn nodes, a single target, and maximum in-degree 2 is PSPACE-hard
to approximate to within an additiven1/3−ε for anyε> 0.
By combining Proposition 5.3 with Corollary 5.2, we see that finding even approximate min-
imum pebble spooky pebbling algorithms for arbitrary DAGs solves a PSPACE-hard problem.
Thus unless P = PSPACE, there can be no polynomial time algorithm that generates mini-
mum pebble spooky pebbling strategies on arbitrary DAGs. Quist and Laarman showed the
PSPACE-completeness of this problem in [20] through a different reduction; however, going
through Proposition 5.3 extends this result to a restricted subset of DAGs (those with maxi-
mum in-degree two with a single sink node) and shows that even approximating the minimum
number of pebbles to an additive factor ofn1/3−ε is PSPACE-hard.
Theorem 5.4.The minimum number of pebbles needed in the spooky pebble game on DAGs
with n nodes, a single sink, and maximum in-degree 2 is PSPACE-hard to approximate.
3Although Theorem 1 as stated in [40] does not refer to the number of targets, the full construction presented
in section 2.3.2 of [41] is a DAG with a single target node.
20
