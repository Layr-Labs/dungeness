---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 6
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 6

The text below is a page-delimited extraction of the unchanged source PDF.

6
|0⟩ℓb|0⟩b|0⟩nb
Stage 1
− − − − − − − − − − − − − − − − − − − − →
Sparse Dicke State Preparation
ℓX
k=0
ˆwk


X
1≤j1<j2<···<jk≤m
jk+1...jℓ=0
|j1⟩b |j2⟩b ···| jℓ⟩b

|0⟩b|0⟩nb

where ˆwk = wk
m
k
−1/2!



2a: Check ifi ∈ [j1, . . . jℓ] and store the result in qubityi
− − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − →
ℓX
k=0
ˆwk |SDm
k ⟩lb |yi⟩
X
ei∈Fq
˜gi(ei) |ei⟩b |s⟩nb
2b: Apply Gi on qubityi to generate error termei
− − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − − →
ℓX
k=0
ˆwk |SDm
k ⟩lb
X
ei∈Fq
˜gi(ei) |ei⟩b |s⟩nb
2c: Update syndrome register|s⟩ with BT
i ·ei
− − − − − − − − − − − − − − − − − − − − − − − − − − − − →
ℓX
k=0
ˆwk |SDm
k ⟩lb
X
ei∈Fq
˜gi(ei) |ei⟩b |s + BT
i · ei⟩nb
2d: MBU on error register|ei⟩ (record ci)
− − − − − − − − − − − − − − − − − − − − − − − − − − →
ℓX
k=0
ˆwk |SDm
k ⟩lb
X
ei∈Fq
˜gi(ei)(−1)ei·ci|s + BT
i · ei⟩nb



Repeat i = 1 . . . m
Stage 2
− − − − − − − − − − − − − − − →
Syndrome Computation
ℓX
k=0
ˆwk
X
|e|=k
 mY
i=1
˜gi(ei)
!
(−1)c·e|BT e⟩nb
Stage 3
− − − − − − − − − − − − − →
Reversible Decoding
ℓX
k=0
ˆwk
X
|e|=k
 mY
i=1
˜gi(ei)
!
|BT e⟩nb ≡ |]P(f)⟩nb
Stage 4
− − − − − − − − − − − − − − →
IQFT + Measurement
X
x
P(f(x))|x⟩nb ≡ |P(f)⟩nb
• Stage 1: Sparse Dicke State Preparation:We prepare a superpositionPl
k=0 wk|k⟩, using classically pre-
computed coefficientswk which define the optimal enhancing polynomialP [27–29]. This is used to prepare the
ℓ · b-qubit error locator register into the corresponding superposition of Sparse Dicke states:
lX
k=0
wk
m
k
−1/2


X
1≤j1<j2<···<jk≤m
jk+1...jℓ=0
|j1⟩b |j2⟩b ···| jℓ⟩b

 (3)
In Appendix B, we describe a way to prepare Sparse Dicke States using2 · k · log2 m qubits andO(m.k + k2b2)
gates. The sparse construction is useful in reducing the qubit counts for instances wheren ≪ m.
• Stage 2: Sequential Syndrome Computation and MBU:This stage translates the error locator register
into a superposition of syndromes, using our space-efficient sequential approach.
Defining the Constraint Encoding GatesGi: The operations in this stage depend on the specific constraints of
the optimization problem. Recall the objective functionf(x) = Pm
i=1 fi(bi · x) with fi : Fq → {+1, −1}. As
detailed in [4, Section 8.2.1], we find it convenient to work in terms ofgi, which we define asfi shifted and
rescaled such that:
gi(x) := fi(x) − ¯f
c , (4)
where ¯f is the average value offi over Fq and c is a normalization constant. This standardization ensures that
the Fourier transform ofgi, denoted˜gi(e), vanishes ate = 0 and is normalized (P
e |˜gi(e)|2 = 1). We then define
an isometryGi, which acts on a singe qubityi storing whether an error occurs at indexi or not, and maps it
to a superposition overb-qubit error terms that encode these Fourier coefficients:
Gi|0⟩ = |0⟩b, G i|1⟩ =
X
e∈Fq,e̸=0
˜gi(e)|e⟩b. (5)
