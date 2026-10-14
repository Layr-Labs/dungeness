---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 10
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 10

The text below is a page-delimited extraction of the unchanged source PDF.

Lemma 3.5. For anys,m ∈N such thatn≤
(m+s−1
s−1
)
, there exists an unghosting algorithm for
the line of lengthn that uses at mosts pebbles andO(mn) steps.
Proof. We consider the following unghosting algorithm that usesspebbles for when the line has
length exactlyn=
(m+s−1
s−1
)
for some value ofm:
Ug({v1,...,v n},s): // Assume that n=
(m+s−1
s−1
)
for some value of m.
if (n≤s):
for i∈[1,n]:
place (vi)
for i∈[0,n −1]:
remove (vn−i)
else :
let k=
(m+s−2
s−1
)
place (v1)
for i∈[2,k]:
place (vi)
remove (vi−1)
run Ug({vk+1,...v n},s −1) // Line of length n−k=
(m+s−2
s−2
)
.
remove (vk)
run Ug({v1,...,v k},s) // Line of length k=
(m+s−2
s−1
)
.
Note that ifm′= m−1 then k=
(m′+s−1
s−1
)
, so our assumption onn holds in the recursive cases.
While the recursive calls toUg may run on lines that contain ghosts on nodes other than the
target, removing the ghost at the target will require placing pebbles on all other nodes. This
will remove any additional ghosts present at the start of the recursive call. To upper bound
the number of steps required to runUg on a line of lengthn=
(m+s−1
s−1
)
with s pebbles, we will
upper bound the number of steps that act on any node and multiply that by the total number
of nodes. LetTi(m,s) be the number of timesUg acts on nodevi and T∗(m,s) = maxiTi(m,s).
Then directly from the construction ofUg we have:
T∗(m,s) ≤
{
2 s≥
(m+s−1
s−1
)
max (2 +T∗(m−1,s),T∗(m,s −1)) s<
(m+s−1
s−1
)
.
In other words, whens≥n, each node has a pebble placed and removed at most once. Otherwise,
when s < n, the node visited the most times either is beforevk+1 and gets a pebble placed
and removed and is part of the callUg({v1,...,v k},s) or is after k and is part of the call
Ug({vk+1,...v n},s −1).
When mor sis 1, we observe thats≥
(m+s−1
s−1
)
, and so the base caseT∗(1,s) = T∗(m,1) = 2.
Since every recursive step at most increasesT∗by 2 every time thatm increases by1, it follows
that T∗(m,s) ≤2m. This lets us conclude that when the line has lengthn=
(m+s−1
s−1
)
, we can
unghost it usingO(mn) steps.
When n<
(m+s−1
s−1
)
we observe that the above unghosting algorithm can be truncated to the
shorter line of lengthn by ignoring steps on nodes aftervn. Again the largest number of steps
on any node is at most2m so we can conclude that the unpebbling algorithm takes at most
2mn steps.
We can convert this to a pebbling algorithm with Lemma 3.2.
Theorem 3.6.For anys,m ∈N such thatn≤
(m+s−2
s−2
)
+ 1, there exists a pebbling algorithm
for the line of lengthn that uses at mosts pebbles andO(mn) steps.
10
