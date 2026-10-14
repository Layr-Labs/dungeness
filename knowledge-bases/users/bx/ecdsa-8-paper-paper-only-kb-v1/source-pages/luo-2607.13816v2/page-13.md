---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 13
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 13

The text below is a page-delimited extraction of the unchanged source PDF.

Inputx 1 x2 x3
Step 1Iteration 1, Phase 1 Iteration 1, Phase 1 Iteration 1, Phase 1
Step 2Iteration 1, Phase 1 Iteration 1, Phase 1 Iteration 1, Phase 1
Step 3Iteration 1, Phase 2 Iteration 1, Phase 1 Iteration 1, Phase 1
Step 4Iteration 1, Phase 2 Iteration 1, Phase 1 Iteration 1, Phase 2
Step 5Iteration 1, Phase 3 Iteration 1, Phase 1 Iteration 1, Phase 2
Step 6Iteration 1, Phase 3 Iteration 1, Phase 2 Iteration 1, Phase 2
Step 7Iteration 1, Phase 4 Iteration 1, Phase 2 Iteration 1, Phase 3
Step 8Iteration 1, Phase 4 (and SWAP) Iteration 1, Phase 2 Iteration 1, Phase 3
Step 9Iteration 2, Phase 1 Iteration 1, Phase 2 Iteration 1, Phase 3
Step 10Iteration 2, Phase 1 Iteration 1, Phase 2 Iteration 1, Phase 4
Step 11Iteration 2, Phase 1 Iteration 1, Phase 3 Iteration 1, Phase 4
Step 12Iteration 2, Phase 2 Iteration 1, Phase 3 Iteration 1, Phase 4 (and SWAP)
Step 13Iteration 2, Phase 2 Iteration 1, Phase 3 Iteration 2, Phase 1
Step 14Iteration 2, Phase 2 Iteration 1, Phase 3 Iteration 2, Phase 1
Step 15Iteration 2, Phase 3 Iteration 1, Phase 3 Iteration 2, Phase 2
Step 16Iteration 2, Phase 3 Iteration 1, Phase 4 Iteration 2, Phase 2
··· ··· ··· ···
Step 100Iteration 9, Phase 3 Iteration 5, Phase 2 Iteration 8, Phase 4
··· ··· ··· ···
Table 3: An example illustrating that the EEA iteration index and phase number may vary depending
on the input valuex.
Algorithm 1Forward space-efficient EEA inversion subroutine
Require:Quantum registers|x⟩|0 n⟩|0m⟩, where the firstn-qubit register is the input/output register, the second
n-qubit register is a large workspace, and the remainingmqubits serve as auxiliary qubits.
Ensure:Output state|x −1 modp⟩|0 n⟩|Γ(x)⟩, where|Γ(x)⟩denotes the remaining forward EEA state.
Initialize registerWork1with (n+ 3) qubits as|100, p⟩▷Using (n+ 3) auxiliary qubits
Initialize registerWork2with (n+ 3) qubits as|000, x⟩▷Padxtonbits on the left
InitializeLengthregisters to|ℓ t := 1, ℓq := 0, ℓr′ := length ofx, ℓs := 0⟩
InitializeControlregisters to|Phase1:= 0,Phase2:= 0,Sign:= 0,Iter:= 0⟩
ifx > p/2then▷Ensures that the algorithm is invertible
Iter←Iter⊕1
end if
ifIter= 1then
x←p−x
end if
fori= 1,2,···,4⌈cn⌉do▷Main iterative loop performing the optimized algorithm steps
Execute Algorithm 3 on the quantum registers
end for
Keep thet ′ part ofWork2as the output value
ifIter= 0then▷Convertt ′ to the positive inverse modulop
t′ ←p−t ′
end if
Reset the input-independent terminal contents of the large workspace to|0 n⟩
Denote the remaining forward EEA state by|Γ(x)⟩
13
