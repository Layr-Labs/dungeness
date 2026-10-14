---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 1
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

Measurement-based uncomputation of
quantum circuits for modular arithmetic
Alessandro Luongo1,2, Antonio Michele Miti3, Varun Narasimhachar4, and Adithya Sireesh5,*
1Centre for Quantum Technologies, National University of Singapore, Singapore
2Inveriant Pte. Ltd., Singapore
3Department of Mathematics, Sapienza Universit` a di Roma, Rome, Italy
4A*STAR Quantum Innovation Centre (Q.InC), Institute of High Performance Computing (IHPC),
Agency for Science, Technology and Research (A*STAR), Singapore.
5School of Informatics, University of Edinburgh, Scotland, United Kingdom
*Corresponding author: asireesh@ed.ac.uk
July 30, 2024
Abstract
Measurement-based uncomputation (MBU) is a technique used to perform probabilistic
uncomputation of quantum circuits. We formalize this technique for the case of single-qubit
registers, and we show applications to modular arithmetic. First, we present formal statements
for several variations of quantum circuits performing non-modular addition: controlled addition,
addition by a constant, and controlled addition by a constant. We do the same for subtraction
and comparison circuits. This addresses gaps in the current literature, where some of these
variants were previously unexplored. Then, we shift our attention to modular arithmetic, where
again we present formal statements for modular addition, controlled modular addition, modular
addition by a constant, and controlled modular addition by a constant, using different kinds of
plain adders and combinations thereof. We introduce and prove a “MBU lemma” in the context
of single-qubit registers, which we apply to all aforementioned modular arithmetic circuits. Using
MBU, we reduce the Toffoli count and depth by 10% to 15% for modular adders based on the
architecture of [VBE96], and by almost 25% for modular adders based on the architecture of
[Bea02]. Our results have the potential to improve other circuits for modular arithmetic, such
as modular multiplication and modular exponentiation, and can find applications in quantum
cryptanalysis.
1 Introduction
Consider a quantum circuit Uf computing a Boolean function f : {0, 1}n → {0, 1}m between bit
strings. When f is invertible (meaning that f is injective and n = m) we say that Uf computes f
in-place if it performs the mapping
Uf : |x⟩n 7→ |f(x)⟩m (1)
for any bit string x ∈ {0, 1}n, where we use the subscripts to denote the number of qubits in a
quantum register. An in-place implementation is not always possible. In the most general case, one
needs to compute f out-of-place, meaning that the circuit Uf realises the following mapping
Uf : |x⟩n |0⟩m 7→ |x⟩n |f(x)⟩m . (2)
1
arXiv:2407.20167v1  [quant-ph]  29 Jul 2024
