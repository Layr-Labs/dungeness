---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 1
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

Improved quantum circuits for elliptic curve discrete
logarithms
Thomas H¨ aner1, Samuel Jaques2 ∗†, Michael Naehrig3, Martin Roetteler1, and Mathias Soeken 1
1 Microsoft Quantum, Redmond, WA, USA
{thhaner,martinro,a-masoek}@microsoft.com
2 Department of Materials, University of Oxford, UK
samuel.jaques@materials.ox.ac.uk
3 Microsoft Research, Redmond, WA, USA
mnaehrig@microsoft.com
Abstract. We present improved quantum circuits for elliptic curve scalar multiplication,
the most costly component in Shor’s algorithm to compute discrete logarithms in elliptic
curve groups. We optimize low-level components such as reversible integer and modular
arithmetic through windowing techniques and more adaptive placement of uncomputing
steps, and improve over previous quantum circuits for modular inversion by reformulating
the binary Euclidean algorithm. Overall, we obtain an aﬃne Weierstrass point addition
circuit that has lower depth and uses fewer T gates than previous circuits. While previous
work mostly focuses on minimizing the total number of qubits, we present various trade-oﬀs
between diﬀerent cost metrics including the number of qubits, circuit depth and T-gate
count. Finally, we provide a full implementation of point addition in the Q# quantum
programming language that allows unit tests and automatic quantum resource estimation
for all components.
Keywords: Quantum cryptanalysis, elliptic curve cryptography, discrete logarithm problem,
Shor’s algorithm, resource estimates.
1 Introduction
Shor’s algorithm [29,30] solves the discrete logarithm problem for ﬁnite abelian groups with only
polynomial cost. When run on a large-scale, fault-tolerant quantum computer, its variant for
elliptic-curve groups could eﬃciently break elliptic curve cryptography with parameters that are
widely used and far out of reach of current classical adversaries.
Barring the eﬃcient classical post-processing of the measured data, Shor’s quantum algorithm
consists of three steps: ﬁrst, a superposition of exponents is created, then those exponents control
the evaluation of a group exponentiation, and ﬁnally a quantum Fourier transform is applied to the
exponent register, which is then measured. The group operations in the exponentiation must be
computed in superposition and this is by far the most expensive step of the algorithm. Thus, the
precise cost of Shor’s algorithm depends on a detailed resource estimation for implementing the
group operation on a quantum computer. For solving the elliptic curve discrete logarithm problem
(ECDLP), the relevant operation is the repeated controlled addition of classical elliptic curve points
to an accumulator point in a quantum register.
The ﬁrst detailed discussion of the elliptic curve case was given by Proos and Zalka in [ 25].
Based on this work, Roetteler et al. [ 27] (hereinafter referred to as RNSL) presented explicit
quantum circuits for point addition and all its components and automatically derive their resource
estimates from a concrete implementation. Both papers focus on minimizing the number of qubits
required to run the algorithm, since its polynomial runtime implies that it will run fast once an
adversary has enough qubits to do so. They count the required number of logical qubits. For
example, RNSL estimate that Shor’s algorithm needs 2330 logical qubits to attack a 256-bit elliptic
∗Partially supported by the University of Oxford Clarendon fund.
†Most of this work was done by Samuel Jaques, while he was an intern at Microsoft Research.
