# ECDSA Fail: coverage-first 32-paper set

Revised 2026-09-11 for maximum useful breadth while remaining relevant to
reversible secp256k1 point addition and its
`average executed Toffolis × peak live qubits` objective.

## Selection rule

This is a breadth-first set, not simply the 32 papers closest in title to
ECDLP. A paper earns a slot when it contributes a substantially different
formula, arithmetic family, representation, space-time tradeoff, or
uncomputation technique. Closely overlapping resource-estimation papers are
de-emphasized unless they introduce a distinct circuit architecture. All
papers from the previously processed eight-paper knowledge base are retained
to preserve continuity with existing nodes and experiments. Every selected
paper has a publicly downloadable full-text PDF; publication date is not an
exclusion criterion.

## Coverage map

| Ground covered | Papers |
|---|---|
| Benchmark, public frontier, and historical ECDLP lineage | 1–9 |
| Complete formulas, other prime curves, and binary fields | 10–12 |
| Ripple, prefix, Fourier, carry-save, and constant adders | 13–18 |
| Windowing, approximation, and low-width modular arithmetic | 19–22 |
| Multiplication, reduction, inversion, division, and EEA restructuring | 23–29 |
| Measurement-aware pebbling, automatic cleanup, and dirty ancillas | 30–32 |

## A. Whole-circuit and point-addition architectures

| # | Paper | Distinct ground contributed | Likely ECDSA Fail use |
|---:|---|---|---|
| 1 | [Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities: Resource Estimates and Mitigations](https://arxiv.org/abs/2603.28846) — Babbush et al., 2026 | Benchmark source, secp256k1 resource frontier, approximate correctness, windowing, and measurement-based cleanup. | Target envelope and whole-circuit design |
| 2 | [Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms](https://eprint.iacr.org/2026/1128) — Schrottenloher, 2026 | Public low-qubit and low-Toffoli point-addition circuits designed against the same frontier. | Direct architectural comparison |
| 3 | [Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition](https://arxiv.org/abs/2607.13816) — Luo et al., 2026 | Register-sharing extended Euclid, explicit qubit reuse, and mid-circuit measurement. | Division workspace and register lending |
| 4 | [Reducing the Number of Qubits in Quantum Discrete Logarithms on Elliptic Curves](https://eprint.iacr.org/2026/280) — Chevignard, Fouque, and Schrottenloher, 2026 | Residue-number arithmetic, projective computation, and Legendre-symbol output as radically different low-width approaches. | Alternative representation and output design |
| 5 | [New Quantum Circuits for ECDLP: Breaking Prime Elliptic Curve Cryptography](https://eprint.iacr.org/2026/106) — Kim et al., 2026 | Affine/in-place versus projective/out-of-place point addition and carry-save arithmetic. | Coordinate and depth-width tradeoffs |
| 6 | [Improved Quantum Circuits for Elliptic Curve Discrete Logarithms](https://eprint.iacr.org/2020/077) — Häner, Jaques, Naehrig, Roetteler, and Soeken, 2020 | Established in-place affine lineage, signed windows, Montgomery inversion, and concrete prime-field costs. | Baseline operation schedule |
| 7 | [Quantum Resource Estimates for Computing Elliptic Curve Discrete Logarithms](https://arxiv.org/abs/1706.06752) — Roetteler, Naehrig, Svore, and Lauter, 2017 | First detailed full-stack reversible prime-field ECDLP construction at modern cryptographic sizes. | Correctness and resource baseline |
| 8 | [Shor's Discrete Logarithm Quantum Algorithm for Elliptic Curves](https://arxiv.org/abs/quant-ph/0301141) — Proos and Zalka, 2003 | Foundational register-sharing, exceptional-point handling, and approximate-correctness reasoning. | Reversibility assumptions and edge cases |
| 9 | [How to Compute a 256-bit Elliptic Curve Private Key with Only 50 Million Toffoli Gates](https://arxiv.org/abs/2306.08585) — Litinski, 2023 | Aggressive windowing, inversion batching, state reuse, and global weighting of point-addition costs. | Decide which local costs matter most |

## B. Group-law and field diversity

| # | Paper | Distinct ground contributed | Likely ECDSA Fail use |
|---:|---|---|---|
| 10 | [Complete Addition Formulas for Prime Order Elliptic Curves](https://eprint.iacr.org/2015/1060) — Renes, Costello, and Batina, 2016 | Complete short-Weierstrass formulas that avoid exceptional branches. | Alternative point-add schedules and correctness |
| 11 | [Twisted Edwards Curves Revisited](https://eprint.iacr.org/2008/522) — Hisil, Wong, Carter, and Dawson, 2008 | Twisted Edwards models, extended coordinates, and efficient unified addition and doubling formulas. | Alternative point-addition schedules and coordinate transformations |
| 12 | [New Quantum Cryptanalysis of Binary Elliptic Curves](https://eprint.iacr.org/2025/017) — Sarkar and Seo, 2025 | Characteristic-two field arithmetic and contrasting in-place/out-of-place point-addition layouts. | A deliberately different arithmetic architecture |

## C. Addition and comparison families

| # | Paper | Distinct ground contributed | Likely ECDSA Fail use |
|---:|---|---|---|
| 13 | [A New Quantum Ripple-Carry Addition Circuit](https://arxiv.org/abs/quant-ph/0410184) — Cuccaro, Draper, Kutin, and Moulton, 2004 | Canonical single-ancilla ripple carry with majority/unmajority structure. | Add, subtract, compare, and carry proofs |
| 14 | [A Logarithmic-Depth Quantum Carry-Lookahead Adder](https://arxiv.org/abs/quant-ph/0406142) — Draper, Kutin, Rains, and Svore, 2004 | Prefix generate/propagate arithmetic at the opposite space-depth point from ripple carry. | Chunked or parallel carry experiments |
| 15 | [Addition on a Quantum Computer](https://arxiv.org/abs/quant-ph/0008033) — Draper, 2000 | Fourier-basis addition without explicit carry registers. | Alternative arithmetic representation |
| 16 | [Halving the Cost of Quantum Addition](https://arxiv.org/abs/1709.06648) — Gidney, 2018 | Temporary logical ANDs and measurement-based erasure of carry information. | Toffoli reduction in carry ladders |
| 17 | [A Classical-Quantum Adder with Constant Workspace and Linear Gates](https://arxiv.org/abs/2507.23079) — Gidney, 2025 | Constant addition using clean/dirty workspace and measurement “venting.” | Known secp256k1 constants and folds |
| 18 | [Tree-based Quantum Carry-Save Adder](https://eprint.iacr.org/2025/626) — Baksi, Chattopadhyay, and Seo, 2025 | Concrete Wallace- and Dadda-tree carry-save arithmetic with multiplier integration. | Parallel multiplication and squaring |

## D. Windowing, approximation, and modular building blocks

| # | Paper | Distinct ground contributed | Likely ECDSA Fail use |
|---:|---|---|---|
| 19 | [Windowed Quantum Arithmetic](https://arxiv.org/abs/1905.07682) — Gidney, 2019 | Lookup-window tradeoffs for addition and multiplication. | Chunking and table-assisted arithmetic |
| 20 | [Approximate Encoded Permutations and Piecewise Quantum Adders](https://arxiv.org/abs/1905.08488) — Gidney, 2019 | Coset encodings, oblivious carry runways, and quantified approximation error. | Guard widths and error-budget allocation |
| 21 | [Factoring Using 2n+2 Qubits with Toffoli Based Modular Multiplication](https://arxiv.org/abs/1611.07995) — Häner, Roetteler, and Svore, 2017 | A compact toolkit for comparison, constant addition, modular reduction, and uncomputation. | Low-width modular primitives |
| 22 | [Measurement-Based Uncomputation of Quantum Circuits for Modular Arithmetic](https://arxiv.org/abs/2407.20167) — Luongo et al., 2024 | Systematic measurement-based cleanup for modular adders and multipliers, including when it saves gates. | Carry and quotient erasure |

## E. Multiplication, reduction, inversion, division, and EEA restructuring

| # | Paper | Distinct ground contributed | Likely ECDSA Fail use |
|---:|---|---|---|
| 23 | [High Performance Quantum Modular Multipliers](https://arxiv.org/abs/1801.01081) — Rines and Chuang, 2018 | Division-based, Montgomery, and Barrett-style modular multiplication architectures. | Compare exact multiplier families |
| 24 | [Asymptotically Efficient Quantum Karatsuba Multiplication](https://arxiv.org/abs/1904.07356) — Gidney, 2019 | Recursive multiplication with explicit reversible scheduling and reduced space overhead. | Multiplication and squaring crossovers |
| 25 | [Efficient Quantum Modular Reduction: Crandall Reduction and Its Fault-Tolerant Resource Analysis](https://arxiv.org/abs/2608.11563) — Lee et al., 2026 | Exact reduction for moduli of the form `2^n-c`, directly matching the shape of the secp256k1 prime. | Specialized multiplication, squaring, and folding |
| 26 | [Fast constant-time gcd computation and modular inversion](https://eprint.iacr.org/2019/266) — Bernstein and Yang, 2019 | Divsteps and fixed-time gcd/inversion replace a data-dependent Euclidean schedule with regular control flow. | Alternative inversion transcript, control schedule, and invariants |
| 27 | [Improved Quantum Circuits for Division](https://arxiv.org/abs/2603.18110) — Mukhopadhyay, Gheorghiu, and Krovi, 2026 | Reversible and non-reversible division built around a fused compare-and-conditional-subtract primitive, with explicit gate and ancilla tradeoffs. | Quotient steps inside inversion/division |
| 28 | [Verifiable Quantum Advantage via Optimized DQI Circuits](https://arxiv.org/abs/2510.10967) — Khattar et al., 2025 | Separates Euclidean evolution from Bézout reconstruction using an operation transcript or “dialog,” the restructuring later adapted by point-addition work. | History compression, Bézout replay, and in-place inversion |
| 29 | [Quantum Schoolbook Multiplication with Fewer Toffoli Gates](https://arxiv.org/abs/2410.00899) — Litinski, 2024 | Low-Toffoli schoolbook multiplication using controlled add-subtract circuits and measurement-based uncomputation. | A practical alternative to recursive multiplication |

## F. Measurement-aware space-time scheduling and ancilla reuse

| # | Paper | Distinct ground contributed | Likely ECDSA Fail use |
|---:|---|---|---|
| 30 | [Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements](https://arxiv.org/abs/2110.08973) — Kornerup, Sadun, and Soloveichik, 2021 | Measurement-aware pebbling that trades classical records and recomputation for fewer simultaneously live qubits. | Whole-circuit register recycling |
| 31 | [Reqomp: Space-Constrained Uncomputation for Quantum Circuits](https://arxiv.org/abs/2212.10395) — Paradis et al., 2024 | Automatic dependency-aware uncomputation under a qubit budget. | Discover cleanup schedules humans may miss |
| 32 | [Quantum Uncomputation of Clean and Dirty Ancilla Qubits](https://arxiv.org/abs/2608.09578) — Liu, Zhou, and Meng, 2026 | A unified framework and synthesis methods for uncomputing values held in clean or borrowed dirty ancillas. | Formalize register lending and dirty-workspace reuse |

## What changed from the earlier list

- Added explicit coverage of complete point formulas, Fourier arithmetic,
  modern carry-save trees, special-form Crandall reduction, improved division,
  automatic uncomputation, and dirty-ancilla cleanup.
- Retained all eight papers from the previously processed consolidated KB,
  including Litinski's schoolbook multiplier, the spooky pebble game, and
  Khattar et al.'s DQI/EEA restructuring paper.
- Kept twisted-Edwards and binary-curve papers intentionally: they are less
  directly tied to secp256k1, but broaden the design space with different
  coordinates, fields, inversion methods, and multiplication structures.
- Replaced the two subscription-only entries with publicly downloadable IACR
  ePrint papers: Hisil et al. for twisted-Edwards formulas and Bernstein-Yang
  for constant-time gcd and modular inversion. The four papers first posted
  after May 27, 2026 remain in the set because they already have open access.
- Removed or deprioritized papers whose main novelty is physical-resource
  estimation, distributed execution, generic QROM erasure, or a second
  treatment of constant-specialized arithmetic. Those mechanisms remain
  represented through papers 6, 17, 19, 25, and 31.
- Corrected the identifier for Gidney's constant-workspace adder to
  `arXiv:2507.23079`.

## Preprocessing guidance

Each paper should be tagged by mechanism rather than only by bibliographic
topic. At minimum, extract:

1. arithmetic representation and coordinate system;
2. forward operation, inverse operation, and cleanup method;
3. simultaneously live registers at the high-water mark;
4. Toffoli/CCZ cost, measurements, Clifford gates, and ancillas;
5. assumptions about known constants, dirty workspace, or tolerated error;
6. formulas or pseudocode transferable to `pingpong`, `modular`,
   `const_arith`, or `square`;
7. incompatibilities with the benchmark's validation and reversibility rules.
