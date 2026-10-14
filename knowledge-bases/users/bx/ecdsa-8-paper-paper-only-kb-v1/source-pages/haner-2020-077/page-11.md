---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 11
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 11

The text below is a page-delimited extraction of the unchanged source PDF.

5.1 Windowed arithmetic
Shor’s algorithm uses 2 n qubits as control qubits, half of which control circuits that add P, 2P,
4P, etc.; the other half control addition of Q, 2Q, etc. The points are added to a single quantum
register which we call the accumulator. This process requires 2 n point additions. We instead use a
windowed approach, analogous to ubiquitous classical pre-computation techniques and similar to
the techniques used for RSA in [ 14]. Other classical pre-computation strategies are less eﬀective, as
Appendix A.5 discusses.
For windowed scalar multiplication, we use the index as an address for a sequential quantum
look-up, which loads a superposition of points O,P, 2P,3P,..., (2ℓ −1)P into an auxiliary register
which we call the cache. For elliptic curves, this requires us to switch from a circuit adding a classical
point to a circuit adding two quantum points, but this has little eﬀect on the cost. The depth and
T-count of the look-up are exponential in the window size ℓ, but we save ℓ point additions.
Signed addition. We can save a factor of 2 in windowing by using one qubit to control the sign
of P = (x,y) and only using ℓ−1 for the look-up. Since −P = (x,−y), the extra qubit only needs
to control a cheap modular negation. This changes the indexing slightly. Our original windowed
circuit took an address register |b⟩and an input register |R⟩, and produced |b⟩|[b]P + R⟩. Using
the top bit bℓ−1 of b= bℓ−12ℓ−1 + b′as a sign and looking up b′P if bℓ−1 = 1 and (2ℓ−1 −b′)P and
negating it if bℓ−1 = 0, we can implement the operation
∑
b∈{0,1}ℓ
|b⟩|R⟩↦→
∑
b∈{0,1}ℓ
|b⟩
⏐⏐[b−2ℓ−1]P + R
⟩
. (2)
Thus, we get an oﬀset in each round, but since the oﬀset is constant, it has no eﬀect on the ﬁnal
phase estimation.
|i0⟩
|i⟩
|x1⟩
|y1⟩
|λ= 0⟩
ℓ−1
n
n
n
Ini
[i]P
neg
neg
−
−
−
−
Ini
[i]P
div
mul
Ini3([i]P)x
+
+
Ini3([i]P)x
−squ
mul
+mul
div
Ini
[i]P
neg
neg
−
−
−
−
Ini
[i]P
neg
Fig. 10: Signed windowed elliptic curve addition, with ℓ address qubits. Ini is the indexing half of
the look-up gate, which writes the classical data shown into the output registers. The width of the
circuits is proportional to the number of auxiliary qubits used.
6 Results
We present quantum resource estimates for Shor’s algorithm based on our cost estimates for
windowed elliptic curve point addition. Results are obtained for optimizing three diﬀerent cost
metrics: either minimizing circuit width (i.e. the total number of logical qubits), the total number
of T gates in the circuit, or total circuit depth. Window sizes above 18 were too large to simulate,
11
