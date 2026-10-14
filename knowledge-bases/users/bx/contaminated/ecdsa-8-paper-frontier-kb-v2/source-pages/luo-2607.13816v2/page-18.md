---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 18
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 18

The text below is a page-delimited extraction of the unchanged source PDF.

and overall gate complexity.
Removing redundant arithmetic and shift operations.In the baseline version, several arithmetic
and shift operations between different phases are functionally redundant. Specifically, we have:
In phases 1 and 2: comparison, addition, subtraction between (r,2 ℓsr′);
In phases 3 and 4: comparison, addition, subtraction between (t ′,2 ℓst);
In phases 1 and 3: a one-position left shift onWork2;
In phases 2 and 4: a one-position right shift onWork2.
By combining the control conditions of these operations (or equivalently, the corresponding quantum
control wires), we can eliminate redundant operations from the circuit. This optimization results in a
total of two groups of location-controlled addition/subtraction operations and two location-controlled
swaps in one step. Here,location-controlrefers to arithmetic operations applied conditionally on specific
positions of the twoWorkregisters, with the active positions indicated by theLengthregisters.
Merging location-controlled swaps.To further decrease the circuit depth and gate count, we observe
that the two location-controlled swaps appearing in phases 2 and 3 act on the same qubit position of
Work1. We merge them into a single swap controlled byPhase1⊕Phase2. The required update ofℓ q
depends on the phase:ℓ q is increased in phase 2 and decreased in phase 3.
Algorithm pseudocode and overall complexity.After applying the above optimizations, the over-
all asymptotic quantum resource estimation per step is summarized as follows:
•Five location-controlled arithmetic operations, including one swap, two additions, and two subtrac-
tions; along with four length updates at the termination step of an EEA iteration. Each of these
operations costsO(n) gates in the implementation presented in Section 4.
•Four position shifts and one (n+ 3)-qubit SWAP, each requiringO(n) quantum gates.
With these optimizations, one step of our space-efficient EEA proceeds as in Algorithm 3.
4 Quantum Circuit Implementation of Modular Inversion
In this section, we present the explicit quantum circuit implementation of a single step of the space-
efficient EEA with register sharing, as described in Algorithm 3. Throughout the section, we use the
same quantum register notation as in the algorithm.
The full circuit construction is, however, too complex to be depicted within a small number of circuit
diagrams. This difficulty is mainly due to the presence of location-controlled arithmetic operations,
which are highly non-standard. To present the construction in a relatively more explicit manner, we first
describe the overall circuit structure in Section 4.1, where the location-controlled arithmetic operations
18
