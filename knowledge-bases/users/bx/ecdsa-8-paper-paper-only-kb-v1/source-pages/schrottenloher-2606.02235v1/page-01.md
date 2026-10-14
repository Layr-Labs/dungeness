---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 1
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

Optimized Point Addition Circuits for Elliptic
Curve Discrete Logarithms
Andr´ e Schrottenloher
Univ Rennes, Inria, CNRS, IRISA, Rennes, France
firstname.lastname@inria.fr
Abstract.Shor’s algorithm represents the main threat of quantum com-
puters to cryptography. In order to precisely understand its feasibility,
many authors have worked towards reducing its costs, either at the logi-
cal level (assuming a fault-tolerant architecture), or at the physical level
(taking into account the constraints of envisioned hardware). In partic-
ular, recent works by Chevignard et al. (CRYPTO 2024) and Gidney
(arXiv 2025) used improved arithmetic to significantly reduce the qubit
cost of factoring RSA public keys.
Even more recently, Babbush et al. (arXiv 2026) improved the cost of
computing elliptic curve discrete logarithms, with a reduction of a factor
2 to 3 in gate count and qubit count compared to a previous work by
Litinski (arXiv 2023). Their result relies on optimized point addition
circuits on elliptic curves over prime fields. However they did not reveal
their logical quantum circuits, relying instead on a zero-knowledge proof.
In this paper, we detail a quantum logical circuit architecture which
gives similar results as Babbush et al., with a slightly higher number of
qubits (around 1.5% increase) and a slightly smaller Toffoli gate count
(between 6.5% and 10% reduction) for the curve secp256k1. We also
give gate counts for a generic variant of the circuit, which is valid for any
prime field.
Keywords:Quantum cryptanalysis, Shor’s algorithm, Discrete logarithms, El-
liptic curves, Quantum resource estimates
1 Introduction
Since Shor’s breakthrough paper [21], it has been known that once a large-
scale quantum computer becomes available, public-key cryptography based on
the hardness of integer factoring (e.g., the RSA cryptosystem) and discrete loga-
rithms (e.g., cryptography based on finite fields [16] and elliptic curve groups [16])
can be considered as broken, the underlying problems being solved in quantum
polynomial time.
This impact motivates the early adoption of post-quantum cryptography,
with a first batch of public-key encryption and signature schemes standardized
by the NIST as a result of a large-scale public standardization process [18].
arXiv:2606.02235v1  [quant-ph]  1 Jun 2026
