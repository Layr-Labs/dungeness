---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 19
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 19

The text below is a page-delimited extraction of the unchanged source PDF.

Algorithm 3Optimized one step of our EEA implementation
Require:Work1register stores|t, q, r⟩,Work2register stores|t ′, r′⟩;
Require:Lengthregisters store|ℓ t, ℓq, ℓr′ , ℓs⟩;
Require:Controlregisters store|Phase1,Phase2,Iter,Sign⟩.
ifPhase1= 0then▷Pre-shift operations
Perform a one-position left shift onWork2, and updateℓ s ←ℓ s + 1
ifPhase2= 1then
Perform a two-position right shift onWork2, and updateℓ s ←ℓ s −2
end if
(Sign, r)←(Sign, r)−2ℓs r′ ▷Arithmetic block 1: location-controlled subtraction onr’s
ifPhase2= 1then
Sign←Sign⊕1
end if
ifPhase2= 0orSign= 0then
r←r+ 2 ℓs r′
end if
end if
ifPhase1⊕Phase2= 1then▷Arithmetic block 2: location-controlled swap
SwapSignwith the (ℓ t +ℓ q + 1)-th qubit ofWork1
ifPhase1= 1then
ℓq ←ℓ q −1
else
ℓq ←ℓ q + 1
end if
end if
ifPhase1= 1then▷Arithmetic block 3: location-controlled addition ont’s
ifPhase2= 1orSign= 0then
t′ ←t ′ −2 ℓs t
end if
Sign←Sign⊕1
(Sign, t′)←(Sign, t′) + 2ℓs t
Perform a one-position left shift onWork2, and updateℓ s ←ℓ s + 1▷Post-shift operations
ifPhase2= 1then
Perform a two-position right shift onWork2, and updateℓ s ←ℓ s −2
end if
end if
ifℓ q = 0andℓ r′ >0then▷Phase update logic;ℓ r′ = 0 indicates algorithm termination
Phase2←Phase2⊕Sign⊕Phase1,Sign←Sign⊕Phase2
end if
ifℓ s = 0then
Phase1←Phase1⊕1,Phase2←Phase2⊕1
end if
ifℓ q = 0andℓ s = 0then▷Register swapping at the end of one EEA iteration
SwapWork1andWork2
Updateℓ t to the bit length of the newt,ℓ r′ to the bit length of the newr ′
Iter←Iter⊕1
end if
19
