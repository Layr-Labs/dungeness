---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 33
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 33

The text below is a page-delimited extraction of the unchanged source PDF.

•Location-controlled swap.These operations cost
4⌈cn⌉X
T=1
2

K2(T)−k 2(T)

+O(nlog 2 n) = (4c+ 1)n 2 +O(nlog 2 n)
Toffoli gates, and (8c+ 2)n 2 +O(nlog 2 n) CNOT gates.
•Location-controlled addition/subtraction ont’s.These operations cost
2
4⌈cn⌉X
T=1
9

K3(T)−k 3(T)

+O(nlog 2 n) = (72c−36)n 2 +O(nlog 2 n)
Toffoli gates, and (80c−40)n 2 +O(nlog 2 n) CNOT gates.
•Length-update circuit for updatingℓ t.We execute the length-update circuit only at step
indicesTthat are multiples of four. These operations cost
⌈cn⌉X
T′=1
24

K4(4T′)−k 4(4T′)

+O(nlog 2 n) = 12cn2 +O(nlog 2 n).
Toffoli gates, and 16cn2 +O(nlog 2 n) CNOT gates.
•Length-update circuit for updatingℓ r′.We execute the length-update circuit only at step
indicesTthat are multiples of four. These operations cost
⌈cn⌉X
T′=1
24

K4(4T′)−k 4(4T′)

+O(nlog 2 n) = (12c−12)n 2 +O(nlog 2 n).
Toffoli gates, and (16c−16)n 2 +O(nlog 2 n) CNOT gates.
In addition to the circuit blocks analyzed above, the modular inversion circuit (illustrated in Figures
5 and 6) contains four controlled Shift circuits. Each Shift circuit consists ofn+O(1) Toffoli gates and
2n+O(1) CNOT gates. Therefore, these four Shift circuits contribute an additional 16cn 2 +O(n) Toffoli
gates and 32cn2 +O(n) CNOT gates.
Combining all contributions, the total number of Toffoli gates required by our (one-sided without
reversion) modular inversion circuit grows asymptotically as
(160c−36)n 2 +O(nlog 2 n)<216.636n 2 +O(nlog 2 n).
The asymptotic bound of CNOT gates required is
(200c−42)n 2 +O(nlog 2 n)<273.795n 2 +O(nlog 2 n).
33
