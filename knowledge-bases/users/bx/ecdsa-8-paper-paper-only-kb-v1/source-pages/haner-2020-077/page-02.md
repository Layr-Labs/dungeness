---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 2
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 2

The text below is a page-delimited extraction of the unchanged source PDF.

curve. Under plausible assumptions about physical error rates, this could translate into 6 .77 ·107
physical qubits [11]. But the number of logical qubits is not the only important cost metric, and
one might prioritize others such as circuit depth, the total number of gates, or the total number of
likely expensive gates such as the Toﬀoli gate or the T gate.
Our goal in this work is not only to improve the circuits proposed by RNSL [ 27], but also
to explore diﬀerent trade-oﬀs favoring diﬀerent cost metrics. To this end, we provide resource
estimates for point addition circuits optimized for depth, T gate count, and width, respectively. We
also report on initial experiments with automatic optimization for T-depth and T gate count. By
using the automatic compilation techniques presented in [ 19], we ﬁnd low T-depth and low T-count
circuits for a modular multiplication component and show signiﬁcant improvements compared to
their manually designed counterparts, however, at a very high cost to the number of qubits.
Beyond alternative choices for low-level arithmetic components, we also improve the higher-
level structure of RNSL’s circuit. While many components stay the same, the most dramatic
improvements come from windowing techniques similar to those proposed by Gidney and Eker˚ a in
[14] and a better memory management via pebbling. For example, instead of copying out the result
in an out-of-place circuit that uses Bennett’s method for embedding an irreversible function in a
reversible computation, the result can be used for the next operation before it is uncomputed. This
technique does not treat modular operations merely as black boxes, but can adaptively reduce the
cost of the higher-level circuit they are used in. Along with a reformulation of the binary extended
Euclidean algorithm, it signiﬁcantly reduces costs for the modular inversion circuit.
One of our main contributions is a modular, testable library 4 of functions for elliptic curve
arithmetic in the Q# programming language for quantum computing [ 31]. These incorporate
diﬀerent possible choices for subroutines like addition and modular multiplication. Besides enabling
unit testing for all components, the Q# development environment allows automated resource
estimation.
We strictly improve RNSL’s estimates under all metrics. For example, for solving the ECDLP
on a 256-bit elliptic curve, we reduce the number of qubits from 2338 to 2124, improve the T-count
by a factor of 119 and the T-depth by a factor of 54. Asymptotically, we estimate that the number
of T gates in our circuit for Shor’s algorithm scales as 436 n3 + o(n3).
Under a diﬀerent trade-oﬀ optimizing for depth, our circuit costs 2 33 T gates with T-depth of
225 and 2871 qubits. Compared to RNSL, this is a factor 6000 reduction in T-depth with only a
22% increase in width. Asymptotically, our circuits can achieve 1115 n3/lg n+ o(n3/lg n) T gates,
or 285n2 + o(n2) T-depth.
Extrapolating analogous values, breaking RSA-3072 would cost 2 34 T gates and 9287 logical
qubits [14]. This suggests that, at similar classical security levels, elliptic curve cryptography is less
secure than RSA against a quantum attack.
2 Preliminaries
This section only gives a very brief discussion of the basic concepts used in this work. For a more
detailed introduction to quantum computing, we refer to [ 24], for Shor’s algorithm see [ 29] and [30]
and for its ECDLP variant [25] and [27].
Quantum computing. A quantum computer acts on quantum states by applying quantum
gates to its qubits. A quantum state is denoted by |x⟩for some label x. We work entirely with
computational basis states, so x is always a bit string. As the fundamental gate set we use
the Cliﬀord+ T gate set and assume that the T gate is by far the most expensive, including
measurements. This is a plausible assumption because, in a quantum computer using a surface
code for error correction, T gates consume special states which require many qubits and many
surface code cycles to produce, and surface codes require frequent measurements for all gates
[10]. A quantum algorithm is described by a sequence of gates in the form of a quantum circuit.
4 Our code will be released under an open source license.
2
