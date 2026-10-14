---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 15
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 15

The text below is a page-delimited extraction of the unchanged source PDF.

Lemma 4.9. Let Ug be an unghosting algorithm for the line of lengthn that usess pebbles and
takes τ steps. Then there exists an unpebbling algorithm for the line of lengthn that uses s
pebbles and takesτ + 1 steps.
Proof. Define Up by first ghostingvn, then runningUg.
Lemma 4.10. Let Up be an unpebbling algorithm for the line of lengthn that usess pebbles
and takesτ steps. Then there exists an unghosting algorithm for the line of lengthn that usess
pebbles and takesτ + 1 steps.
Proof. Define Ug by runningUp, but beforeLast(vn,Up), skip all preexisting operations onvn,
and immediately beforeLast(vn,Up), add a new step to place a pebble onvn. Ug only differs
from Up by sometimes not having a pebble onvn when Up does, so it uses at most as many
pebbles, and it inserts only a single new step.
Theorem 4.11.TP(n+ 1,s + 1) = TUG(n,s) + 1. TUG(n,s) = TUP(n,s) ±1.
Lower bounds on the number of steps for pebbling
Now that we have established the relationship between pebbling, unpebbling, and unghosting,
we can lower bound the number of steps needed to perform these tasks. While pebbling is the
most natural quantity to evaluate, it turns out that unghosting has a much cleaner analysis than
pebbling.
We can now restate Corollary 4.7 in the language of unghosting.
Corollary 4.12.Let TUG(n,s) (TUP(n,s)) be the minimum number of steps needed to unghost
(unpebble) a line of lengthn using at mosts pebbles. Then:
TUG(n,s) =



2 s≥1 and n= 1
∞ s< 2 and s<n
mink∈[1,n] 2k−1 + TUP(k,s) + TUG(n−k,s −1) o.w.
Note that we cannot apply Theorem 4.11 to the base case in Corollary 4.7. Instead the
base case in the above recurrence can be verified by inspection. We can then use Theorem 4.11
to convert our lower bound on unghosting to pebbling. By Theorem 4.11 we know that
TUP(k,s) ≥TUG(k,s) −1. We therefore define the following recurrence relation that is a lower
bound onTUG(n,s):
T(n,s) =



2 s≥1 and n= 1
∞ s< 2 and s<n
mink∈[1,n] 2k−2 + T(k,s) + T(n−k,s −1) o.w.
(1)
While T(n,s) is not exactly the minimum number of steps needed to unghost the line of length
n with s pebbles, it is a sufficiently tight lower bound. A function similar toT(n,s) appears
in [31, 32] as the solution to the backtracking problem in dynamic programming. They provide
efficient algorithms that can be used to compute the optimal value ofk in each recursive call.
Another similar recurrence appears in the problem of sequence reversing, where there is a proven
lower bound similar to the one we present here [33, 34]. In the rest of this section we use this
recurrence relation to prove that unghosting with at mostspebbles requiresΩ(mn) steps which
is sufficient to obtain the following theorem.
15
