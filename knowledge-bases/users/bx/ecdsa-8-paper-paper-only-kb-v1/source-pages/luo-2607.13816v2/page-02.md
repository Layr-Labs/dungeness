---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 2
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 2

The text below is a page-delimited extraction of the unchanged source PDF.

1 Introduction
Elliptic curve cryptography (ECC), first proposed in the mid-1980s as an alternative framework for public-
key cryptography [Kob87, Mil85], has become one of the foundational primitives in modern cryptographic
systems. The security of ECC-based cryptosystems relies on the computational difficulty of the Elliptic
Curve Discrete Logarithm Problem (ECDLP). Specifically, given an elliptic curve defined over a finite
field, a base pointPon that curve, and another pointQresulting from scalar multiplication ofPby
an unknown integerm, the ECDLP asks for the recovery of the scalarmfrom the two points. Despite
decades of research, no classical algorithm is known that solves the ECDLP in polynomial time of bit
length; the best generic attacks, such as Pollard’s rho method, require Θ( √p) group operations, wherep
denotes the field size of the curve which is exponentially large [GG16].
Compared to classical public-key systems such as RSA [RSA78] and finite-field Diffie-Hellman [DH76],
ECC offers equivalent security with substantially smaller key sizes. For example, according to NIST
recommendations [BD20], a 256-bit elliptic curve provides a security level of 128 bits, which is comparable
to that of RSA with a 3072-bit modulus. This efficiency advantage has led to the widespread adoption
of ECC in both theoretical cryptographic constructions and real-world applications. Specifically, ECC is
used for key exchange [DH76] and digital signature schemes [ElG85, JMV01] in widely deployed protocols,
including transport layer security [BWBG +06], secure shell [SG09], as well as cryptocurrencies such as
Bitcoin [BWQ99, NB08].
In contrast to the computational hardness of ECDLP on classical computers, the security landscape
changes fundamentally in the presence of large-scale quantum computers. In 1994, Shor gave polynomial-
time quantum algorithms for integer factorization and discrete logarithms [Sho94]. Because the ECDLP
is a discrete-logarithm problem in a cyclic subgroup of an elliptic-curve group, it can be efficiently solved
quantumly by Shor’s algorithm whenever the elliptic-curve group operation can be implemented efficiently.
Proos and Zalka subsequently developed an implementation with resource analysis for prime-field ellip-
tic curves [PZ03]. Thus, sufficiently large fault-tolerant quantum computers would break conventional
ECC based on the hardness of the ECDLP. At the same time, the practical implementation of quan-
tum algorithms for cryptography problems remains severely constrained by the limitations of near-term
quantum hardware. For instance, implementing Shor’s algorithm at cryptographically relevant scales
requires a fault-tolerant quantum computer with a large number of logical qubits and circuits, as well as
sufficiently low physical error rates (or equivalently, achievable logical error rates after error correction)
[GE21, Gid25].
Motivated by these challenges, a substantial body of work has focused on reducing the quantum
resource requirements of Shor’s algorithm for integer factorization [Reg25, RV24, KMRVvK25, CFS25]
and the ECDLP [RNSL17, HJN +20, GYCM25, KJW +26, CFS26, BZG +26, Sch26]. In recent studies,
three primary resource metrics have received the most attention: (i) space, measured by the number of
logical qubits; (ii) quantum gate complexity; and (iii) circuit depth. These resources are strongly coupled,
and optimizing one metric often leads to increased costs in others [RNSL17, HJN +20, BZG+26, Sch26].
For each single metric, the state-of-the-art results are:
•In terms of space complexity, Chevignard, Fouque, and Schrottenloher [CFS26] proposed a low-space
2
