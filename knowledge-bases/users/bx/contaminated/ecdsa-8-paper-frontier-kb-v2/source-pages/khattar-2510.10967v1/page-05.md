---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 5
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

5
TABLE II: Key parameters and their dual roles in the DQI framework [4], connecting the optimization problem
with the corresponding coding theory problem. For Reed Solomon codes, the field sizeq ≥ m. For our resource
estimates, m = q − 1 and ℓ ≈ n/2.
Symbol Role in Optimization (max-LINSAT/OPI) Role in Coding Theory (C⊥)
q Size of the finite field Fq over which the problem is
defined.
Alphabet size of the code.
b Bit-length of the field elements, whereb = ⌈log2 q⌉. Bit-length of the code symbols.
m Number of constraints in the optimization problem. Block length of the dual codeC⊥.
n Number of variables in the optimization problem. Dimension of the primal codeC; length of the syndrome
of dual codeC⊥.
ℓ Maximum number of errors DQI is configured to handle,
which sets the degree of the enhancing polynomialP.
Theerror-correctioncapability(numberofcorrectableer-
rors) of the decoder forC⊥.
r Size of the allowed setsFi for each constraint. (Not a standard coding parameter, but influences the
problem instance).
B The m × n constraint matrix defining the instance. Generator matrix of the primal codeC = {xB : x ∈ Fn
q }.
B⊺ The n × m matrix used to compute the syndrome. Parity-check matrix of the dual codeC⊥ = {c ∈ Fm
q :
BT c = 0}.
A. The DQI Quantum Circuit: An Improved Construction for Qubit Efficiency
The goal of the Decoded Quantum Interferometry (DQI) circuit is to efficiently prepare the state |P(f)⟩ =P
x P(f(x))|x⟩, whereP is an appropriately normalized degree-ℓ polynomial. In the original construction[4, Section-
8], the algorithm requires simultaneous instantiation of anmb-sized error register, to hold a superposition of error
patterns e ∈ Fm
q , and an nb-sized syndrome register to hold the syndrome valuess = BT e. This leads to a total
space complexity of(m + n)b plus the ancilla overhead due to reversible decoding. Note that the decoding problem is
defined on an input of sizenb (the length of the syndrome), and hence for the regime wherem ≫ n, the multiplicative
mb qubit overhead in the DQI circuit is prohibitive.
We present an optimized circuit construction that significantly reduces qubit overhead by reformulating the Dicke
state preparation, syndrome computation, and reversible decoding steps (stages 1, 2 and 3). The Dicke states in
the DQI circuit are used to encode the locations ofℓ < n
2 errors in the length m codeword. Instead of using a
dense representation consisting ofm qubits, we use a sparse representation consisting ofℓ · ⌈log2 m⌉ ≤ℓ · b qubits
to encode this information. We show how to efficiently prepare Sparse Dicke States in Appendix B. Next, instead of
generating the entiremb-qubit error state|e⟩ to encode the values of errors at each of them locations in the codeword,
we employ a sequential approach utilizing Measurement-Based Uncomputation (MBU) [25, 26]. We iterate through
the m constraints, generate one error symbolei (of size b qubits) at a time, update the syndrome register with its
contribution, and immediately uncomputeei via measurement in the X-basis. This leads to phase errors that we
later fix as part of the reversible decoding step, where we sequentially generate each decoded error termei and apply
a phase fixup using the measurement resultci. This allows us to reuse a singleb-qubit ancilla register for all error
terms during state preparation. Using Sparse Dicke state preparation and sequential computation of the error terms,
the ancilla cost for preparing thenb-qubit syndrome register reduces tonb qubits. We will later show how to perform
the reversible decoding on thenb-qubit syndrome register usingnb + O(log2(n)) ancilla qubits, thus achieving a total
space cost of2nb + O(log2(n)) qubits.
The following description of the DQI quantum circuit is for the general max-LINSAT case over a Galois fieldFq.
The construction proceeds through four main stages. The evolution of the quantum state across these stages is
summarized below, utilizing an error locator register (ℓ · b qubits), an error value register (b qubits), and a syndrome
register (n · b qubits). We omit normalization factors for clarity.
