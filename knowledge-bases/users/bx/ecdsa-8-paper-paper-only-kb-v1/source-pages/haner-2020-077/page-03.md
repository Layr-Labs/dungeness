---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 3
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 3

The text below is a page-delimited extraction of the unchanged source PDF.

We use standard quantum circuit diagrams, with black triangles representing output registers.
For circuit design and testing, we use circuits built from NOT, CNOT and Toﬀoli gates as those
can be simulated eﬃciently at scale on classical inputs [ 27]. However, for cost estimation, we use
decompositions over the Cliﬀord+T gate set, such as the ones introduced in [1,12,28].
Shor’s algorithm for the ECDLP. Let an instance of the ECDLP be given by two Fp-rational
points P,Q ∈E(Fp) on an elliptic curve E over a ﬁnite ﬁeld of large characteristic p such that
ord(P) = r, Q∈⟨P⟩. The problem is to ﬁnd the unique integer m∈{1,...,r }such that Q= mP.
Shor’s algorithm applies a Hadamard transform to two registers with n+ 1 qubits initialized to |0⟩
to create the state 1
2n+1
∑2n+1−1
k,ℓ=0 |k⟩|ℓ⟩. Next, the state 1
2n+1
∑2n+1−1
k,ℓ=0 |k⟩|ℓ⟩|kP + ℓQ⟩is computed
using the elliptic curve group law. A quantum Fourier transform QFT2n+1 on n+1 qubits is applied
to both |k⟩and |ℓ⟩and the 2(n+ 1) qubits in |k⟩|ℓ⟩are measured. Classical post-processing then
yields the discrete logarithm m. We assume that the algorithm is modiﬁed using the semiclassical
Fourier transform method [15], which means that a small number of qubits can be re-used to act
as the 2n+ 2 qubits for |k⟩|ℓ⟩. RNSL use only one qubit for this [ 27], but we use more than one
to allow windowed arithmetic (see Section 5.1). The most cost-intensive part is the double-scalar
multiplication to compute |kP + ℓQ⟩.
Functions as quantum circuits. The elliptic curve group law is built from various classical
functions that operate on bit strings of varying lengths n. For any function f, we use Uf to denote
a quantum circuit that computes f.
We often want Uf to compute f in-place, meaning it has the action Uf : |x⟩↦→| f(x)⟩on inputs
x∈{0,1}n. If Uf is built out of Cliﬀord+ T gates, each gate is easy to invert; thus, an in-place
circuit Uf automatically yields an in-place circuit U†
f that computes f−1. As quantum circuits
need to be reversible, an in-place circuit is not always possible, e.g. if f is not injective.
As an example consider modular multiplication. Let p be an integer modulus. The function
f : (x,y) ↦→(x,xy mod p) is injective for inputs x,y ∈Z/pZ that are co-prime to p. Its inverse is
modular division. At present, the best circuits we know to compute modular division use some
variant of the Euclidean algorithm. Thus, an in-place modular multiplication circuit would either
be more expensive than the Euclidean algorithm or would provide a state-of-the-art circuit for
modular division.
When an in-place circuit is not possible, Uf needs to implement f out-of-place as |x⟩|0⟩n ↦→
|x⟩|f(x)⟩. Some circuits might require a number m of auxiliary qubits, such that
Uf : |x⟩|0⟩n |0⟩m Uf
↦−−→|x⟩|f(x)⟩|g(x)⟩, (1)
where g is some function of the input. The auxiliary qubits are entangled with the other registers,
and g must be uncomputed before the end of the computation to restore them to their original
state. In our circuit diagrams, white triangles indicate such outputs.
If it is too costly to compute g(x) from xand f(x), one can use a method due to Bennett [ 4] to
clean any auxiliary qubits. By adding another n-qubit register, the output f(x) is “copied” to that
register using CNOT gates. Then, the inverse U†
f is applied. This trick roughly doubles the cost to
reversibly compute f.
In a sequence of out-of-place circuits, uncomputing early steps prevents us from uncomputing
later steps. To make the full algorithm work, we either need to keep intermediate steps at the cost
of an increasing number of qubits or recompute them repeatedly at the cost of additional gates.
This is an instance of a general problem known as a pebbling game.
Controlled circuits. As larger circuits are composed from smaller ones, the smaller circuit often
needs to be controlled with a single qubit. We can “promote” each Cliﬀord+ T gate in the smaller
circuit into a controlled variant, which is expensive, e.g., for CNOT and Toﬀoli gates. Thus, we want
to optimize which gates we control. For example, a circuit using Bennett’s trick can be controlled
3
