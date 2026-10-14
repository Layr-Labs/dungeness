---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 26
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 26

The text below is a page-delimited extraction of the unchanged source PDF.

26
Proof. We analyze the complexity of the DQI algorithm stages (as described in Section IIA). The conditions ensure
that basic arithmetic operations (addition, multiplication) in Fq require eO(b) = eO(1) gates. The degree of the
enhancing polynomial isl = O(n) = O(m).
• Stage 1: Dicke State Preparation. Standard dense Dicke state preparation requires O(lm) = O(m2)
gates [47]. To achieve near linear time, we describe a new Dicke State Preparation method in Appendix B2,
which employs a reversible implementation of a Divide and Conquer unranking strategy, accelerated by Binary
Splitting. As analyzed in the appendix, the total gate complexity for this step iseO(m).
• Stage 2: Syndrome Computation. We analyze the complexity of the sequential approach described in
Section IIA, but using dense Dicke States instead of sparse Dicke States. This stage iteratesm times. Below,
we show that the cost of each iteration iseO(1) resulting in a total cost ofeO(m) :
– Constraint Encoding and Error Generation (ApplyGi): The gateGi can be implemented using QFTs over
Fq and one call to the oracleUi [4, Section 14.4]. The cost of the QFT iseO(b) = eO(1). By assumption,
the cost ofUi is eO(1). Thus, the cost ofGi is eO(1).
– Syndrome Update: We update the syndrome register withBT
i · ei. This involves one field multiplication
and addition, costingeO(1) gates.
• Stage 3: Reversible Decoding. We reversibly decode the Reed-Solomon codeC⊥. By Lemma IV.1, this
requires eO(m) field operations, resulting ineO(m · b) = eO(m) gates.
• Stage 4: Final Transformation (IQFT).Applying the inverse QFT overFn
q . This takes eO(n · b) = eO(m)
gates.
Total Complexity:Since each stage requireseO(m) gates, the total gate complexity of the DQI algorithm under
the stated conditions iseO(m).
The conditions required for Theorem IV.2 are met, for instance, whenq is small (e.g., the binary extension fields
analyzed in this paper, providedb is polylogarithmic inm) and when the OPI instance has some special structure
that allows for efficient constraint encoding. For example, in the Polynomial Approximation problem, the subsetsFi
are contiguous intervals [48], allowingUi to be implemented efficiently via comparators ineO(b) gates.
It is important to contrast this with the general OPI case studied in Section 5 of [4], wherem ≈ q and the subsets
Fi are arbitrary.
Corollary IV.1. Consider the general OPI problem overFq where m = q − 1 and the subsetsFi are arbitrary (e.g.,
the balanced case where|Fi| ≈q/2). The DQI algorithm requireseO(m2) elementary quantum gates.
Proof. In this case, b = O(log m) = eO(1). However, implementing the oracle Ui or the gate Gi for an arbitrary
function defined by a subset of sizeO(q) generally requires eO(q) = eO(m) gates (e.g., using QROM or generic state
preparation [27]). The total cost of Stage 2 (Constraint Encoding) becomesm· eO(m) = eO(m2), dominating the overall
complexity.
B. Asymptotic Optimality
Combining Theorem IV.2 and Theorem III.7 we have Theorem I.1:
Theorem I.1.There is an NP-search / optimization problem where the runtime of the best-known classical algorithm
for the problem is2N and which can be solved with a circuit ofeO(N) quantum gates.
Since any quantum circuit ofn gates can be simulated in timeO(2n), our speedup provides the largest separation
possible between classical and quantum runtimes. This is somewhat extraordinary since OPI is essentially a contrived
problem and seems (to us) no more “quantum" or “natural" than e.g. factoring or period-finding. We speculate
informally on the outlook for this situation below.
• Faster Classical Algorithms for OPI:Although the best attacks we are currently aware of for OPI take
exponential time in the number of evaluation points, it is certainly possible that better algorithms exist. It is
interesting to note that none of the algorithms we know about leverage the low-degree algebraic structure and
instead treat it as an arbitrary max-LINSAT problem.
