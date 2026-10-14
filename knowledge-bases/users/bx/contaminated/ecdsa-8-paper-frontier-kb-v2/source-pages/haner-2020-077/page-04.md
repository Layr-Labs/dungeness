---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 4
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 4

The text below is a page-delimited extraction of the unchanged source PDF.

by changing only the middle CNOT gates into Toﬀoli gates. For other circuits, we design controlled
versions as needed.
3 Components
Design strategies. A full cost estimate of Shor’s algorithm requires estimates at all layers of the
architecture, including error correction, layout, and possibly architecture design. We focus only on
the logical layer, and provide circuits that operate on abstracted logical qubits. From this level we
cannot decide which design choices will be optimal. A shallower circuit with more logical qubits
would have smaller error correction overhead and could have fewer physical qubits.
Thus, we provide diﬀerent approaches and tradeoﬀs. We measure the T-depth, T-count, depth
including all gates, and total number of qubits used (“width”). We focus on three strategies,
favouring depth, T-count, or width. We could instead make diﬀerent choices for each sub-circuit of
Shor’s algorithm, resulting in a large parameter space for potential optimization. Since we wrote
Q# functions for all circuits, future work could combine diﬀerent choices for each step.
Toﬀoli and AND gates. As explained by RNSL in the introduction of [ 27], circuits that are
expressed as Toﬀoli gate networks can be implemented exactly over the Cliﬀord+T gate set and can
be classically simulated and tested. Therefore, our circuits are designed using the same approach.
The only source of T-gates in such a circuit is from Toﬀoli gates. In many instances, we know that
the output qubit is in the |0⟩state and we can use a dedicated AND circuit with a lower T-count
instead. We use an AND gate design which combines Jones’ and Selinger’s AND gates [ 17,28]. It
uses 4 T gates, while a Toﬀoli gate uses 7, and the inverse AND †uses no T gates while Toﬀoli†
uses 7. AND gates use 1 auxiliary qubit for T-depth 1; Toﬀoli gates can use 4 auxiliary qubits for
T-depth 1 or none for T-depth 3, see [1].
Integer addition. The adder of lowest known T-count is Gidney’s modiﬁcation of the Cuccaro
et al. adder [ 8] (hereinafter called the CDKMG adder), which uses only 4 n Tgates to add two
n-bit numbers, but uses n auxiliary qubits [12]. The adder of lowest known T-depth is the carry
lookahead adder of Draper et al. [ 9] (hereinafter the DKRS adder), with logarithmic depth but
2n−O(n) auxiliary qubits. The adder of lowest width is due to Takahashi et al. [32] (hereinafter
the TTK adder), which computes in-place using no auxiliary qubits. RNSL used the TTK adder.
The DKRS adder uses 10 n Toﬀoli gates, but of these, 4 n can be replaced with an AND or AND †
gate.
Controlled addition. We provide new methods for controlling the addition circuits. The DKRS
adder uses a circuit to propagate carries, which is uncomputed. These gates do not need to be
controlled. The remaining gates which must be promoted to controlled versions are all CNOT
gates, leading to only a slight increase in the T-count. To control the CDKMG adder, we promote
two CNOT gates per bit to Toﬀoli gates, as Figure 1 shows, and we change the ﬁnal CNOT for the
carry qubit to a Toﬀoli gate. Unfortunately, for both addition circuits, the new Toﬀoli gates cannot
be replaced with AND gates.
Constant addition. When tackling an ECDLP instance, the prime modulus is a classically known
integer, and we need a circuit to add it to integers encoded in quantum registers. The simplest
method allocates a new quantum register, inputs the integer into the quantum register, runs any
quantum addition circuit, then uncomputes the integer from the quantum register to free the
qubits. This simple method is easy to control. Only copying the integer into the quantum register
is controlled, and then an uncontrolled addition is used, as shown in Figure 2a. Copying an integer
uses only X gates, so a controlled copy operation only uses CNOT gates, giving the same T-cost
as uncontrolled quantum addition. We use this strategy with the CDKMG and TTK adders.
4
