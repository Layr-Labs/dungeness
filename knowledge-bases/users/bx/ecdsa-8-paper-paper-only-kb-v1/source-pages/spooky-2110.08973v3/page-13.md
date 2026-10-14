---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 13
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 13

The text below is a page-delimited extraction of the unchanged source PDF.

pebble placed and each node not inPt must have had a pebble removed before stept in P. We
define P′= [P0,P′
1,..., P′
t′ = Pt,Pt+1,..., Pτ]. Since t′≤t we know thatT(P′) ≤τ. We can
additionally conclude thatS(P′) ≤s since Pt must contain a pebble atvn−1 and soI only uses
s pebbles. Note that whileP and P′may have different ghosting sequences,P′is still a valid
spooky pebbling. This is becauseP must place a pebble (and subsequently remove it without
creating a ghost) at every location whereP′had a ghost during stept′due to Lemma 4.3.
Now we are ready to prove Lemma 4.1.
Proof of Lemma 4.1.By Lemma 4.6 we can assume thatP is sweep-first. Without loss of
generality, let P be the algorithm with T(P) = τ and S(P) = s that maximizes over all
algorithms the least value ofk where vk ∈PFirst(vn,P). Let t= First(vn,P). By our choice ofP
and k, for alli<k , P must place and remove a pebble atvi; thus we can rearrange these steps
from P to match lines 2 through 5 ofP′. Since P is a sweep-first pebbling we know that these
are the only instructions acting onv1,...,v k before step t. We now partition the remaining
instructions ofP into P∗, the set of all instructions acting on nodesvk+1,...,v n, andU∗, the
set of all instructions acting onv1,...,v k — while maintaining their relative order withinP.
We will now show thatP∗ is a valid pebbling of{vk+1,...,v n}that uses at mosts−1
pebbles. Since (i)P is a valid pebbling, (ii)P′as constructed above maintains a pebble atvk
during the execution ofP∗, and (iii) instructions acting on verticesv1,...,v k−1 cannot change
the validity of an instruction onvk+1,...,v n, it follows thatP∗is a valid pebbling. Now assume
for the sake of contradiction thatP∗ placed s pebbles during some step. Then sinceP uses
only spebbles, there must be some first stept′in P where {v1,...,v k}∩Pt′ = ∅before thes’th
pebble is placed on vertices{vk+1,...,v n}. Let ℓ be the least value wherevℓ ∈Pt′. We will
construct another sweep-first pebbling algorithmP⊥ that hasℓ>k as the least value where
vℓ ∈P⊥
First(vn,P⊥) while maintainingT(P⊥) ≤τ and S(P⊥) ≤s, contradicting our choice of
P. Intuitively P⊥ will behave likeP except that it has a pebble atvℓ instead of vk during
step t. P⊥has P⊥
First(vn,P⊥) = (Pt ∪{vℓ}) \{vk}and reaches this state by following the firstt
instructions ofP, except thatP⊥ ghosts vk after a pebble is placed onvk+1 and ignores any
instruction to removevℓ before placing a pebble onvn.
After this,P⊥ continues following the instructions ofP on all vertices excludingvk,...v ℓ
until step t′ of P. At this point we know thatPt′ has empty intersection withvk,...,v ℓ−1
and thereforeP and P⊥have pebbles in the same positions and ghosts on the same positions
excluding vk,...,v ℓ−1. HoweverPt′ has a pebble atvℓ and therefore must place pebbles on all
of vk,...,v ℓ−1. So ifP⊥copies all steps ofP after stept′, it will also remove any ghosts it had
in vk,...v ℓ−1. Thus P⊥is a valid spooky pebbling that uses at mosts pebbles andτ steps and
violates our choice ofP since ℓ>k .
We know thatU∗must be a valid unpebbling by the same reasoning asP∗. All that remains
is to show thatU∗uses at mosts−1 pebbles. As P is a sweep-first algorithm that uses at most
s pebbles, we know that for all stepst′> t, ∥Pt′∩{v1,...,v k}∥≤ s−1. Thus executing the
same instructions inU∗cannot use more thans−1 pebbles andP′is a valid spooky pebbling
that uses no more pebbles or steps thanP.
By Lemma 4.1 we can assume that for any fixed pebble count, there is a minimum step
algorithm that matches the structure ofP′. By recursively applying this argument, we get a
recurrence relation for the minimum number of steps needed to pebble the line of lengthnusing
at mosts pebbles. In general this recurrence has a tree like structure based on the choice ofk
at each level. However, the value ofk that minimizes the expression is the optimal choice.
13
