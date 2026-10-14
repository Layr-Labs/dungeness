---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 32
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 32

The text below is a page-delimited extraction of the unchanged source PDF.

6.1 Space complexity improvements
In this work, we focus exclusively on reducing the space complexity required for modular inversion,
rather than exploring trade-offs among Toffoli count, circuit depth, and space complexity as previous
works [RNSL17, HJN +20, BZG +26, Sch26]. Specifically, we present an exact, space-efficient, in-place
reversible quantum circuit for modular inversion that implements Equation (1). The circuit is based on
the register-sharing technique originally proposed by Proos and Zalka [PZ03]. This approach reduces the
nunmber of qubits required for modular inversion to
2n+ 6⌊log 2 n⌋+ 19.
Of this total, 2n+ 4⌊log 2 n⌋+ 15 qubits correspond to the base circuit shown in Figures 5 and 6, while
the remaining 2⌊log 2 n⌋+ 4 qubits are required for the unary iteration described in Section 4.3.
For elliptic curve point addition shown in Figure 14, the overall space complexity is then
3n+ 6⌊log 2 n⌋+ 19.
6.2 Asymptotic gate counts
Modular inversion.We first derive the asymptotic Toffoli and CNOT gate counts of the proposed
modular inversion circuit. Since the circuit consists of several types of location-controlled operations, we
first recall (in Section 4.4) the gate cost incurred by each circuit block at algorithmic stepT. These per-
step costs are summarized in Table 5. We then combine them with the active-window analysis developed
in Section 4.2 to obtain the overall asymptotic gate complexity.
Circuit block on stepT Toffoli cost CNOT cost
Location-controlled
addition/subtraction onr’s 11(K1(T)−k 1(T)) 12(K1(T)−k 1(T))
Location-controlled swap 2(K2(T)−k 2(T)) 4(K2(T)−k 2(T))
Location-controlled
addition/subtraction ont’s 9(K3(T)−k 3(T)) 10(K3(T)−k 3(T))
Length-update circuit for
ℓt (only on 4|T) 24(K4(T)−k 4(T)) 32(K4(T)−k 4(T))
Length-update circuit for
ℓr′ (only on 4|T) 24(K5(T)−k 5(T)) 32(K5(T)−k 5(T))
Table 5: Per-step Toffoli and CNOT gate counts of the major circuit blocks in the modular inversion
algorithm.
•Location-controlled addition/subtraction onr’s.These operations cost
2
4⌈cn⌉X
T=1
11

K1(T)−k 1(T)

+O(nlog 2 n) = (44c+ 11)n 2 +O(nlog 2 n)
Toffoli gates, and (48c+ 12)n 2 +O(nlog 2 n) CNOT gates.
32
