---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 11
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 11

The text below is a page-delimited extraction of the unchanged source PDF.

Our Theorem 4.13 will show that the above algorithm for spooky pebbling the line is asymp-
totically optimal for all pebble bounds.
Corollary 3.7.For any constantε∈(0,1] there exists a spooky pebbling algorithm on any line
of lengthn≥⌈2/ε⌉⌈2/ε⌉ that uses⌈nε⌉pebbles andO(n/ε) steps.
Proof. Let m be the smallest integer such thatn≤
(m+⌈nε⌉−2
⌈nε⌉−2
)
+ 1. Applying the algorithm in
Theorem 3.6 to the line of lengthn lets us pebble it withO(mn) steps and⌈nε⌉pebbles. We
now want to show that whenm′= ⌈2/ε⌉and n≥⌈2/ε⌉⌈2/ε⌉, n≤
(m′+⌈nε⌉−2
⌈nε⌉−2
)
. Observe that:
(
m′+ ⌈nε⌉−2
⌈nε⌉−2
)
≥
(m′+ nε −2
m′
)m′
≥n2/⌈(2/ε)⌉⌈2/ε⌉≥n
By our choice ofm we can conclude thatm ≤m′ and therefore the number of steps for the
pebbling algorithm isO(n/ε).
Corollary 3.8.For anyε∈(0,1], there exists a spooky pebbling algorithm on the line of length
n that usesO(1/ε) pebbles andO(n1+ε/ε) steps.
Proof. Let m= ⌈(2nε −1)/ε⌉and s= ⌈1/ε⌉+ 2.
(
m+ s−2
s−2
)
+ 1 ≥
(m+ s−2
s−2
)s−2
=
(⌈(2nε −1)/ε⌉+ ⌈1/ε⌉
⌈1/ε⌉
)⌈1/ε⌉
≥
(2nε/ε
2/ε
)⌈1/ε⌉
≥n
Therefore, by Theorem 3.6, there exists a pebbling algorithm on the line usings = O(1/ε)
pebbles andO(mn) or O(n1+ε/ε) steps.
Corollary 3.9. There exists a spooky pebbling algorithm on the lines of lengthn that uses
O(log n) pebbles andO(nlog n) steps.
Proof. By Corollary 3.8 withε= 1/log n.
These results are summarized in Figure 1.
4 Lower bounds on spooky pebbling the line
We use a divide and conquer approach to describe the general structure of time-optimal spooky
pebbling algorithms for a given pebble bound. We then analyze the runtime of such an algorithm
to obtain an asymptotically tight lower bound on spooky pebbling the line.
Optimal structured spooky pebbling
Let P = [ P0,..., Pτ] be an arbitrary spooky pebbling of the line with nodesv1,...v n. We
will show thatP uses at least as many steps as a spooky pebbling algorithm matchingP′ in
Lemma 4.1.
Lemma 4.1. Let P be an arbitrary spooky pebbling of the line usingT(P) = τ steps and
S(P) = s pebbles. Then there existsk, pebbling algorithmP∗, and unpebbling algorithmU∗ such
that the pebbling algorithmP′ described below hasT(P′) ≤τ and S(P′) ≤s.
11
