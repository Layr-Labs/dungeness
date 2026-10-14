---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 16
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 16

The text below is a page-delimited extraction of the unchanged source PDF.

Algorithm 2One step of our EEA implementation with register sharing
Require:Work1register stores|t, q, r⟩,Work2register stores|t ′, r′⟩
Require:Lengthregisters store|ℓ t, ℓq, ℓr′ , ℓs⟩
Require:Controlregisters store|Phase1,Phase2,Iter,Sign⟩.
if(Phase1,Phase2) = (0,0)then▷Arithmetic logic for the four phases
Perform a one-position left shift onWork2
ℓs ←ℓ s + 1
Sign←Sign⊕(r <2 ℓs r′)▷Act on qubits (ℓ t +ℓ q + 2) through (n+ 3−ℓ s)
else if(Phase1,Phase2) = (0,1)then
Perform a one-position right shift onWork2
ℓs ←ℓ s −1,ℓ q ←ℓ q + 1
(Sign, r)←(Sign, r)−2ℓs r′ ▷Use registerSignto store the sign of the subtraction result
ifSign= 1then
r←r+ 2 ℓs r′ ▷Ignore overflows
end if
Sign←Sign⊕1
SwapSignwith the (ℓ t +ℓ q + 1)-th qubit ofWork1▷The least significant work qubit ofq
else if(Phase1,Phase2) = (1,0)then
SwapSignwith the (ℓ t +ℓ q + 1)-th qubit ofWork1
ifSign= 0then
t′ ←t ′ −2 ℓs t ▷Act on left-most (ℓ t + 1) qubits
end if
Sign←Sign⊕1
(Sign, t′)←(Sign, t′) + 2ℓs t ▷Use registerSignto store the sign of the addition result
Perform a one-position left shift onWork2
ℓs ←ℓ s + 1,ℓ q ←ℓ q −1
else if(Phase1,Phase2) = (1,1)then
Sign←Sign⊕(t ′ ≥2 ℓs t)▷Same qubit range as above
Perform a one-position right shift onWork2
ℓs ←ℓ s −1
end if
ifℓ q = 0andℓ r′ >0then▷Phase update logic;ℓ r′ = 0 indicates algorithm termination
Phase2←Phase2⊕Sign⊕Phase1,Sign←Sign⊕Phase2
end if
ifℓ s = 0then
Phase1←Phase1⊕1,Phase2←Phase2⊕1
end if
ifℓ q = 0andℓ s = 0then▷Register swapping at the end of one EEA iteration
SwapWork1andWork2
Updateℓ t to the bit length of the newt ▷Act on the left-most (n+ 3−ℓ r′ ) qubits ofWork1andWork2
Updateℓ r′ to the bit length of the newr ′ ▷Act on the right-most (n+ 2−ℓ t) qubits ofWork1andWork2
Iter←Iter⊕1
end if
16
