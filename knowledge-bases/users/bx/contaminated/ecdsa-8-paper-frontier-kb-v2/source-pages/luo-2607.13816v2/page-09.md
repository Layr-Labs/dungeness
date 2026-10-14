---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 9
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 9

The text below is a page-delimited extraction of the unchanged source PDF.

2.2 Elliptic curves and the ECDLP
Letpbe a large prime and letF p denote the finite field withpelements. An elliptic curveE/F p (in short
Weierstrass form) is the set of affine solutions (x, y)∈F 2
p to an equationy 2 =x 3 +ax+b, together with
a distinguished pointOat infinity. The set ofF p-rational points, together withO, is denoted byE(F p).
The points onE(F p) form an abelian group under the elliptic-curve addition law, with identity
elementO. For affine pointsP 1 = (x1, y1) andP 2 = (x2, y2) that are not inverse to each other, the sum
P3 =P 1 +P 2 can be computed via a slope parameterλ:
x3 =λ 2 −x 1 −x 2, y 3 =λ(x 1 −x 3)−y 1,
whereλequals the chord slope y2−y1
x2−x1
whenP 1 ̸=P 2, and the tangent slope 3x2
1+a
2y1
whenP 1 =P 2.
Exceptional cases (e.g.,P i =OorP 2 =−P 1) are handled according to the standard group properties.
For an integerm≥1, the notation [m]Pdenotes them-fold sum of a pointPwith itself, i.e.
[m]P=P+P+···+P, wherePoccursmtimes. Thism-fold sum can be extended to allm∈Z
by defining [0]P=Oand [−m]P= [m]\(−P) form≥1. The operationm7→[m]Pis calledscalar
multiplicationand is the core primitive used in elliptic-curve cryptography.
LetP∈E(F p) generates a cyclic subgroup⟨P⟩of orderr, and letQ∈ ⟨P⟩. Theelliptic-curve discrete
logarithm problem (ECDLP)is to recover the uniquem∈ {0,1, . . . , r−1}such that
Q= [m]P.
In classical settings, the best generic algorithms require on the order of Θ( √p) group operations [GG16],
which is exponential in the bit length log 2 p.
2.3 Shor’s quantum algorithm for ECDLP
Shor’s discrete-logarithm algorithm for solving ECDLP applies to elliptic curve over any finite abelian
group and therefore toE(F p). Letn=⌊log 2 p⌋+ 1 be the bit-length ofp. The quantum procedure uses
two exponent registers and one register storing an elliptic curve point.
Firstly, initialize two (n+ 1)-qubit registers 1 to be|0 n+1,0 n+1⟩, and apply Hadamard gate to all
the qubits to obtain a uniform superposition over pairs (k, ℓ)∈ {0,1, . . . ,2n+1 −1} 2. Next, coherently
compute the elliptic curve group action into an accumulator as
2n+1−1X
k,ℓ=0
|k, ℓ⟩|O⟩ 7−→
2n+1−1X
k,ℓ=0
|k, ℓ⟩|[k]P+ [ℓ]Q⟩.(2)
After this step, apply Quantum Fourier TransformQFT 2n+1 to both exponent registers and then measure
them. Finally, a classical post-processing procedure uses the measurement outcomes to reconstruct the
discrete logarithmmwith high probability, as shown in [Sho94].
In terms of resource, the dominant cost arises from the coherent group evaluation, i.e., the double-
scalar multiplication on elliptic curve points. To reduce the qubit cost associated with QFT, its full circuit
1Hasse’s bound [Has36] indicates that ord(P)≤#E(F p)≤p+ 1 + 2 √p, which can be represented by at mostn+ 1 bits.
9
