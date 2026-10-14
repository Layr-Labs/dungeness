---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 14
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 14

The text below is a page-delimited extraction of the unchanged source PDF.

24. M. A. Nielsen and I. L. Chuang. Quantum Computation and Quantum Information. Cambridge
University Press, Cambridge, UK, 2000.
25. John Proos and Christof Zalka. Shor’s discrete logarithm quantum algorithm for elliptic curves. January
2003. arXiv: quant-ph/0301141.
26. Rich Rines and Isaac Chuang. High Performance Quantum Modular Multipliers. January 2018. arXiv:
quant-ph/1801.01081.
27. Martin Roetteler, Michael Naehrig, Krysta M. Svore, and Kristin E. Lauter. Quantum resource
estimates for computing elliptic curve discrete logarithms. In ASIACRYPT 2017, volume 10625 of
Lecture Notes in Computer Science, pages 241–270. Springer, 2017.
28. Peter Selinger. Quantum circuits of T-depth one. Physical Review A, 87(4):042302, April 2013. arXiv:
1210.0974.
29. Peter W. Shor. Algorithms for quantum computation: Discrete logarithms and factoring. In FOCS
1994, pages 124–134, 1994.
30. Peter W. Shor. Polynomial-time algorithms for prime factorization and discrete logarithms on a
quantum computer. SIAM J. Comput., 26(5):1484–1509, October 1997.
31. Krysta M. Svore, Alan Geller, Matthias Troyer, John Azariah, Christopher E. Granade, Bettina Heim,
Vadym Kliuchnikov, Mariia Mykhailova, Andres Paz, and Martin Roetteler. Q#: Enabling scalable
quantum computing and development with a high-level DSL. In RWDSL@CGO 2018, 2018.
32. Yasuhiro Takahashi, Seiichiro Tani, and Noboru Kunihiro. Quantum addition circuits and unbounded
fan-out. Quantum Information and Computation, 10, 10 2009.
33. Eleonora Testa, Mathias Soeken, Luca G. Amar` u, and Giovanni De Micheli. Reducing the multiplicative
complexity in logic networks for cryptography and security applications. In Design Automation
Conference, page 74, 2019.
34. U.S. Department of Commerce/National Institute of Standards and Technology. Digital Signature
Standard (DSS). FIPS-186-4, 2013. http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.
pdf.
A Alternative approaches
A.1 Modular multiplication.
RNSL provide two circuits for modular multiplication. The ﬁrst is the one proposed by Proos
and Zalka [ 25], which uses a double-and-add approach, where doubling and addition are both
modular operations modulo p. The other is reversible Montgomery multiplication, which uses an
add-and-halve approach and works in Montgomery form. The primary motivation for considering
Montgomery multiplication instead of the straightforward double-and-add method is that modular
reduction is achieved by suitable additions to clear lower order bits and divisions by 2 (i.e. bit
rotations) as part of the whole circuit, not delegated to the addition and halving circuits. This
results in simpler operations per bit.
However, Montgomery multiplication has the downside that it entangles with a register of
auxiliary qubits which must be cleared. In our case, at every point in an elliptic curve point
addition, we have enough spare auxiliary qubits for this. Overall, it is cheaper, even with the
Bennett method, and especially with the multiply-then-add technique of Section 4.1.
Rines and Chuang recently provided high-performance modular multipliers [ 26]. A direct
comparison is diﬃcult, since they give costs in Toﬀoli gates. Our low-T multiplier scales as
38n2 + o(n2) T gates, while their best exact multiplier uses 4 n2 Toﬀoli gates, suggesting perhaps
28n2 T gates. However, some of these Toﬀoli gates might be replaceable with AND gates. Their
adder seems to use 4 .5n additions, slightly more than our 2 n+ O(n/log n) additions. We leave a
true comparison and Q# implementation for future work.
A.2 Modular Inversion.
Proos and Zalka [ 25] (PZ) gave an approach to modular inversion based on precise control of a
bit-shift division operation, with asymptotic complexity of O(n2). There are O(n) iterations of a
round. Each round implements conditional logic by computing state qubits, then using those state
qubits to control some operations on the integer registers.
14
