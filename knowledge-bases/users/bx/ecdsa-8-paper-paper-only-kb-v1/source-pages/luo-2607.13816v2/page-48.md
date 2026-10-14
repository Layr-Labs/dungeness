---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 48
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 48

The text below is a page-delimited extraction of the unchanged source PDF.

Location-controlled addition/subtraction ont’s.As shown above, we have thatℓ t+1≤ ⌊(T−u)/4⌋+
2≤ ⌈T/4⌉+ 1. Under the constraint thatt≤p <2 n, we also obtain thatℓ t + 1≤n+ 1. Therefore,
ℓt + 1≤min{⌈T/4⌉+ 1, n+ 1}.
Length-update circuit.For the lower boundk 4(T), the length-update circuit is activated only at the
end of an EEA iteration, namely whenu= 4(b j + 1). By Lemma A.2, we have
ℓt ≥ T−u−4δ
4c ≥ T−4(n+ 1−ℓ t)−4δ
4c ,
which impliesℓ t ≥ T−4(n+ 1)−4δ
4c−4 .
For the lower boundk 5(T), Lemma A.2 directly yieldsℓ ∗
t ≥ T−4δ
4c . For the upper boundK 5(T),
recall the recurrence relation of the EEA on ther-sequence,r i−1 =r i+1 +q iri <(q i + 1)ri ≤2 bi+1ri. By
iterating this inequality, we obtain
p/rj+1 ≤
jY
i=1
2bi+1 = 2T/4 .
It follows thatn+4−ℓ ∗
r′ < n+4−log2 rj+1 ≤T/4+n+4−log 2 p≤T/4+5, and hencen+4−ℓ ∗
r′ ≤T/4+4.
For the upper boundK 4(T), we similarly haven+ 4−ℓ r′ ≤n+ 4−ℓ ∗
r′ ≤T/4 + 4.
B Improved Modular Multiplication Circuit
Our modular multiplier used in in-place division/multiplication implements
Mulp :|x⟩|y⟩|0⟩ 7−→ |x⟩|y⟩|xymodp⟩,
based on the usual Horner double-and-add scan as the low-space multiplier of [RNSL17]. The circuit
containsncontrolled modular additions andn−1 modular doublings.
•Controlled modular additions.The controlled modular addition
|c⟩|A⟩|B⟩|0⟩f 7−→ |c⟩|A⟩|B+cAmodp⟩|0⟩ f ,
is implemented by first doing the controlled additionB←B+cA(mod 2 n), while XORing the
overflow carry into a flagf. We use a specialized controlled quantum–quantum ripple-carry adder
for this step, rather than controlling every gate of an ordinary adder from [CDKM04]. Letγ i denote
the carry into biti, withγ 0 = 0, andγ i+1 = maj(Ai, Bi, γi).
During the forward sweep, the circuit computes the carry chain. At biti, the addend and accumu-
lator wires are temporarily transformed toA i ⊕γ i andB i ⊕γ i, while the carry wire is advanced
toγ i+1. In the reverse sweep, we first undo the carry Toffoli, so the carry wire again containsγ i.
A CNOT from this carry wire to the accumulator wire restoresB i ⊕γ i 7−→B i. At this point the
addend wire still containsA i ⊕γ i. We then apply the controlled sum-writing Toffoli
CCX

c, Ai ⊕γ i;B i

.
48
