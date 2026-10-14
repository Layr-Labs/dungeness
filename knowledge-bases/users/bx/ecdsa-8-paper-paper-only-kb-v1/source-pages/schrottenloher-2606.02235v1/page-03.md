---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 3
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 3

The text below is a page-delimited extraction of the unchanged source PDF.

recent work [4] achieved a space of 3.12n+O( √n), but the technique employed
is very different and yields a sharp increase in gate count for a relatively small
gain in memory on relevant instances.
A comparison between the qubit and gate counts of Babbush et al. [2] and
ours is given in Table 1.
Table 1.Costs of our circuits and comparison with [2]. The “Toffolis” column counts
together CCX, CCZ as well as And gates. All circuits have a failure probability at most
2−13.3 (succeeding on 10 000 randomly chosen inputs). The number of qubits and gates
given here do not account for the small window of sizew= 16: it costs 16 qubits more
and 3×2 w Toffoli gates to run the actual “windowed point addition” circuit.
Type Qubits Toffolis Total gates Reference
Space-optimized forsecp256k11175 2 21.36 ≃2 24 [2]
Gate-optimized forsecp256k11425 2 21.00 ≃2 24 [2]
Space-optimized forsecp256k11192 2 21.19 ≃2 24 Ours
Gate-optimized forsecp256k11446 2 20.83 ≃2 24 Ours
Space-optimized for any prime 1192 2 21.78 ≃2 24.5 Ours
Gate-optimized for any prime 1446 2 21.42 ≃2 24.5 Ours
Following the same reasoning as [2], the Toffoli count of the entire Shor’s
algorithm onsecp256k1is roughly:
28×(3×2 16 +Q A) (1)
whereQ A is the Toffoli count of a single windowed addition circuit as given
in Table 1, while the qubit count is the one of Table 1 plus 16 (roughly). The
algorithm needs to run only once to retrieve the discrete logarithm (contrary to
trade-offs for RSA like in [9], which require multiple runs). The resulting numbers
are summarized in Table 2. The best previous result was from Litinski [15]
using around 200 million Toffoli gates (i.e., 2 27.57) to compute a single discrete
logarithm, with about twice as much qubits.
Ideas of the Circuit and Organization of the Paper
We detail our circuits in a top-down approach, starting from the high-level imple-
mentation of Shor’s algorithm (which is the same as in [2] and previous works),
down to the implementation of arithmetic circuits.
From Shor’s Algorithm to Point Addition (Section 2).The fact that Babbush
et al. [2] used a standard implementation of Shor’s algorithm, and not a “com-
pressed” version like [4], is explicit in their work. In this implementation, the
main costly component in the algorithm is point multiplication:
|u, v⟩|0⟩ 7→ |u, v⟩|[u]P+ [v]Q⟩,
3
