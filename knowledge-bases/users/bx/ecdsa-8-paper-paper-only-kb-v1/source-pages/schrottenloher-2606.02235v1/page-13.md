---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 13
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 13

The text below is a page-delimited extraction of the unchanged source PDF.

ponents to reduce the gate count as much as possible. There are three types of
optimizations that we perform, which we detail below:
–Using appropriate arithmetic circuits. So far all the circuits used are exact
and this has no influence on the success probability.
–Using approximate arithmetic circuits for some steps. This has an influence
on the success probability.
–Using approximate modular arithmetic circuits taking advantage of the spe-
cial form of the prime. This has an influence on the success probability, and
makes our circuit dependent on the instance considered.
Trade-offs Between Implementations.When implementing arithmetic circuits
with two inputs (adders, comparators, etc.), we commonly have the choice be-
tween two implementations:
–Implementations using (almost) no ancillas, based on the CDKM adder [5] or
variants. CDKM-basedn-bit addition and comparison uses 2nToffoli gates,
n-bit controlled addition uses 3nToffoli gates.
–Implementations using aroundnancillas using the Gidney adder [7]. This
adder uses measurement-based uncomputation to uncompute AND gates
efficiently. Addition usesnToffoli gates, controlled addition uses 2nToffoli
gates.
We use strategically components based on the latter when ancillas are available,
such as in the modular squaring step, and components based on the former
when this is not the case. Notably, during the execution of Algorithm 2 (or the
inverse), we have access to roughlynancillas, so we can use the Gidney adder
for the subtraction step. In fact, we do not haveexactlynancillas, because
the circuit itself is using some of them as padding for the registersuandv.
Therefore, we used a hybrid construction as proposed in [7] for the subtraction
step in Algorithm 2, which uses exactly the amount of available ancillas.
Approximate Arithmetic Circuits.Shor’s algorithm requires the point addition
circuit to work with a large constant probability. This leaves us a lot of freedom
to simplify the cost of arithmetic operations. In our circuits, we simplified all
comparisons by comparing the most significant bits only (we typically used 40
to 50 bits to ensure a large probability of success). This simplification is used in
the comparison step of Algorithm 2 and inside the modular arithmetic circuits.
Approximate Modular Arithmetic.The modular arithmetic circuits that we im-
plement, both for the B´ ezout coefficient reconstruction (Algorithm 3) and for
the modular squaring step, are:
–(Controlled) Modular addition:|x, y⟩ 7→ |x, y+xmodq⟩
–Modular doubling:|x⟩ 7→ |2xmodq⟩.
13
