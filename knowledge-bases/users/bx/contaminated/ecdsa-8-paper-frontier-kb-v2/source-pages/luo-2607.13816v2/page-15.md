---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 15
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 15

The text below is a page-delimited extraction of the unchanged source PDF.

t
ℓt
r
t′ r′
ℓr′ Phase 1 t r
t′(h) r′ t′(l)
ℓs
Phase 2
t r−qr′q
ℓq
t′ r′
Phase 3t r−qr′
t′(h) r′ t′(l)Phase 4
t r−qr′
t′+qt r′
Swap t′+qt r′
t r−qr′
Figure 4: An illustration of how the twoWorkregisters are allocated for temporary variables within
a single iteration of the EEA. The upper and lower stripes represent theWork1andWork2registers,
respectively. The symbols (h) and (l) indicate that the valuet ′ is split into its higher-order bits (h)
and lower-order bits (l), which are placed at the corresponding positions on the two sides of theWork2
register.
2−ℓst′ +t= 2 −ℓs(t′ + 2ℓst). Thus, the expressiont ′ + 2ℓstrepresents the desired result, corresponding to
a left shift byℓ s positions.
With this register allocation, one step of our space-efficient EEA proceeds as in Algorithm 2. To
illustrate how the proposed space-efficient EEA operates in practice, we also provide a concrete execution
example forp= 37 andx= 13, shown in Table 4.
For each step, Table 4 shows how the contents of the twoWorkregisters evolve and how different
variables are mapped ontoWork1andWork2under the register-sharing strategy. In particular, the
variablet ′ stored inWork2is divided into two parts that occupy the left-most and right-most portions
of the register. The division symbols are not explicitly implemented in the quantum circuit; they are all
illustrative and inferred from the correspondingLengthregisters, used to visualize the register allocation.
In the actual quantum implementation, all registers are in superposition, and the location of these division
symbols may vary across different input values.
3.3 Algorithmic optimizations
The baseline implementation of one step, as described in the previous subsection, was constructed to
be fully reversible, ensuring that every state transformation can be realized as a unitary operation on a
quantum computer. However, this direct implementation contains multiple redundant operations that
unnecessarily increase both the circuit depth and gate count. In this subsection, we present a series of
algorithmic optimizations applied to the baseline design in order to reduce the quantum circuit depth
15
