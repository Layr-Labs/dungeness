---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 6
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 6

The text below is a page-delimited extraction of the unchanged source PDF.

4 Modular arithmetic
Because modular reduction is irreversible, we cannot design an in-place circuit which maps x to
xmod N without creating some auxiliary qubits that represent the quotient ⌊x/N⌋. Any algorithm
for modular arithmetic that uses many modular reductions thus creates signiﬁcant qubit overhead.
Instead, we design bespoke circuits for each operation. Primarily, we follow RNSL [ 27]. We ﬁnd
that working in Montgomery representation [ 21] has the lowest costs. For an odd modulus p with
n= ⌈lg p⌉, the Montgomery representation of an integer x is x2n mod p.
We use the modular addition circuit from RNSL. Note that addition in Montgomery repre-
sentation is the same as in standard representation. For controlled modular addition, we only
need to control two operations, as Figure 3 shows. This automatically gives us modular addition
by a constant, by replacing the quantum-quantum addition and comparison circuits by their
quantum-classical counterparts.
|x⟩
|y⟩
|0⟩
|ctrl⟩
n
n + −p
+p >
Fig. 3: Controlled modular addition.
4.1 Multiplication and squaring
RNSL provide two circuits each for multiplication and squaring. We use the one that operates on
n-bit integers in Montgomery form with 2 n additions and n halvings, and justify this choice in
Appendix A.1. This circuit is a direct translation of classical Montgomery multiplication.
Windowed arithmetic. Windowed multiplication, such as [ 13], is not directly possible in our
setting because we multiply two quantum integers, but we can adapt some of these techniques to
our setting. When computing x·y, the Montgomery multiplier uses the ith bit of |x⟩to control an
addition of |y⟩to the output register. It then copies the lowest bit of the output to an auxiliary
register |m⟩and uses this bit to control addition of the modulus p. This ensures that the sum is
even, and so we rotate the register to divide by 2.
When using a window of size k, the integer xis split into k-bit words x(1),...,x (n/k), analogous
to classical interleaved radix-2k Montgomery multiplication. The k-bit value x(i) is multiplied with
y, adding the (n+ k)-bit result to the output register. To add a suitable multiple of pto the output
to set the k least signiﬁcant bits to 0, these k bits are copied to an auxiliary register mi. The
multiple tmi p such that tmi p+ mi ≡0 mod 2k can be looked up from a classically pre-computed
table T, where T[mi] = tmi p for tmi ≡p−1mi mod 2k.
We use the bits in mi as an address for a sequential quantum look-up [ 2]5, writing the resulting
(n+ k)-bit integer tmi p into an auxiliary register. Then an uncontrolled addition of tmi p into the
output register clears the bottom k bits, so we can cyclically rotate by k bits. Figure 4 illustrates
this process.
5 This technique is referred to as QROM in [2]; some papers also call it QRAM ; we use quantum look-up
to distinguish it from quantum random oracles and to emphasize that it is constructed out of Cliﬀord+ T
gates and does not require special QRAM technology.
6
