---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 12
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 12

The text below is a page-delimited extraction of the unchanged source PDF.

1 P′({v1,...,v n}):
2 place (v1)
3 for i∈[2,k]:
4 place (vi)
5 remove (vi−1)
6 run P∗({vk+1,...v n})
7 run U∗({v1,...,v k})
Inotherwords, P′isthesamealgorithmasinLemma3.5, butwiththechoiceof kdetermined
by the values ofnand sin some arbitrary way. We prove Lemma 4.1 over the course of Section 4.
Given a spooky pebbling algorithm and a nodevi, we define a notation for the first and last
time that this node contains a pebble:
Definition 4.2.Let First(vi,P) = min({t|vi ∈Pt}) and Last(vi,P) = max({t|vi ∈Pt}).
Lemma 4.3.∀i∈[2,n −1], Last(vi,P) <Last(vi−1,P).
Proof. Let t= Last(vi,P), which implies that there is never a pebble placed onvi after Pt. By
the definition of a spooky pebbling we require thatGτ = ∅, sovi ̸∈Gt+1 as we never place a
pebble onvi after stept. Since this is a valid pebbling, we can conclude thatvi−1 ∈Pt and thus
Last(vi,P) <Last(vi−1,P).
Definition 4.4.Let First(vn,P) = t. We callP sweep-first if a pebble is placed atvn only once
and eachvi has at most one pebble placed on it before stept.
Lemma 4.5. Let G = (V,E) be a line andS ⊆V be such that|S|= s. Then there exists a
valid sequence of pebbling instructions that places pebbles on exactlyS that is time-optimal and
uses at mosts+ 1 pebbles.
Proof. Consider the following pebbling sequence:
1 I({v1,...,v n},S):
2 k= argmaxivi ∈S
3 place (v1)
4 for i∈[2,k]:
5 place (vi)
6 if( vi−1 ̸∈S):
7 remove (vi−1)
The above sequence uses at mosts+ 1 pebbles and takes exactly2k−s steps. Since placing
a pebble onvk requires placing pebbles on each node before it and we want to only end with
pebbles onS, any pebbling sequence that completes this task must place at leastk pebbles and
remove k−s pebbles. Therefore the above pebbling sequence uses the time-optimal number of
steps.
Note thatI only usess pebbles when vk−1 ∈S. Using the above lemma, we can turn any
pebbling into one that is sweep first.
Lemma 4.6. Let P be any spooky pebbling algorithm whereT(P) = τ and S(P) = s. Then
there exists a sweep-first pebbling algorithmP′ where T(P′) ≤τ and S(P′) ≤s.
Proof. Let t be the last step whereP places a pebble onvn. We know thatt< Last(vn−1,P).
Thus by Lemma 4.3 we know thatt< Last(vi,P) for alli<n . P′will place pebbles on exactly
Pt in t′= 2n−∥Pt∥steps by runningI({v1,...v n},Pt). We know thatt′≤tsince eachvi has a
12
