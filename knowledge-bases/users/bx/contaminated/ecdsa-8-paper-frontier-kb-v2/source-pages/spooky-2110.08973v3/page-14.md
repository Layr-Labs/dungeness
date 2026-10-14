---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 14
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 14

The text below is a page-delimited extraction of the unchanged source PDF.

Corollary 4.7. Let TP(n,s) (TUP(n,s)) be the minimum number of steps needed to pebble
(unpebble) a line of lengthn using at mosts pebbles. Then:
TP(n,s) =



1 s≥1 and n= 1
∞ s< 3 and s<n
mink∈[1,n) 2k−1 + TUP(k,s −1) + TP(n−k,s −1) o.w.
The ∞comes from observing that there is no way to spooky pebble a line longer thans
with s pebbles whens< 3. Unfortunately the above recurrence features a call toTUP and the
non-obvious choice ofk makes it hard to analyze. Now we establish how the time complexities
of pebbling, unpebbling, and unghosting relate so that we can convert Corollary 4.7 into a form
that is easier to work with.
Relationships between Pebbling, Unpebbling, and Unghosting
In Section 3, our constructions were more naturally expressed using unghosting rather than
pebbling. In order to prove the tightness of our upper bounds, it is convenient to also express
our lower bounds in terms of unghosting. For such a bound to be useful, we require a tight
relationship between pebbling and unghosting. We have already proven a way to convert an
unghosting to a pebbling.
Lemma 3.2. Let Ug be an unghosting algorithm for the line of lengthn that usess pebbles and
takes τ steps. Then there exists a pebbling algorithm on the line of lengthn+ 1 that uses(s+ 1)
pebbles and takes at most(τ + 1) steps.
Now we will show how to convert a pebbling into an unghosting.
Lemma 4.8.Let P be a pebbling algorithm for the line of lengthn+ 1 that usess+ 1 pebbles
and takesτ + 1 steps. Then there exists an unghosting algorithm on the line of lengthn that
uses s pebbles and takes at mostτ steps.
Proof. Let t be the the last step ofP operating onvn+1. This must be a pebbling step, so both
vn and vn+1 are inPt. Divide P into two components around this point,Ppre for the firsttsteps
and Ppost for the remaining steps. SincePpre must have spent at least one step on pebbling
each ofvn and vn+1, there must be some algorithmP∗
pre running in at mostt−2 steps that
ends inPt \{vn,vn+1}. Moreover, by Lemma 4.5,P∗
pre may be constructed to require at most
|Pt \{vn,vn+1}|+ 1 ≤s pebbles.
Let P∗
post be a sequence of pebbling instructions derived fromPpost by removing any in-
structions operating onvn before Last(vn,Ppost), then inserting an instruction placing a pebble
on vn immediately before that last removal ofvn. This is valid, as the new placement occurs
immediately before a removal (so the predecessor ofvn is pebbled), and no operations occur on
vn+1 that would be affected by changing whether a pebble is present onvn.
P∗
pre followed byP∗
post is then a valid unghosting of the line graph up tovn, excludingvn+1.
Since P∗
pre is at least 2 steps shorter thanPpre and P∗
post is at most 1 step longer thanPpost, the
composition takes at mostτ steps. Moreover, the composition requires at mosts pebbles, P∗
pre
by Lemma 4.5 andP∗
post because it operates as inPpost but without an extra pebble sitting on
vn+1.
Combining the results of Lemma 4.8 and Lemma 3.2 we show a tight relationship between
unghosting and pebbling. We also characterize the relationship between unghosting and unpeb-
bling.
14
