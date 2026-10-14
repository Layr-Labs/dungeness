---
title: ECDSA Fail 32-Paper Knowledge Base
generated: 2026-09-11
paper_count: 32
scope: Reversible secp256k1 point addition, arithmetic, inversion, measurement-assisted cleanup, and qubit-lifetime scheduling
benchmark_objective: Average executed Toffolis multiplied by peak live qubits
source_policy: Publicly downloadable primary-source PDFs only
evidence_policy: Paper statements are separated from transfer inferences and experiment proposals
---

# ECDSA Fail 32-Paper Knowledge Base

## Purpose

This knowledge base decomposes the 32-paper coverage-first collection into reusable evidence cards for designing and reviewing ECDSA Fail circuits. It is organized around mechanisms, interfaces, costs, and cleanup obligations rather than around prose summaries.

The companion PDFs are in [`ecdsa-fail-32-papers`](./papers/), and the selection rationale is in [`ecdsa-fail-32-paper-coverage-first.md`](./ecdsa-fail-32-paper-coverage-first.md).

## Decomposition protocol

These are the rules used to turn each paper into knowledge-base entries.

1. **Freeze identity first.** Record the exact paper, public source, version when visible, and local PDF before extracting claims.
2. **Decompose by mechanism, not section order.** A card should answer one reusable question: what transformation is performed, what invariant makes it work, what it costs, or how it is cleaned up.
3. **Make the circuit contract explicit.** Record inputs, outputs, representation, coordinate system, in-place/out-of-place behavior, controls, garbage, exceptional cases, and whether the output is canonical, scaled, compressed, or implicit.
4. **Track a resource vector, not one headline number.** Keep Toffoli/CCZ or T count, depth, clean ancillas, dirty ancillas, classical records, measurements, and approximation error separate until a common cost model is chosen.
5. **Trace lifetimes through cleanup.** A qubit is not reusable merely because its logical value is no longer wanted. Record the inverse computation, measurement repair, phase obligation, recomputation dependency, and peak-live point.
6. **Separate direct evidence from transfer inference.** Numerical results are portable only when the arithmetic domain, representation, gate library, and interface match. An idea transferred from another field or curve is labeled as an inference.
7. **Normalize before comparing.** Translate candidate circuits to the benchmark's representation, reversibility rules, measurement model, and `average executed Toffolis × peak live qubits` objective before ranking them.
8. **Preserve negative knowledge.** Record when a construction is approximate, non-reproducible, out-of-place, asymptotic-only, specialized to a classical operand, or likely beyond the 256-bit crossover.
9. **Cross-link consumers and producers.** A locally expensive primitive can still win if its garbage is consumed before reversal; a locally cheap primitive can lose after conversion and cleanup.
10. **End with a falsifiable experiment.** Transfer claims should identify the target benchmark module, expected effect, and the validation needed to accept or reject the idea.

## Evidence-card conventions

- **Direct evidence** means the paper explicitly states or derives the result.
- **Transfer inference** means this knowledge base applies the mechanism to secp256k1 or the ECDSA Fail benchmark.
- **Experiment** means a proposed implementation or measurement, not a result already established by the paper.
- Page references are one-based physical PDF pages in the local collection.
- `n` is the relevant operand width unless a card states otherwise.
- Costs are not considered comparable until their primitive library and cleanup policy match.

## Quick-reference matrix

| # | Paper | Main reusable mechanism | Headline result | Main import warning | Likely modules |
|---:|---|---|---|---|---|
| 1 | Babbush et al. | Certified secp256k1 frontier, windowed point addition | 1,175 qubits/2.7M Toffolis or 1,425/2.1M per point addition | Detailed circuit is not public; some costs are average and approximate | whole circuit, `pingpong` |
| 2 | Schrottenloher | Reproducible frontier point addition | 1,192 qubits/\(2^{21.19}\) Toffolis or 1,446/\(2^{20.83}\) | Approximate comparisons and highly tuned scheduling | `pingpong`, `modular`, inversion |
| 3 | Luo et al. | Register sharing and X-basis release of a large register | \(3n+6\log_2n+O(1)\) qubits; 835 at \(n=256\) | Very high Toffoli count and classical feed-forward obligations | inversion, lifetime scheduling |
| 4 | Chevignard et al. | Projective RNS computation with compressed output | \(3.12n+o(n)\) qubits | Changes output contract and needs many runs; \(\widetilde O(n^4)\) gates | alternative architecture |
| 5 | Kim et al. | Affine/projective and carry-save depth-width tradeoffs | 58–82% lower qubit×T-depth than Häner et al. | Optimizes depth products, not the benchmark objective directly | point formulas, multiplier |
| 6 | Häner et al. | Fixed-round Kaliski inversion and producer-consumer fusion | 2,124 qubits for a 256-bit attack design | Montgomery representation and tightly coupled cleanup | `pingpong`, inversion, `square` |
| 7 | Roetteler et al. | First detailed testable prime-field ECDLP stack | Point add: \(9n+2\lceil\log_2n\rceil+10\) qubits | Superseded resource constants | correctness baseline |
| 8 | Proos–Zalka | Register sharing, random shift, bounded variable-time EEA | Roughly \(6n\) logical qubits at high level | Non-explicit circuit and tolerated fidelity loss | exceptional cases, inversion |
| 9 | Litinski | Global weighting, windowing, and batched inversion | \((44+65/k)\)M Toffolis per key | Batch savings need multiple instances/keys | whole-circuit prioritization |
| 10 | Renes et al. | Complete short-Weierstrass projective formulas | Generic complete addition: 12 field multiplications | Field-operation counts omit reversible garbage and conversion | point-formula alternative |
| 11 | Hisil et al. | Unified/complete twisted-Edwards formulas | \(8M+1D\) for a specialized addition schedule | Different curve model and extra coordinate | schedule inspiration |
| 12 | Sarkar–Seo | Binary-field point addition and carryless arithmetic | Up to 92%+ qubit×depth improvement out of place | \(\mathrm{GF}(2^n)\) costs do not transfer to prime fields | architecture patterns |
| 13 | Cuccaro et al. | One-ancilla MAJ/UMA ripple carry | Full add: \(2n-1\) Toffolis | Linear depth | add, subtract, compare |
| 14 | Draper et al. QCLA | Prefix generate/propagate carries | \(O(\log n)\) depth | Linear extra width may worsen peak-live objective | parallel carry experiments |
| 15 | Draper Fourier adder | Addition by phase rotations in Fourier basis | No explicit carry register | Rotation synthesis, approximation, basis conversion | representation experiment |
| 16 | Gidney 2018 | Temporary logical AND and zero-T measurement erasure | Adder: \(4n-4\) T gates | Measurement conditions and extra ancillas | carry ladders |
| 17 | Gidney 2025 | Constant addition with vented carries and borrowed dirties | \(4n\pm O(1)\) with 3 clean ancillas | Deferred classical phase obligations | `const_arith`, folds |
| 18 | Baksi et al. | Wallace/Dadda quantum carry-save trees | QFA: 1 Toffoli and 5 CNOTs | High width; useful mainly for multioperand sums | multiplier, `square` |
| 19 | Gidney windowing | Chunked table lookups and cheap unlookup | Product-add \(O(n^2/\log n)\) | Strongest when one factor is classical | `const_arith`, multiplier |
| 20 | Gidney approximation | Coset encodings and oblivious carry runways | Runway deviation \(2^{-m}\) | Errors accumulate and representation changes | approximate add |
| 21 | Häner–Roetteler–Svore | Very-low-width modular arithmetic toolkit | Factoring architecture with \(2n+2\) qubits | Older constants and repeated recomputation | low-width modular primitives |
| 22 | Luongo et al. | Measurement-based uncomputation of predicates | Modular add \(3.5n\) expected Toffolis | Repair oracle and classical result must remain valid | reduction flags, comparators |
| 23 | Rines–Chuang | Division, Montgomery, and Barrett multiplier families | Ripple variants near \(3n\) qubits and \(4n^2\) Toffolis | Mostly leading-order and adder-dependent | `modular`, multiplier |
| 24 | Gidney Karatsuba | Inline recursive outputs to avoid stored intermediates | \(O(n)\) space and \(O(n^{\log_2 3})\) operations | Practical crossover reported near 10,000 bits | scheduling principle |
| 25 | Lee et al. | Exact reversible Crandall reduction | Two folds plus one normalization for small \(c\) | Forward circuit retains garbage; paper is very recent | `modular`, `square` |
| 26 | Bernstein–Yang | Fixed-count divsteps and narrow control flow | About \(2.8821n\) steps suffice asymptotically | Classical algorithm; reversible resource costs not supplied | inversion schedule |
| 27 | Mukhopadhyay et al. | Fused compare-and-conditional-subtract | Type I uses \(3k-1\) Toffolis and \(2k+1\) total qubits | Some lowest-T variants use measurement and are not fully reversible | compare, divide, EEA |
| 28 | Khattar et al. | Dialog/transition trace instead of materialized Bézout data | Leading-order \(2nb\) qubits in its polynomial setting | Quantitative costs are for \(\mathrm{GF}(2^b)\) | inversion history |
| 29 | Litinski schoolbook | Controlled add-subtract multiplier | \(n^2+4n+3\) Toffolis | Prime multiplier is out of place and Montgomery-form | multiplier, `modular` |
| 30 | Kornerup et al. | Spooky pebbling and phase ghosts | Tight line time-qubit tradeoffs | Classical measurement records remain live | global lifetime schedule |
| 31 | Paradis et al. | Automatic space-constrained recomputation/uncomputation | Up to 96% fewer ancilla qubits in evaluation | Primarily qfree gates; heuristic may fail | compiler/lifetime audit |
| 32 | Liu et al. | Unified clean/dirty ancilla uncomputation | First dirty-ancilla synthesis framework; existence is coNP-hard | Rewrite method is incomplete and has graph/H-gate limits | dirty-register lending |

# A. Whole-circuit and point-addition architectures

## 1. Babbush et al., *Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities: Resource Estimates and Mitigations*

Source: [arXiv:2603.28846](https://arxiv.org/abs/2603.28846) · [local PDF](./papers/01-babbush-securing-ecc-cryptocurrencies.pdf)

Retrieval tags: `secp256k1`, `resource frontier`, `windowed point addition`, `average Toffoli`, `attestation`

### KB-BAB-01 — Certified point-addition and whole-attack envelopes

**Direct evidence.** The paper certifies two secp256k1 point-addition operating points: approximately 1,175 logical qubits with 2.7 million Toffolis per point addition, and 1,425 logical qubits with 2.1 million Toffolis. At whole-attack level it reports envelopes around 1,200 qubits/90 million Toffolis and 1,450 qubits/70 million Toffolis. (PDF pp. 1 and 55–57.)

**Transfer inference.** These points are the benchmark frontier to beat, but the correct comparison unit is the exact point-addition interface and its high-water schedule, not a stand-alone arithmetic primitive.

### KB-BAB-02 — Windowing and average-executed nonlinear gates

**Direct evidence.** The architecture uses in-place windowed point additions, a window size of 16, and three table lookups per addition. The resource accounting uses average executed CCX/CCZ operations for input-dependent branches rather than simply counting every syntactically present gate. (PDF pp. 54–57.)

**Experiment.** Instrument candidate circuits with branch probabilities and separately report static gates, average executed Toffolis, and peak live qubits.

### KB-BAB-03 — Reproducibility boundary

**Direct evidence.** The detailed attack circuit is not released; a zero-knowledge attestation is used to certify stated bounds. Approximate-correctness behavior is tested on 9,024 inputs rather than proved by a fully public circuit artifact. (PDF pp. 1 and 54–57.)

**Warning.** The paper is a target envelope and design clue, not a drop-in implementation. Any benchmark submission needs its own independently testable semantics.

## 2. Schrottenloher, *Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms*

Source: [IACR ePrint 2026/1128](https://eprint.iacr.org/2026/1128) · [local PDF](./papers/02-schrottenloher-optimized-point-addition.pdf)

Retrieval tags: `public frontier`, `canonical residues`, `pseudo-Mersenne`, `Dialog`, `approximate comparator`

### KB-SCR-01 — Reproducible frontier operating points

**Direct evidence.** For secp256k1 the paper reports a space-oriented point addition using 1,192 qubits and \(2^{21.19}\) Toffolis, and a gate-oriented point addition using 1,446 qubits and \(2^{20.83}\) Toffolis. Including the 16-qubit window register, the corresponding whole circuits use 1,208 qubits/\(2^{26.11}\) Toffolis and 1,462 qubits/\(2^{25.78}\). (PDF pp. 3–4.)

**Transfer inference.** This is the strongest directly reproducible architectural comparator in the set.

### KB-SCR-02 — Architecture that reaches the frontier

**Direct evidence.** The construction combines affine point addition, three lookups, a split between Euclidean evolution and Bézout reconstruction, direct in-place multiplication, canonical rather than Montgomery residues, truncated most-significant-bit comparisons, and pseudo-Mersenne reduction. Its selected space design is about \(4.355n\) qubits against a stated lower bound of \(4.12n+O(\sqrt n)\). (PDF pp. 2–10.)

**Experiment.** Reproduce each optimization independently so its marginal effect on Toffolis and peak live qubits is measurable.

### KB-SCR-03 — Approximation budget is part of the interface

**Direct evidence.** Some comparisons inspect only leading bits. The paper reports no failures in 10,000 tests and an estimated aggregate failure probability at most about \(2^{-13.3}\) for the chosen parameters. (PDF pp. 10–14.)

**Warning.** A truncated comparator is not interchangeable with an exact comparator unless the benchmark accepts the error model and the complete point-addition error budget is tracked.

## 3. Luo et al., *Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition*

Source: [arXiv:2607.13816](https://arxiv.org/abs/2607.13816) · [local PDF](./papers/03-luo-space-efficient-point-addition.pdf)

Retrieval tags: `register sharing`, `mid-circuit measurement`, `space-efficient EEA`, `phase correction`

### KB-LSE-01 — Qubit-first point-addition bound

**Direct evidence.** The full attack is stated to use \(3n+6\lfloor\log_2n\rfloor+O(1)\) qubits and \(1056n^3/\log n+O(n^2)\) Toffolis. For secp256k1 the quoted point is 835 qubits and \(2^{30.88}\) Toffolis. The inversion subroutine uses \(2n+6\log_2n+19\) qubits and \(229n^2+O(n\log n)\) Toffolis. (PDF pp. 1–5.)

**Warning.** This is an extreme space point, not a competitive Toffoli point.

### KB-LSE-02 — Register sharing by length and location metadata

**Direct evidence.** Variable-length Euclidean quantities are packed into two approximately \(n\)-qubit work registers. Small metadata records each logical value's length and location, allowing inactive high bits and mutually exclusive values to share physical storage. (PDF pp. 8–20.)

**Transfer inference.** Benchmark register allocation should be based on mutually exclusive live ranges, not on the sum of nominal widths in pseudocode.

### KB-LSE-03 — Measuring away an obsolete coordinate

**Direct evidence.** An old \(y\)-coordinate is measured in the X basis to release an \(n\)-qubit register. The measurement creates a classical feed-forward phase correction; analogous techniques are used in in-place multiplication/division. (PDF pp. 21–32.)

**Experiment.** Add a phase-obligation ledger to the benchmark scheduler and verify that each measured function can still be recomputed before its correction deadline.

## 4. Chevignard, Fouque, and Schrottenloher, *Reducing the Number of Qubits in Quantum Discrete Logarithms on Elliptic Curves*

Source: [IACR ePrint 2026/280](https://eprint.iacr.org/2026/280) · [local PDF](./papers/04-chevignard-reducing-qubits-ecdlp.pdf)

Retrieval tags: `RNS`, `projective coordinates`, `output compression`, `Legendre symbol`, `spooky pebbling`

### KB-CFS-01 — Output compression instead of preserving an affine point

**Direct evidence.** The construction keeps projective coordinates and extracts a one-bit Legendre-symbol hash such as \(h(P)=(XZ/q)\), avoiding the final affine inversion. Multiple independent executions reconstruct the discrete logarithm from compressed observations. At \(n=256\), one reported configuration uses 1,193 qubits and 22 independent runs, each around \(2^{38.98}\) Toffolis. (PDF pp. 1–6.)

**Warning.** This changes the algorithm's output contract and cannot directly replace a benchmark point-addition map.

### KB-CFS-02 — Residue-number computation and tree pebbling

**Direct evidence.** Projective coordinates are evaluated over many small residue moduli and recombined classically. The design uses measurement-aware pebbling over a computation tree to keep the quantum high-water mark near \(3.12n+o(n)\), at a gate cost described as roughly \(\widetilde O(n^4)\). (PDF pp. 6–31.)

**Transfer inference.** The reusable lesson is to ask whether the benchmark truly needs every intermediate in the canonical prime-field representation; the reported RNS costs themselves are not competitive for the present objective.

## 5. Kim et al., *New Quantum Circuits for ECDLP: Breaking Prime Elliptic Curve Cryptography*

Source: [IACR ePrint 2026/106](https://eprint.iacr.org/2026/106) · [local PDF](./papers/05-kim-new-quantum-circuits-ecdlp.pdf)

Retrieval tags: `carry-save`, `projective`, `affine`, `depth-width`, `zig-zag`

### KB-KIM-01 — Affine versus projective reversible contracts

**Direct evidence.** The affine construction is in place and garbage-free but pays for division. The projective construction avoids division and uses 11 field multiplications, but is out of place and leaves the previous point as garbage. (PDF pp. 3–12.)

**Transfer inference.** Count projective cleanup or prove that the old point can be consumed, ghosted, or reused before declaring the 11-multiplication schedule cheaper.

### KB-KIM-02 — Carry-save and unconditional-round depth reduction

**Direct evidence.** The circuits combine quantum carry-save Montgomery multiplication with a low-depth binary EEA using unconditional rounds, postponed reduction, and copied controls placed into otherwise idle ancillas. The paper reports 58–82% reductions in qubit×T-depth and 43–87% reductions in qubit×full-depth relative to Häner et al., with total gate reductions of 61–93% in its comparisons. (PDF pp. 1–4 and 12–30.)

**Warning.** Qubit×depth and total gate count are different objectives from average Toffolis×peak-live qubits.

### KB-KIM-03 — Zig-zag cleanup for projective garbage

**Direct evidence.** Windowing is combined with a zig-zag arrangement so projective garbage from one direction can be uncomputed while progress is made from the other direction. (PDF pp. 30–38.)

**Experiment.** Model point-additions as a dependency DAG and test whether alternating traversal lowers peak live qubits after including lookup tables and cleanup.

## 6. Häner et al., *Improved Quantum Circuits for Elliptic Curve Discrete Logarithms*

Source: [IACR ePrint 2020/077](https://eprint.iacr.org/2020/077) · [local PDF](./papers/06-haner-improved-quantum-circuits-ecdlp.pdf)

Retrieval tags: `Kaliski inversion`, `Montgomery`, `fixed rounds`, `producer-consumer fusion`, `workspace reuse`

### KB-HAN-01 — Normalizing four Kaliski cases

**Direct evidence.** A swap bit orients the four binary-EEA cases into one shared round body. Controlled swaps choose register roles; then subtraction/addition, halving, and doubling occur only once in the body before the swap is reversed. (PDF pp. 8–9.)

**Transfer inference.** Before optimizing four conditional branches independently, search for a reversible role-normalization that shares their nonlinear core.

### KB-HAN-02 — Fixed rounds and integrated pseudo-inverse correction

**Direct evidence.** The circuit schedules exactly \(2n\) rounds although only \(k\), where \(n\le k\le2n\), modify the EEA state. The initial result is a scaled pseudo-inverse. During reversal, inactive rounds perform the \(2n-k\) modular doublings needed to convert it to the desired Montgomery inverse, while active rounds uncompute EEA state. (PDF p. 8.)

**Transfer inference.** Cleanup slots can perform useful output correction when the same round predicate distinguishes inactive from active history.

### KB-HAN-03 — Consume before reversing

**Direct evidence.** For \(xy+z\), the multiplication's auxiliary state remains live while the product is added into \(z\); only then is the multiplier reversed. Likewise, square-then-subtract avoids copying and recomputing the square. The inversion leaves registers in known states \(0\), \(1\), and \(p\), which are cleared and reused as multiplication workspace before full inverse cleanup. (PDF pp. 7–10.)

**Experiment.** Audit every Bennett-style `compute → copy → uncompute` block for a consumer that can replace the copy layer.

## 7. Roetteler et al., *Quantum Resource Estimates for Computing Elliptic Curve Discrete Logarithms*

Source: [arXiv:1706.06752](https://arxiv.org/abs/1706.06752) · [local PDF](./papers/07-roetteler-quantum-resource-estimates-ecdlp.pdf)

Retrieval tags: `foundational ECDLP`, `affine`, `prime field`, `testable circuit`, `resource baseline`

### KB-RNSL-01 — Explicit affine point-addition baseline

**Direct evidence.** The point-addition circuit uses

\[
9n+2\lceil\log_2n\rceil+10
\]

qubits and approximately

\[
224n^2\log_2n+2045n^2
\]

Toffolis. The full ECDLP estimate is approximately \(448n^3\log_2n+4090n^3\) Toffolis; for a 256-bit prime the paper reports 2,330 qubits and about \(1.26\times10^{11}\) Toffolis. (PDF pp. 1–5 and resource tables.)

### KB-RNSL-02 — Why the old stack remains useful

**Direct evidence.** The paper gives explicit, testable networks for modular addition, multiplication, inversion, and affine point addition. Montgomery arithmetic is selected partly because the inversion workspace already supplies useful ancillas. (PDF pp. 5–24.)

**Transfer inference.** Use this as a semantic and register-interface reference even when replacing every expensive arithmetic component.

## 8. Proos and Zalka, *Shor's Discrete Logarithm Quantum Algorithm for Elliptic Curves*

Source: [arXiv:quant-ph/0301141](https://arxiv.org/abs/quant-ph/0301141) · [local PDF](./papers/08-proos-zalka-shor-ecdlp.pdf)

Retrieval tags: `semiclassical QFT`, `exceptional addition`, `random shift`, `quantum halting`, `register sharing`

### KB-PZ-01 — Reducing exponent-register width and exceptional-case damage

**Direct evidence.** Semiclassical QFT techniques replace large exponent registers with sequential one-qubit processing. A random initial accumulator shift \(kP\) makes exceptional additions rare; failed inversions then act as a bounded permutation/error on amplitudes rather than requiring fully complete formulas. (PDF pp. 1–8.)

**Warning.** The accepted correctness model includes a fidelity loss and is not automatically compatible with exact benchmark validation.

### KB-PZ-02 — Bounded execution of a variable-time EEA

**Direct evidence.** The variable-time Euclidean process is embedded in a fixed number of cycles with a small halting/history register, bounded quotient sizes, and deliberate register sharing. The inversion-space analysis reaches about \(3n+8\sqrt n+4\log_2n+\epsilon\), contributing to a high-level whole-algorithm width near \(6n\). (PDF pp. 20–27.)

**Transfer inference.** The key idea is not the old cost estimate but the separation between a fixed external schedule and data-dependent logical activity.

## 9. Litinski, *How to Compute a 256-bit Elliptic Curve Private Key with Only 50 Million Toffoli Gates*

Source: [arXiv:2306.08585](https://arxiv.org/abs/2306.08585) · [local PDF](./papers/09-litinski-50-million-toffoli-ecc.pdf)

Retrieval tags: `global optimization`, `batch inversion`, `windowing`, `parallel instances`, `active volume`

### KB-L50-01 — Global resource law

**Direct evidence.** For \(k\) parallel instances, the paper gives a per-key Toffoli estimate

\[
(44+65/k)\text{ million}
\]

and active volume

\[
(2.8+3.8/k)\text{ billion blocks}.
\]

One instance therefore costs about 109 million Toffolis under this model. (PDF pp. 1–4.)

### KB-L50-02 — Three global optimizations

**Direct evidence.** The design reuses the first-half state across keys, brute-forces 48 key bits classically, and batches inversions across parallel instances so one inverse plus products replaces many independent inversions. Window size 16 is used, with exact point-addition flags and about 3,000 logical memory qubits per instance. (PDF pp. 3–16.)

**Warning.** Batch inversion is a throughput optimization across instances; it does not lower a single isolated benchmark point-addition cost.

# B. Group-law and field diversity

## 10. Renes, Costello, and Batina, *Complete Addition Formulas for Prime Order Elliptic Curves*

Source: [IACR ePrint 2015/1060](https://eprint.iacr.org/2015/1060) · [local PDF](./papers/10-renes-complete-addition-formulas.pdf)

Retrieval tags: `complete formulas`, `short Weierstrass`, `projective`, `exception-free`

### KB-RCB-01 — Branch-free complete formulas

**Direct evidence.** The generic complete short-Weierstrass addition schedule uses 12 field multiplications plus fixed-constant multiplications and additions. For \(a=0\), relevant to secp256k1, Algorithm 7 is counted as \(12M+2m_{3b}+19a\); mixed addition uses \(11M+2m_{3b}+13a\), and doubling uses \(6M+2S+m_{3b}+9a\). (PDF pp. 2–10.)

### KB-RCB-02 — Reversible import test

**Transfer inference.** Complete formulas remove exceptional-case branches and their flags, but field-operation counts alone do not determine reversible cost. A valid comparison must schedule all temporaries, decide which products are in place, include projective-to-affine conversion, and uncompute old coordinates.

**Experiment.** Compile the \(a=0\) schedule to the benchmark primitive library and compare peak live qubits against affine inversion, not merely multiplication count.

## 11. Hisil et al., *Twisted Edwards Curves Revisited*

Source: [IACR ePrint 2008/522](https://eprint.iacr.org/2008/522) · [local PDF](./papers/11-hisil-twisted-edwards-curves-revisited.pdf)

Retrieval tags: `twisted Edwards`, `extended coordinates`, `unified addition`, `complete formulas`

### KB-HWCD-01 — Extended-coordinate schedules

**Direct evidence.** Extended twisted-Edwards coordinates retain \(T=XY/Z\), allowing the same unified formula to handle addition and doubling under the paper's parameter conditions. Reported schedules include \(9M+2D\), \(8M+2D\) for mixed addition, and specialized \(a=-1\) forms around \(8M+1D\) or \(7M\) mixed. (PDF pp. 1–8.)

### KB-HWCD-02 — What transfers and what does not

**Transfer inference.** The reusable content is schedule structure: symmetric formulas, precomputed coordinate products, and parallel multiplication opportunities. The numerical operation counts do not directly transfer to secp256k1 because the curve model, completeness conditions, extra coordinate, and conversion map differ.

## 12. Sarkar and Seo, *New Quantum Cryptanalysis of Binary Elliptic Curves*

Source: [IACR ePrint 2025/017](https://eprint.iacr.org/2025/017) · [local PDF](./papers/12-sarkar-seo-binary-elliptic-curves.pdf)

Retrieval tags: `binary elliptic curves`, `GF(2^n)`, `carryless`, `Itoh-Tsujii`, `in-place`

### KB-SAS-01 — Binary-field architectural alternatives

**Direct evidence.** The paper presents in-place and out-of-place point-addition layouts over binary extension fields, reporting 73–81% improvements in qubit×depth for in-place designs and over 92% for out-of-place designs in its comparisons. Addition and shifts are CNOT/index operations, squaring is a linear map, and inversion uses Fermat/Itoh–Tsujii structure. (PDF pp. 1–12.)

### KB-SAS-02 — Domain boundary

**Warning.** Prime-field addition has carry propagation, integer comparison, and conditional reduction; none appears in the same form over \(\mathrm{GF}(2^n)\). Transfer only the architecture patterns—linear-map banks, copied controls, and forward/reverse inversion layout—not the quoted costs.

# C. Addition and comparison families

## 13. Cuccaro et al., *A New Quantum Ripple-Carry Addition Circuit*

Source: [arXiv:quant-ph/0410184](https://arxiv.org/abs/quant-ph/0410184) · [local PDF](./papers/13-cuccaro-ripple-carry-adder.pdf)

Retrieval tags: `MAJ`, `UMA`, `ripple carry`, `one ancilla`, `comparator`

### KB-CDKM-01 — Exact low-width addition costs

**Direct evidence.** The MAJ/UMA full adder uses one ancilla, \(2n-1\) Toffolis, \(5n-3\) CNOTs, \(2n-4\) NOTs, and depth \(2n+4\). Addition modulo \(2^n\) uses \(2n-3\) Toffolis and depth \(2n+2\). (PDF pp. 1–7.)

### KB-CDKM-02 — Comparator by retaining only the carry information

**Direct evidence.** A high-bit/comparison variant uses \(2n-1\) Toffolis, \(4n-3\) CNOTs, and depth \(2n+3\). (PDF pp. 6–7.)

**Transfer inference.** This is a useful exact baseline for judging fused comparators, temporary-AND adders, and approximate leading-bit comparators.

## 14. Draper et al., *A Logarithmic-Depth Quantum Carry-Lookahead Adder*

Source: [arXiv:quant-ph/0406142](https://arxiv.org/abs/quant-ph/0406142) · [local PDF](./papers/14-draper-carry-lookahead-adder.pdf)

Retrieval tags: `QCLA`, `generate propagate`, `prefix`, `log depth`, `comparator`

### KB-DKRS-01 — Prefix-carry depth point

**Direct evidence.** Carry status is represented through generate/propagate signals and combined in a tree. The out-of-place adder has depth \(2\log_2n+O(1)\) with about \(n\) ancillas; the in-place form has depth \(4\log_2n+O(1)\) with about \(2n\) ancillas. Comparator and modulo-\(2^n\) variants are also derived. (PDF pp. 1–8 and 19.)

### KB-DKRS-02 — Benchmark-specific tradeoff

**Transfer inference.** QCLA should be tested only where reduced depth exposes enough qubit reuse or parallelism to compensate for its width. Under a Toffoli×peak-live objective, logarithmic depth alone is not a win.

## 15. Draper, *Addition on a Quantum Computer*

Source: [arXiv:quant-ph/0008033](https://arxiv.org/abs/quant-ph/0008033) · [local PDF](./papers/15-draper-addition-quantum-computer.pdf)

Retrieval tags: `Fourier addition`, `phase rotations`, `classical constant`, `AQFT`

### KB-DRA-01 — Addition without a carry register

**Direct evidence.** The target is Fourier transformed, phases corresponding to the addend are applied, and the inverse QFT returns the binary sum. A known classical constant can be added without a quantum addend register, and the phase rotations commute, offering substantial parallelism. (PDF pp. 1–6.)

### KB-DRA-02 — Cost-model incompatibility

**Direct evidence.** Approximate QFT drops small rotations and reduces operation count to roughly \(O(n\log n)\), with logarithmic-depth organizations discussed. (PDF pp. 5–8.)

**Warning.** Rotation synthesis precision, accumulated approximation, and entry/exit from Fourier basis must be translated into the benchmark's nonlinear-gate model before comparison with Toffoli adders.

## 16. Gidney, *Halving the Cost of Quantum Addition*

Source: [arXiv:1709.06648](https://arxiv.org/abs/1709.06648) · [local PDF](./papers/16-gidney-halving-cost-addition.pdf)

Retrieval tags: `temporary logical AND`, `measurement uncompute`, `4T adder`, `phase insensitive`

### KB-GHA-01 — Temporary logical AND

**Direct evidence.** A logical AND is computed with 4 T gates and erased with no T gates using measurement and classically controlled fixup. Substituting this gadget into a ripple adder gives \(4n-4\) T gates, measurement depth \(2n-2\), and \(n\) work ancillas. (PDF pp. 1–3.)

### KB-GHA-02 — Conditions on the consumer

**Direct evidence.** A controlled adder is estimated near \(8n+O(1)\) T gates, while reversing an out-of-place addition can be T-free in the intended use. The savings rely on measuring temporary values only after their consumers are insensitive to the corresponding phase information. (PDF pp. 2–6.)

**Transfer inference.** Treat the gadget as a compute/use/measure contract, not as a generic Toffoli replacement.

## 17. Gidney, *A Classical-Quantum Adder with Constant Workspace and Linear Gates*

Source: [arXiv:2507.23079v1](https://arxiv.org/abs/2507.23079v1) · [local PDF](./papers/17-gidney-classical-quantum-adder.pdf)

Retrieval tags: `constant addition`, `constant workspace`, `dirty ancilla`, `carry venting`, `free control`

### KB-GCA-01 — Principal workspace/Toffoli tradeoffs

**Direct evidence.**

| Clean ancillas | Dirty ancillas | Toffoli cost |
|---:|---:|---:|
| 3 | 0 | \(4n\pm O(1)\) |
| 2 | \(n-2\) | \(3n\pm O(1)\) |

The constant-workspace construction splits the target into two halves and lets each half borrow the other as dirty workspace at different stages. (PDF pp. 1, 3, and 7.)

### KB-GCA-02 — Carry venting identity

**Direct evidence.** With \(x'=x+d+c_0\) and

\[
\operatorname{carry}(x,d,c_0)=x\oplus d\oplus(x+d+c_0),
\]

the paper uses

\[
\operatorname{carry}(\sim x',d,c_0)=\operatorname{carry}(x,d,c_0).
\]

The carry can therefore be recomputed from post-addition values. X-basis measurement releases the carry qubit while a minus outcome leaves a known phase-correction task. (PDF p. 3.)

### KB-GCA-03 — Outer control without extra Toffolis

**Direct evidence.** To control addition of a classical offset, each hardwired offset bit 0 remains 0 and each hardwired 1 is replaced by the external control. Because these bits only invert controls or trigger bit flips, the substitution adds no Toffolis or workspace under the paper's construction. (PDF p. 7.)

**Experiment.** Test this directly for secp256k1 constants \(p\), \(2^{32}+977\), and formula coefficients.

## 18. Baksi, Chattopadhyay, and Seo, *Tree-based Quantum Carry-Save Adder*

Source: [IACR ePrint 2025/626](https://eprint.iacr.org/2025/626) · [local PDF](./papers/18-baksi-tree-based-carry-save-adder.pdf)

Retrieval tags: `QCSA`, `Wallace tree`, `Dadda tree`, `multioperand addition`, `multiplier`

### KB-BCS-01 — Quantum full-adder node and tree choices

**Direct evidence.** The paper's quantum full-adder node uses one Toffoli and five CNOTs. Wallace trees reduce operand columns aggressively for lower depth; Dadda trees postpone reductions to lower count and width at greater depth. (PDF pp. 1–10.)

### KB-BCS-02 — Reported depth-width improvements and cleanup

**Direct evidence.** The evaluated carry-save adders report more than 82% and in some cases up to 99% improvement in qubit×depth, while integrated multiplier comparisons report improvements up to 87%. Ancilla outputs feed the final carry-propagate adder and are then reversed for cleanup and reuse. (PDF pp. 1–4 and 12–24.)

**Transfer inference.** This is most promising where point-addition formulas expose three or more simultaneously available summands or many partial products. It is unlikely to help an isolated two-input addition enough to offset width.

# D. Windowing, approximation, and modular building blocks

## 19. Gidney, *Windowed Quantum Arithmetic*

Source: [arXiv:1905.07682](https://arxiv.org/abs/1905.07682) · [local PDF](./papers/19-gidney-windowed-quantum-arithmetic.pdf)

Retrieval tags: `windowing`, `QROM`, `classical constant`, `product addition`, `nested windows`

### KB-WIN-01 — Replace per-bit controls with chunk lookups

**Direct evidence.** A quantum-addressed lookup of \(L\) classical entries can be implemented with \(L-1\) Toffolis independently of output width, and measurement-based unlookup can reduce cleanup to roughly \(2\sqrt L\) Toffolis. Processing \(w\) control bits at a time trades a \(2^w\)-entry table against fewer additions. (PDF pp. 2–4.)

### KB-WIN-02 — Classical-factor product addition

**Direct evidence.** For \(x\mathrel{+}=ky\) with classical \(k\), windowing gives cost

\[
O\!\left(\frac{n}{w}(n+2^w)\right).
\]

Choosing \(w\approx\log_2n\) gives \(O(n^2/\log n)\). Similar nesting is applied to modular product addition and exponentiation. (PDF pp. 5–11.)

**Warning.** The paper does not know how to obtain the same advantage for \(x\mathrel{+}=ab\) when all three registers are quantum. Use it for constants, table-selected points, and fixed-modulus operations.

## 20. Gidney, *Approximate Encoded Permutations and Piecewise Quantum Adders*

Source: [arXiv:1905.08488](https://arxiv.org/abs/1905.08488) · [local PDF](./papers/20-gidney-approximate-encoded-permutations.pdf)

Retrieval tags: `approximation`, `coset representation`, `carry runway`, `trace distance`, `piecewise addition`

### KB-AEP-01 — Error calculus

**Direct evidence.** If an approximate encoded permutation has deviation \(\epsilon\), the resulting trace distance from the ideal operation is at most \(2\sqrt\epsilon\). Deviation is subadditive under composition and concatenation. (PDF pp. 1–7.)

### KB-AEP-02 — Cosets and oblivious carry runways

**Direct evidence.** Modular addition in a coset representation with \(m\) padding bits has deviation at most \(2^{-m}\). One oblivious carry runway of length \(m\) also contributes at most \(2^{-m}\); a modular addition with \(r\) runways has deviation at most \((r+1)2^{-m}\). (PDF pp. 8–12.)

### KB-AEP-03 — Whole-circuit error budget

**Direct evidence.** For \(k\) additions and \(r\) runways, the series deviation is bounded by approximately \(kr2^{-m}\), or \(k(r+1)2^{-m}\) with the coset endpoint. Piecewise carry-lookahead addition can reach \(O(\log\log n)\) asymptotic depth. (PDF pp. 12–16.)

**Warning.** The benchmark must accept approximation, and representation conversion plus aggregate error—not the error of one addition—must be validated.

## 21. Häner, Roetteler, and Svore, *Factoring Using \(2n+2\) Qubits with Toffoli Based Modular Multiplication*

Source: [arXiv:1611.07995](https://arxiv.org/abs/1611.07995) · [local PDF](./papers/21-haner-factoring-2n-plus-2-qubits.pdf)

Retrieval tags: `low width`, `dirty ancilla`, `constant adder`, `modular multiplication`, `divide and conquer`

### KB-HRS-01 — Constant addition using borrowed workspace

**Direct evidence.** The paper gives a Toffoli-based classical-constant adder with \(O(n\log n)\) gates and \(O(n)\) depth using one dirty ancilla; additional dirty ancillas reduce constants and expose parallelism. A divide-and-conquer construction lets opposite halves of a register borrow one another. (PDF pp. 1–7.)

### KB-HRS-02 — Compact controlled modular multiplication

**Direct evidence.** Comparison, conditional add/subtract, and a compute/swap/inverse-multiply pattern are assembled into a controlled modular multiplier while keeping the full factoring architecture to \(2n+2\) qubits. Idle multiplier registers supply dirty workspace during modular addition. (PDF pp. 7–12.)

**Transfer inference.** The key portable rule is that dirty workspace availability is phase-specific. Build a time-indexed borrowing map instead of assigning each arithmetic routine a fixed ancilla count.

## 22. Luongo et al., *Measurement-Based Uncomputation of Quantum Circuits for Modular Arithmetic*

Source: [arXiv:2407.20167v1](https://arxiv.org/abs/2407.20167v1) · [local PDF](./papers/22-luongo-measurement-uncomputation-modular-arithmetic.pdf)

Retrieval tags: `MBU lemma`, `modular addition`, `predicate cleanup`, `expected Toffoli`, `external control`

### KB-MBU-01 — One-bit MBU branches

**Direct evidence.** Starting from \(\sum_x\alpha_x|x\rangle|g(x)\rangle\), apply a Hadamard and measure the one-bit garbage. Outcome 0, with probability \(1/2\), clears it immediately. Outcome 1 leaves phase \((-1)^{g(x)}\) and invokes a repair based on the self-adjoint XOR oracle

\[
U_g|x\rangle|b\rangle=|x\rangle|b\oplus g(x)\rangle.
\]

Only the repair branch pays the oracle cost. (PDF p. 35.)

### KB-MBU-02 — Modular-adder costs

**Direct evidence.**

| Construction | Expected Toffoli cost | Ancillas |
|---|---:|---:|
| Gidney modular adder | \(3.5n\) | \(2n+3\) |
| Gidney controlled modular adder | \(4.5n+0.5\) | \(2n+3\) |

The half-cost term is the final comparator used to erase the reduction flag. (PDF pp. 36 and 38–39.)

### KB-MBU-03 — Do not over-control modular arithmetic

**Direct evidence.** In the controlled modular adder, the caller's external control is needed on the first addition and the final cleanup comparison. The middle comparison is unconditional, and subtraction by the modulus is controlled by the internal reduction predicate. (PDF p. 28.)

**Experiment.** Distinguish caller controls from internally generated predicates in every benchmark helper.

# E. Multiplication, reduction, inversion, division, and EEA restructuring

## 23. Rines and Chuang, *High Performance Quantum Modular Multipliers*

Source: [arXiv:1801.01081](https://arxiv.org/abs/1801.01081) · [local PDF](./papers/23-rines-chuang-modular-multipliers.pdf)

Retrieval tags: `division multiplier`, `Montgomery`, `Barrett`, `exact reduction`, `in-place`

### KB-RCH-01 — Comparable multiplier families

**Direct evidence.** The paper constructs exact division-based, Montgomery, and Barrett modular multipliers in several adder models. Leading-order ripple implementations use about \(3n\) qubits, \(4n^2\) Toffolis, and \(4n^2\) depth; prefix versions use about \(5n\) qubits, \(20n^2\) gates, and \(8n\log_2n\) depth. Fourier variants approach \(2n+O(\log n)\) qubits but use synthesized rotations. (PDF pp. 3–5 and tables.)

### KB-RCH-02 — Reduce once instead of after every partial product

**Direct evidence.** The division-style architecture forms a nonmodular product and then reduces it, with only logarithmic-width quotient/reduction metadata. Montgomery and Barrett variants replace trial division with modulus-specific estimation and correction. An in-place quantum-quantum multiplier is composed from forward and reverse out-of-place multipliers plus swaps. (PDF pp. 5–29.)

**Warning.** Many formulas are leading-order and depend strongly on the chosen adder and whether the multiplicative inverse needed for in-place conversion is available.

## 24. Gidney, *Asymptotically Efficient Quantum Karatsuba Multiplication*

Source: [arXiv:1904.07356](https://arxiv.org/abs/1904.07356) · [local PDF](./papers/24-gidney-quantum-karatsuba.pdf)

Retrieval tags: `Karatsuba`, `inline output`, `linear space`, `recomputation`, `crossover`

### KB-KAR-01 — Inline recursive products

**Direct evidence.** Recursive subproducts are accumulated directly into slices of the final target instead of being stored as separate intermediates and later uncomputed. Padded words absorb carries. This yields \(O(n)\) space and \(O(n^{\log_2 3})\) arithmetic operations. (PDF pp. 1–8.)

### KB-KAR-02 — Practical crossover

**Direct evidence.** The paper's estimates place the practical crossover with optimized schoolbook methods near 10,000 bits, far above 256-bit field operands. (PDF pp. 8–14.)

**Transfer inference.** Do not import Karatsuba recursion for secp256k1 on asymptotics alone. Import its scheduling principle—write producer outputs directly into their consumer destination.

## 25. Lee et al., *Efficient Quantum Modular Reduction: Crandall Reduction and Its Fault-Tolerant Resource Analysis*

Source: [arXiv:2608.11563v1](https://arxiv.org/abs/2608.11563v1) · [local PDF](./papers/25-lee-crandall-reduction.pdf)

Retrieval tags: `Crandall reduction`, `pseudo-Mersenne`, `two folds`, `constant arithmetic`, `secp256k1`

### KB-CRA-01 — Fixed two-fold reduction

**Direct evidence.** For \(q=2^n-c\) and a \(2n\)-bit input \(a=a_1 2^n+a_0\), one fold gives \(ca_1+a_0\). Two folds bound the result by

\[
a^{(2)}\le 2^n-1+c^2.
\]

A third fold does not reduce the required normalization count under the stated conditions, so the circuit fixes the fold count at two. (PDF pp. 2–4.)

### KB-CRA-02 — Normalization conditions and secp256k1 fit

**Direct evidence.** One conditional subtraction suffices when

\[
c^2+2c\le 2^n,
\]

approximately \(c\lesssim2^{n/2}\). Two normalization steps extend the sufficient range to \(c^2+3c<2^{n+1}+1\). (PDF p. 4.)

**Transfer inference.** secp256k1 has

\[
p=2^{256}-(2^{32}+977).
\]

Here \(c=2^{32}+977\) has bit length 33 and Hamming weight 7, and it easily satisfies the one-normalization condition. The paper's worst-case constant-multiplier bounds should therefore be pessimistic for this modulus.

### KB-CRA-03 — Resource formulas and cleanup boundary

**Direct evidence.** Define

\[
M(n)=\left\lceil\frac{n+1}{2}\right\rceil,\qquad
F(n)=\left\lfloor\frac{n^2}{4}\right\rfloor+(n-1)\left\lfloor\frac n2\right\rfloor.
\]

Crandall-1 is bounded by \(4n+4M(n)+1\) qubits, \(4F(n)+20n+4\) T gates, and \(F(n)+5n+1\) T-depth. Crandall-2 adds another normalization block. The forward circuit retains input-dependent ancillary state until reversed and uses temporary logical-AND measurement cleanup. (PDF pp. 5–8.)

**Experiment.** Implement a secp-specific version whose constant multiplier is synthesized from the seven set bits of \(c\), then compare copy-and-reverse against direct consumption by the next point-formula step.

## 26. Bernstein and Yang, *Fast Constant-Time GCD Computation and Modular Inversion*

Source: [IACR ePrint 2019/266](https://eprint.iacr.org/2019/266) · [local PDF](./papers/26-bernstein-yang-fast-constant-time-gcd-inversion.pdf)

Retrieval tags: `divstep`, `constant time`, `modular inversion`, `transition matrix`, `bottom bits`

### KB-BY-01 — A regular two-case divstep

**Direct evidence.** For odd \(f\), the integer divstep is

\[
\operatorname{divstep}(\delta,f,g)=
\begin{cases}
(1-\delta,\ g,\ (g-f)/2), & \delta>0\ \text{and}\ g\ \text{odd},\\
(1+\delta,\ f,\ (g+(g\bmod2)f)/2), & \text{otherwise}.
\end{cases}
\]

It decomposes into a conditional swap/negation followed by one elimination. Decisions depend on \(\delta\) and low bits, not a full-width magnitude comparison. (PDF pp. 21–22.)

### KB-BY-02 — Fixed iteration bound and scaled reciprocal

**Direct evidence.** For \(d\)-bit-size inputs, the paper chooses

\[
m=
\begin{cases}
\lfloor(49d+80)/17\rfloor,&d<46,\\
\lfloor(49d+57)/17\rfloor,&d\ge46,
\end{cases}
\]

which guarantees \(g_m=0\) and \(f_m=\pm\gcd(f,g)\). The reciprocal is extracted from the transition matrix with a known power-of-two scale that is corrected using a precomputed modular factor. Asymptotically about \(2.8821n\) divsteps suffice under the proved bound. (PDF pp. 22 and 26–27.)

### KB-BY-03 — Transfer boundary

**Warning.** This is a classical constant-time algorithm and supplies no reversible qubit/Toffoli schedule. Reversible import must preserve the transition history or reconstruct it, bound intermediate signed widths, and uncompute every conditional decision.

**Experiment.** Compare a reversible divstep transcript against Kaliski/Dialog on step count, decision width, transcript bits, and replay cost.

## 27. Mukhopadhyay, Gheorghiu, and Krovi, *Improved Quantum Circuits for Division*

Source: [arXiv:2603.18110v2](https://arxiv.org/abs/2603.18110v2) · [local PDF](./papers/27-mukhopadhyay-improved-division.pdf)

Retrieval tags: `COMP-N-SUB`, `division`, `fused predicate`, `in-place quotient`, `Stein GCD`

### KB-DIV-01 — Compare and conditionally subtract as one primitive

**Direct evidence.** The unitary maps

\[
|a\rangle|b\rangle|0\rangle\longmapsto
\begin{cases}
|a\rangle|b-a\rangle|0\rangle,&b\ge a,\\
|a\rangle|b\rangle|1\rangle,&b<a.
\end{cases}
\]

It computes the high/sign bit first and uses the remainder of the adder either to finish the subtraction or restore the inputs, avoiding a separate comparison followed by a controlled adder. (PDF pp. 3 and 8–11.)

### KB-DIV-02 — Exact COMP-N-SUB operating points

**Direct evidence.**

| Variant | Toffolis | T count | Total qubits | T depth | Fully reversible |
|---|---:|---:|---:|---:|---|
| I, ripple | \(3k-1\) | \(18k-4\) | \(2k+1\) | \(9k-3\) | yes |
| IIb, lookahead | \(11k-6\omega(k)-6\lfloor\log_2k\rfloor-4\) | \(77k-42\omega(k)-42\lfloor\log_2k\rfloor-21\) | \(5k-\omega(k)-\lfloor\log_2k\rfloor-1\) | \(O(\log k)\) | yes |
| III, temporary AND | \(k\) | \(11k\) | \(3k\) | \(5k\) | no; uses \(k\) measurements |

(PDF pp. 12–19.)

### KB-DIV-03 — Divider-level space reuse

**Direct evidence.** The quotient is written into high dividend bits as those bits become zero, divisors are not padded unnecessarily, and initial overlap can reduce iteration count. Leading T counts fall from \(O(n^2)\) to \(O(nm)\) when the divisor width is \(m\); Type-I long division approaches the storage lower bound with roughly \(n+m+3\) qubits. (PDF pp. 2–6.)

**Transfer inference.** EEA quotient steps and modular normalization should be searched for adjacent “compare then controlled subtract” pairs that can be fused.

## 28. Khattar et al., *Verifiable Quantum Advantage via Optimized DQI Circuits*

Source: [arXiv:2510.10967v1](https://arxiv.org/abs/2510.10967v1) · [local PDF](./papers/28-khattar-optimized-dqi-circuits.pdf)

Retrieval tags: `reversible EEA`, `Bézout`, `Dialog`, `implicit access`, `direct division`

### KB-DIA-01 — Explicit versus implicit Bézout access

**Direct evidence.** With EEA steps represented by transition matrices \(\tau_i\), explicit access materializes the full product \(\tau_m\cdots\tau_1\) and its Bézout coefficients. Implicit access stores the ordered small transitions and rewrites consumers to replay them. Both approaches target leading-order \(2nb+O(\log_2n)\) space in the paper's polynomial setting. (PDF pp. 8–13.)

### KB-DIA-02 — Direct division by replay

**Direct evidence.** If the EEA transition product maps \((P,B)\) to the gcd state, applying that same product to

\[
\begin{bmatrix}0\\A\end{bmatrix}
\]

produces

\[
\begin{bmatrix}AB^{-1}\\0\end{bmatrix}\pmod P.
\]

The quotient is obtained without ever materializing \(B^{-1}\). The paper gives a leading cost of \(4n^2\) underlying field multiplications for this implicit route versus \(7n^2\) for explicit invert-then-multiply. (PDF p. 9.)

### KB-DIA-03 — Dialog representation and domain warning

**Direct evidence.** The Dialog is the EEA execution trace: update coefficients and conditional swaps encoding the ordered transition sequence. For degree-\((n-1)\) polynomial inputs it contains \(2n\) field elements. (PDF pp. 10–13.)

**Warning.** The numerical costs use polynomial arithmetic over \(\mathrm{GF}(2^b)\), where addition and many fixed linear maps are CNOT-only. Only the transition-trace architecture transfers directly to prime-field inversion.

## 29. Litinski, *Quantum Schoolbook Multiplication with Fewer Toffoli Gates*

Source: [arXiv:2410.00899v1](https://arxiv.org/abs/2410.00899v1) · [local PDF](./papers/29-litinski-optimal-modular-multiplication.pdf)

Retrieval tags: `schoolbook multiplication`, `controlled add-subtract`, `Montgomery`, `Toffoli count`

### KB-LIT-01 — Replace shifted controlled adds

**Direct evidence.** A controlled add-subtract adds \(2^ky\) when control \(x_k=1\) and subtracts it when \(x_k=0\). It costs the same as an uncontrolled adder: \(n\) Toffolis with carry-out or \(n-1\) without. (PDF pp. 1–2.)

### KB-LIT-02 — Exact correction and multiplier cost

**Direct evidence.** The \(n\) add-subtract steps produce

\[
2xy+2^{2n}-2^n(x+1+y)+y.
\]

After three global corrections and division by two via wire relabeling, the nonmodular multiplier costs

\[
n^2+4n+3
\]

Toffolis instead of \(2n^2+n\). The modulo-\(2^n\) variant costs \(0.5n^2+1.5n\). (PDF pp. 1–3.)

### KB-LIT-03 — Prime-field interface

**Direct evidence.** The prime-modulus construction is an out-of-place Montgomery multiplier whose steps emit garbage. Its reported Toffoli count is

\[
n^2+6n+\frac nw\left(2^w+3\cdot2^{w/2}+3n-3\right).
\]

Full cleanup may require copying the result and reversing the multiplier. Replacing standard multipliers in a cited 256-bit ECDLP design changes its asymptotic per-key term from 44M to 30M Toffolis, with smaller gains at moderate batching. (PDF pp. 2–5.)

**Warning.** Include Montgomery conversion, separate output, garbage, and reversal when importing it into a canonical in-place API.

# F. Measurement-aware scheduling and ancilla reuse

## 30. Kornerup, Sadun, and Soloveichik, *Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements*

Source: [arXiv:2110.08973v3](https://arxiv.org/abs/2110.08973v3) · [local PDF](./papers/30-kornerup-spooky-pebble-game.pdf)

Retrieval tags: `spooky pebbling`, `ghosting`, `phase record`, `time-qubit tradeoff`, `DAG`

### KB-KSS-01 — Ghosting map and precondition

**Direct evidence.** Ghosting performs

\[
\sum_i\alpha_i|x_i\rangle|y_i\rangle
\longmapsto
\sum_i\alpha_i(-1)^{b\cdot y_i}|x_i\rangle|0\rangle
\]

while returning classical measurement string \(b\). The labels \(x_i\) must be pairwise distinct so basis components do not collapse onto one another. (PDF pp. 4–5.)

### KB-KSS-02 — Tight line tradeoff

**Direct evidence.** If

\[
n\le\binom{m+s-2}{s-2}+1,
\]

a line of length \(n\) can be spooky-pebbled with at most \(s\) pebbles and \(O(mn)\) steps. Related unghosting uses \(n\le\binom{m+s-1}{s-1}\). The paper derives tight time-qubit tradeoffs for sequential computation. (PDF pp. 3 and 9–12.)

### KB-KSS-03 — Memory is moved, not destroyed

**Direct evidence.** The measured string remains live in classical memory until the original value is recomputed and its phase is removed. Spooky pebbling lowers quantum memory but not total classical-plus-quantum memory. (PDF pp. 2 and 5–6.)

**Experiment.** Model a measured register as a reusable qubit allocation plus an unresolved classical phase ticket with explicit dependencies and deadline.

## 31. Paradis, Bichsel, and Vechev, *Reqomp: Space-Constrained Uncomputation for Quantum Circuits*

Source: [arXiv:2212.10395v2](https://arxiv.org/abs/2212.10395v2) · [local PDF](./papers/31-paradis-reqomp.pdf)

Retrieval tags: `automatic uncomputation`, `space constraint`, `well-valued graph`, `recomputation`, `compiler`

### KB-REQ-01 — Input/output contract

**Direct evidence.** Reqomp takes a circuit lacking cleanup, its ancilla variables, and a maximum number of physical ancilla qubits. If it succeeds, it returns a circuit that preserves non-ancilla outputs, resets all ancillas, and respects the space constraint. Well-valued circuit graphs track each qubit's value index, and `evolveVertex` introduces only safe compute or uncompute steps. (PDF pp. 1–6.)

### KB-REQ-02 — Strategy synthesis

**Direct evidence.** Reqomp extracts an ancilla-dependency graph, partitions independent components, derives compute/uncompute/recompute schedules for linear components, and rebuilds the circuit while reusing freed qubits. For non-linear components it falls back to a lazy heuristic; finding a general optimum is PSPACE-complete. (PDF pp. 6–10.)

### KB-REQ-03 — Evaluation and boundary

**Direct evidence.** The evaluation reports up to 96% fewer ancilla qubits than Unqomp. Sixteen of twenty benchmarks achieve at least a 25% ancilla reduction with gate increase no greater than 28%. The synthesis is centered on qfree gates such as X, CNOT, and Toffoli; non-qfree dependencies restrict applicability. (PDF pp. 1–3 and 14–20.)

**Experiment.** Export the benchmark's arithmetic dependency graph and use a Reqomp-like scheduler as an independent audit of hand-written cleanup, even if the exact tool cannot ingest the implementation.

## 32. Liu, Zhou, and Meng, *Quantum Uncomputation of Clean and Dirty Ancilla Qubits*

Source: [arXiv:2608.09578v1](https://arxiv.org/abs/2608.09578v1) · [local PDF](./papers/32-liu-uncomputation-clean-dirty-ancillas.pdf)

Retrieval tags: `dirty ancilla`, `clean ancilla`, `RwUn`, `normal form`, `toggle detection`, `coNP-hard`

### KB-LZM-01 — Unified safety contract

**Direct evidence.** A clean ancilla must return to \(|0\rangle\). A dirty ancilla beginning in arbitrary unknown state \(|x\rangle\) must return to the same \(|x\rangle\), with the circuit's functionality on working qubits independent of \(x\). The paper proves that deciding whether uncomputation exists is coNP-hard, already for reversible Boolean circuits. (PDF pp. 1–5.)

### KB-LZM-02 — Two-stage synthesis pipeline

**Direct evidence.** A syntax-directed system recognizes disciplined clean-ancilla use and dirty-ancilla toggle-detection patterns. When that fails, `RwUn` repeatedly rewrites the circuit into a prefix/suffix normal form that pushes ancilla-modifying operations to the tail, after which regular synthesis removes or reverses them. (PDF pp. 3 and 10–23.)

### KB-LZM-03 — Applicability and failure modes

**Direct evidence.** `RwUn` succeeds on all 17 practical complex-dependency benchmarks in the paper versus 10/17 for Reqomp, roughly doubles coverage on random reversible circuits, and handles about half of tested random quantum circuits outside Reqomp's scope. It is incomplete: ancilla/working-qubit dependency cycles can block qfree normalization, Hadamards on ancillas are excluded, and some rewrite rules can cause large intermediate growth. (PDF pp. 3–4 and 20–28.)

**Transfer inference.** Every claimed use of borrowed benchmark registers should satisfy the dirty-ancilla contract explicitly; “the register is idle” is necessary but not sufficient.

# Cross-paper synthesis

## 1. Representation and point-formula choices

| Choice | Supporting papers | Potential gain | Required accounting |
|---|---|---|---|
| Affine, canonical residues | 2, 7 | Direct benchmark fit and simpler external API | Inversion and exceptional cases |
| Affine, Montgomery residues | 6, 23, 29 | Efficient repeated multiplication | Entry/exit conversion and scaled inverse |
| Complete projective formulas | 5, 10 | Remove exceptional branches and inversion | Old-point garbage, extra coordinates, final affine conversion |
| RNS/projective compressed output | 4 | Extreme quantum-width reduction | Changed output contract and repeated runs |
| Twisted Edwards or binary-field schedules | 11, 12 | New schedules and parallelism ideas | Curve/field conversion; numerical costs are nonportable |

**Rule.** A formula family wins only after representation conversion, garbage cleanup, and peak-live timing are included.

## 2. Addition and comparison decision tree

1. For a generic low-width exact adder, use Cuccaro as the baseline.
2. For a known classical constant, test Gidney's constant-workspace adder and windowing.
3. For a comparison immediately followed by conditional subtraction, test COMP-N-SUB before composing two black boxes.
4. For depth-sensitive multioperand sums, test QCLA or carry-save trees, but charge their full live width.
5. For a predicate used only for cleanup, test MBU before coherent reversal.
6. For an approximate design, derive the whole-circuit trace-distance budget before selecting truncated comparisons, runways, or AQFT.

## 3. Multiplication and reduction frontier

| Mechanism | Best-fit regime | Main papers | ECDSA Fail question |
|---|---|---|---|
| Controlled add-subtract schoolbook | Two quantum 256-bit factors | 29 | Does halving the schoolbook leading term survive cleanup? |
| Windowed product-add | One classical factor/table entry | 19 | Which secp constants and lookup-selected coordinates qualify? |
| Crandall reduction | \(p=2^{256}-(2^{32}+977)\) | 25 | Can seven-bit constant folding beat current modular reduction? |
| Montgomery/Barrett/division reduction | Repeated general products | 23 | Which representation minimizes conversion plus reduction? |
| Carry-save trees | Many partial products/summands | 18 | Does lower depth free enough live registers to offset width? |
| Karatsuba | Very large operands | 24 | At 256 bits, use only scheduling ideas unless measurements disprove the reported crossover |

## 4. Inversion architecture

The papers expose four separable layers:

1. **State evolution:** Kaliski/binary EEA (6), fixed divsteps (26), or other division-free EEA (28).
2. **Decision transcript:** explicit round bits, compact Dialog transitions, or recomputed low-bit decisions.
3. **Bézout/output reconstruction:** materialized coefficient, replay on a consumer vector, or scaled pseudo-inverse correction.
4. **Cleanup:** reverse active rounds, use inactive rounds for correction, measure obsolete registers, or reschedule with pebbling.

**Rule.** Compare inversion designs using at least:

\[
(\text{round count},\ \text{nonlinear gates/round},\ \text{transcript bits},\ \text{peak live width},\ \text{replay/cleanup cost}).
\]

## 5. Measurement and uncomputation hierarchy

These mechanisms are related but not interchangeable:

- Temporary logical AND erases a specific computed bit with a known measurement gadget (16).
- MBU erases a one-bit Boolean predicate with expected half-oracle repair (22).
- Carry venting releases carry bits whose phase can be reconstructed from post-addition values (17).
- Ghosting releases an arbitrary classical register while retaining a classical phase record (30).
- Reqomp reschedules coherent compute/uncompute/recompute under a clean-ancilla budget (31).
- RwUn checks and synthesizes cleanup for both clean and dirty ancillas using rewrites (32).

**Rule.** Every early release creates one of three obligations: an inverse circuit, a recomputation dependency, or a classical phase ticket. The scheduler must represent it explicitly.

## 6. Benchmark integration rules

### Contract checklist

For each imported primitive, record:

- exact reversible map;
- canonical, Montgomery, projective, coset, compressed, or implicit representation;
- in-place or out-of-place output;
- caller control versus internal predicate controls;
- clean, dirty, conditionally clean, and classical workspace;
- coherent garbage and measured classical records;
- exact, expected, or approximate cost;
- exceptional inputs and range preconditions;
- point at which every borrowed qubit is restored.

### Cost normalization

Do not compare a Toffoli count with a T count or field-multiplication count directly. Translate to one benchmark library and report:

\[
\begin{aligned}
&\text{static Toffolis},\\
&\text{average executed Toffolis},\\
&\text{peak live qubits},\\
&\text{objective product},\\
&\text{measurements and feed-forward depth},\\
&\text{classical records still live},\\
&\text{failure or trace-distance budget}.
\end{aligned}
\]

### Validation ladder

1. Exhaustive reversible truth-table tests at small widths.
2. Random and adversarial tests at intermediate widths.
3. Full 256-bit secp256k1 tests including \(0\), \(1\), \(p-1\), carry boundaries, exceptional point pairs, and noncanonical intermediates.
4. Forward-plus-inverse tests with arbitrary dirty-ancilla initial patterns.
5. Phase-sensitive tests for every measurement-assisted release.
6. Independent gate-count and peak-live instrumentation.

## 7. Highest-value experiments

| Priority | Experiment | Papers | Expected effect | Acceptance condition |
|---:|---|---|---|---|
| 1 | secp-specific two-fold Crandall reduction using \(c=2^{32}+977\) | 17, 25 | Lower reduction Toffolis; sparse constant | Exact canonical result; cleanup included; lower objective product |
| 2 | Replace shifted controlled adders with controlled add-subtracts | 13, 16, 29 | Near-half schoolbook leading term | Full multiplier and inverse pass benchmark tests |
| 3 | Fuse compare plus conditional subtract | 13, 22, 27 | Remove duplicated carry work | Exact map and lower average Toffolis after flag cleanup |
| 4 | Consumer-before-reverse fusion in square/multiply stages | 6, 24, 29 | Avoid copied outputs or second evaluation | Lower peak-live or Toffolis with identical outer API |
| 5 | Constant-adder specialization for \(p\), \(c\), and formula constants | 17, 19, 21 | Lower `const_arith` cost | Include controls, dirties, and phase tickets |
| 6 | Dialog or divstep inversion transcript | 2, 6, 26, 28 | Smaller history and narrower decisions | Better full inversion objective, not only fewer rounds |
| 7 | MBU of reduction/comparison flags | 16, 17, 22, 30 | Expected half-cost cleanup | Repair oracle and feed-forward verified phase-sensitively |
| 8 | Dependency-DAG cleanup audit | 30, 31, 32 | Lower peak live qubits | All clean/dirty ancillas restored; no unresolved tickets |
| 9 | Complete \(a=0\) projective point-add schedule | 5, 10 | Remove exceptional branches/inversion | Conversion and old-point garbage included |
| 10 | Carry-save accumulation of partial products | 5, 18 | Lower depth and possibly earlier release | Objective product improves despite extra width |

## 8. Negative results and guardrails

- Do not treat the Babbush attested circuit as reproducible source code.
- Do not import binary-field or twisted-Edwards operation counts into secp256k1 unchanged.
- Do not claim projective addition is cheaper without cleaning the old point and converting the output.
- Do not select QCLA, carry-save, or parallel multiplication on depth alone.
- Do not use Karatsuba at 256 bits solely because of its asymptotic exponent.
- Do not count a measured qubit as fully deleted while its classical phase record is unresolved.
- Do not treat a dirty ancilla as clean; it must return to its exact unknown input state.
- Do not rank approximate circuits without a composed whole-point-addition error bound.
- Do not count only forward arithmetic when the benchmark requires an in-place clean interface.

# Source index

All 32 local PDFs were checked as readable, publicly downloadable full texts.

1. Babbush et al., [arXiv:2603.28846](https://arxiv.org/abs/2603.28846).
2. Schrottenloher, [IACR ePrint 2026/1128](https://eprint.iacr.org/2026/1128).
3. Luo et al., [arXiv:2607.13816](https://arxiv.org/abs/2607.13816).
4. Chevignard, Fouque, and Schrottenloher, [IACR ePrint 2026/280](https://eprint.iacr.org/2026/280).
5. Kim et al., [IACR ePrint 2026/106](https://eprint.iacr.org/2026/106).
6. Häner et al., [IACR ePrint 2020/077](https://eprint.iacr.org/2020/077).
7. Roetteler et al., [arXiv:1706.06752](https://arxiv.org/abs/1706.06752).
8. Proos and Zalka, [arXiv:quant-ph/0301141](https://arxiv.org/abs/quant-ph/0301141).
9. Litinski, [arXiv:2306.08585](https://arxiv.org/abs/2306.08585).
10. Renes, Costello, and Batina, [IACR ePrint 2015/1060](https://eprint.iacr.org/2015/1060).
11. Hisil et al., [IACR ePrint 2008/522](https://eprint.iacr.org/2008/522).
12. Sarkar and Seo, [IACR ePrint 2025/017](https://eprint.iacr.org/2025/017).
13. Cuccaro et al., [arXiv:quant-ph/0410184](https://arxiv.org/abs/quant-ph/0410184).
14. Draper et al., [arXiv:quant-ph/0406142](https://arxiv.org/abs/quant-ph/0406142).
15. Draper, [arXiv:quant-ph/0008033](https://arxiv.org/abs/quant-ph/0008033).
16. Gidney, [arXiv:1709.06648](https://arxiv.org/abs/1709.06648).
17. Gidney, [arXiv:2507.23079](https://arxiv.org/abs/2507.23079).
18. Baksi, Chattopadhyay, and Seo, [IACR ePrint 2025/626](https://eprint.iacr.org/2025/626).
19. Gidney, [arXiv:1905.07682](https://arxiv.org/abs/1905.07682).
20. Gidney, [arXiv:1905.08488](https://arxiv.org/abs/1905.08488).
21. Häner, Roetteler, and Svore, [arXiv:1611.07995](https://arxiv.org/abs/1611.07995).
22. Luongo et al., [arXiv:2407.20167](https://arxiv.org/abs/2407.20167).
23. Rines and Chuang, [arXiv:1801.01081](https://arxiv.org/abs/1801.01081).
24. Gidney, [arXiv:1904.07356](https://arxiv.org/abs/1904.07356).
25. Lee et al., [arXiv:2608.11563](https://arxiv.org/abs/2608.11563).
26. Bernstein and Yang, [IACR ePrint 2019/266](https://eprint.iacr.org/2019/266).
27. Mukhopadhyay, Gheorghiu, and Krovi, [arXiv:2603.18110](https://arxiv.org/abs/2603.18110).
28. Khattar et al., [arXiv:2510.10967](https://arxiv.org/abs/2510.10967).
29. Litinski, [arXiv:2410.00899](https://arxiv.org/abs/2410.00899).
30. Kornerup, Sadun, and Soloveichik, [arXiv:2110.08973](https://arxiv.org/abs/2110.08973).
31. Paradis, Bichsel, and Vechev, [arXiv:2212.10395](https://arxiv.org/abs/2212.10395).
32. Liu, Zhou, and Meng, [arXiv:2608.09578](https://arxiv.org/abs/2608.09578).
