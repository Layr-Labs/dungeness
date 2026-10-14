# Space-Efficient Quantum ECDLP Paper Knowledge Base

This standalone knowledge base processes:

*Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition*, by Han Luo, Ziyi Yang, Jingquan Luo, Ziruo Wang, Yuexin Su, Xiaoming Sun, Lvzhou Li, and Tongyang Li, arXiv:2607.13816v2.

The paper develops an exact low-space reversible modular-inversion circuit, builds affine point addition with three field-sized registers using mid-circuit measurement, and reports concrete logical resources for secp256k1.

## Entry points

- [`agent-pack.md`](agent-pack.md) — compact implementation brief.
- [`index.md`](index.md) — complete navigation.
- [`graph.md`](graph.md) — dependency graph.
- [`AGENTS.md`](AGENTS.md) — instructions for an agent using the KB.
- [`concepts/luo-porting-to-ecdsa-fail.md`](concepts/luo-porting-to-ecdsa-fail.md) — benchmark-transfer plan.

## Structure

- [`sections/`](sections/) follows the paper in reading order.
- [`nodes/`](nodes/) contains 18 atomic algorithms, claims, resource facts, and transfer notes.
- [`concepts/`](concepts/) integrates those nodes into implementation decisions.
- [`sources/`](sources/) records paper provenance and the pinned companion-code map.

## Evidence labels

- **[PAPER]** A result or claim in arXiv:2607.13816v2.
- **[CODE]** A fact from the companion repository at the pinned revision.
- **[BENCHMARK]** A fact about the target benchmark or a trusted local run.
- **[INFERENCE]** A proposed implementation transfer or experiment.

The distinction matters. Paper-level logical resources and companion-code tests are not proof that a benchmark port is correct or competitive.

## Key results

For an `n`-bit prime:

```text
modular inversion = 2n + 6 floor(log2 n) + 19 qubits
point addition     = 3n + 6 floor(log2 n) + 19 qubits
point addition     < 1003n^2 + O(n log n) Toffolis
```

At `n=256`:

```text
modular inversion: 579 qubits, 30.59M Toffolis
point addition:    835 qubits, 70.10M Toffolis
full ECDLP:        approximately 2^30.88 Toffolis
```

The source contains one inconsistent `2^30.63` sentence. The displayed formula, abstract, and comparison table support `2^30.88`.

## Primary sources

- Paper: https://arxiv.org/abs/2607.13816
- Paper HTML: https://arxiv.org/html/2607.13816v2
- Companion implementation: https://github.com/ZeroWang030221/Space-Efficient-Quantum-Algorithm-for-Elliptic-Curve-Discrete-Logarithms-with-Resource-Estimation

Start with [`index.md`](index.md). Only a trusted benchmark evaluator can establish that an implementation works.

