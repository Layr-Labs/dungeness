---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 20
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 20

The text below is a page-delimited extraction of the unchanged source PDF.

are treated as circuit blocks; we then provide a detailed implementation of these operations in Section
4.4. In all circuit diagrams, the black triangle denotes the output wire that carries the result of the
corresponding circuit block; and we denoteℓ=⌊log 2 n⌋for convenience.
4.1 Overall circuit implementation of one step
According to Algorithm 3, the overall circuit implementation of a single iteration of our space-efficient
EEA is shown in Figures 5 and 6, presented in a continuous layout. Both circuit diagrams are divided
into several algorithmic components, indicated by dashed boxes. Each component corresponds exactly
to one arithmetic block specified in Algorithm 3.
In both circuit diagrams,Shiftdenotes a position shift of the workspace: a positive value represents
a left shift, while a negative value represents a right shift. The circuit blocksAdd,Sub, andSwapdenote
location-controlled addition, subtraction, and swap operations, respectively. At the end of each EEA
iteration, the circuit block labeledSWAPrepresents a full SWAP operation applied to all qubits in the
registersWork1andWork2; this block is distinct from theSwapblock to avoid ambiguity. Finally, the
Lenblock denotes the update operations on the length registers.
|Phase1⟩ /1 • • •
|Phase2⟩ /1 • • • • • • •
|0⟩ /1
|Sign⟩ /1
Sub
▶
▶
• •
Swap
▶
▶|Work1⟩ /n+3
Add
▶
|Work2⟩ /n+3 Shift1 Shift−2
|ℓs⟩ /ℓ+1 +1 −2
|ℓt⟩ /ℓ+1
Swap
|ℓq⟩ /ℓ+1 −1 +1
|ℓr′ ⟩ /ℓ+1
|Iter⟩ /1
Figure 5: Overall circuit implementation (first half) of a single iteration of our space-efficient EEA.
The three dashed boxes, from left to right, represent: (1) pre-shift operations; (2) location-controlled
subtraction onr’s; (3) location-controlled swap.
4.2 Step-dependent active windows
To reduce the quantum gate complexity for implementing our space-efficient EEA, we introduce step-
dependent active windows for each location-controlled operation. As illustrated in the figures of the
previous subsection, we definekandKas known bounds on the active indices of theWorkregisters.
For instance, at stepT, a location-controlled Swap circuit acts on the (ℓ t +ℓ q + 1)-th qubit of the
Work1register. Over all possible inputsxused to compute the modular inversex −1 modp, the quantity
ℓt+ℓq+1 is bounded below byk:=k(T) and above byK:=K(T). Therefore, applying location-controlled
20
