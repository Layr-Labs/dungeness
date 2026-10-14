---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 9
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 9

The text below is a page-delimited extraction of the unchanged source PDF.

time-optimal pebbling strategies that employ this structure. The algorithms we discuss in this
section are most naturally expressed in the language of unghosting subroutines (wherevn starts
as a ghost). These subroutines can be converted into pebbling algorithms using the following
lemma:
Lemma 3.2. Let Ug be an unghosting algorithm for the line of lengthn that usess pebbles and
takes τ steps. Then there exists a pebbling algorithm on the line of lengthn+ 1 that uses(s+ 1)
pebbles and takes at most(τ + 1) steps.
Proof. We takeUg and modify it by adding a pebble instruction onvn+1 immediately after the
first instruction acting onvn—which must be a pebble instruction. Note that sincevn starts
with a ghost,Ug must place a pebble atvn during some step. The resulting algorithm is a valid
pebbling that uses at mostτ + 1 steps ands+ 1 pebbles.
We now show a simple spooky pebbling algorithm that uses a constant number of pebbles
to pebble the line.
Proposition 3.3(from [11]). There exists a spooky unghosting algorithm that can unghost the
line graph of lengthn using O(n2) steps and only two pebbles.
Proof. Consider the following algorithm:
Un2
g ({v1,...,v n}):
place (v1)
if( n= 1):
remove (v1)
else :
for i∈[2,n −1]:
place (vi)
remove (vi−1)
place (vn)
remove (vn)
remove (vn−1)
run Un2
g ({v1,...v n−1})
This algorithm removes the ghost onvn, leaving a ghost onvn−1. This process is repeated until
the remaining ghost is onv1, at which point we can remove the pebble without creating a ghost.
The number of steps in this pebbling algorithm is given byT(1) = 2 and T(k) = 2k+2+ T(k−1).
Unrolling this recursion yieldsT(n) = n2 + 3n−2 which isO(n2).
We can convertU into a pebbling algorithm for the line of lengthn with 3 pebbles using
Lemma 3.2.
Corollary 3.4(from [11]). There exists a spooky pebbling algorithm that can pebble the line
graph of lengthn using O(n2) steps and only three pebbles.
With the use of additional pebbles, we can create asymptotic improvements in the number
of steps used by pebbling algorithms. One additional pebble produces a pebbling that requires
only O(n3/2) steps. This extra pebble lets us leave a “checkpoint” in our computation that makes
removing ghosts possible with fewer steps. However this checkpoint must then be removed in an
unpebbling subroutine. This idea can be extended to create a general tradeoff between pebbles
and steps.
9
