---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 2
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 2

The text below is a page-delimited extraction of the unchanged source PDF.

After Shor’s paper, many authors have quantified theexactgate and qubit
counts of the algorithm, especially for its main cryptographic applications: fac-
toring RSA integers, computing discrete logarithms in finite fields, and in el-
liptic curves of prime order. This paper focuses on the latter. Most of these
studies [19,13,4] have considered logical quantum circuits, that is, without any
implementation constraints. As the technology has matured, several works have
also examined the cost of physically implementing the algorithm under specific
assumptions regarding the capabilities and scale of the available hardware. Both
logical algorithms and physical mappings have advanced in parallel. As an exam-
ple, in 2021, Gidney and Eker˚ a [10] estimated that 20 million superconducting
qubits could be necessary to factor RSA-2048 public keys (classically secure).
A more recent paper by Gidney [9] reached one million qubits. Roughly half of
this 20×reduction (i.e., a factor 4) comes from logical circuits based on (and
improving over) [3], while the rest comes from an improved physical implemen-
tation.
Babbush et al.’s Result.In a recent preprint, Babbush et al. [2] improved logical
quantum circuits for computing elliptic curve discrete logarithms, and discussed
the risks for cryptocurrencies using this non-post-quantum cryptography. In this
paper, we only focus on their logical circuit results.
Babbush et al.’s result is based on an improved (windowed) elliptic curve
point addition circuit on the curvesecp256k1. Their circuits are “kickmick”
circuits, which allow measurement-based uncomputation and phases but are ul-
timately efficient to simulate classically. They did not publish any detail on their
circuit architecture, relying instead on a zero-knowledge proof to prove that they
obtained circuits with the claimed gate and qubit counts, which performed point
addition with a reasonable success probability. Succeeding on random inputs is
enough to run Shor’s algorithm.
The decision not to publish the circuit is justified in [2] by concerns on the
feasibility of such quantum attacks in practice on the medium term. This paper
follows instead the practice of previous works [15,11,9], which intend to make
the result fully reproducible. We believe that a full discussion of the arguments
in [2] would be out of scope of the current paper.
Our Result.We obtain two circuits for point addition onsecp256k1, reaching
similar results as Babbush et al. [2], with a slight improvement in Toffoli gate
count. The design principles of these circuits are described in this paper. We
programmed and tested them using Qarton 1. In particular, the circuits are not
exact: they will fail with some probability. Testing on random inputs shows that
this probability of failure is comparable to the one of [2].
While the gate count varies depending on implementation details, the number
of qubits is around 4.355n+O(√n) in the version that we selected, wherenis the
bit-size of the prime. It could be reduced up to 4.12n+O( √n) using a different
implementation, which would likely increase the Toffoli gate count. Another
1 https://gitlab.inria.fr/capsule/qarton
2
