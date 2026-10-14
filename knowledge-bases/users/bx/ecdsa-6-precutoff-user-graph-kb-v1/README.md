# Six-paper quantum arithmetic knowledge base

This is the decomposed, agent-oriented version of the six-paper report. It follows the earlier packaged format: paper pages, atomic nodes, cross-paper concepts, provenance, indexes, a graph, and a single-file agent pack.

## Start here

- **Fastest one-file context:** [agent-pack.md](agent-pack.md)
- **Browse by paper or node:** [index.md](index.md)
- **Compare the papers:** [paper-matrix.md](paper-matrix.md)
- **See relationships:** [graph.md](graph.md)
- **Instructions for an implementation agent:** [AGENTS.md](AGENTS.md)

## Contents

- 6 exact requested paper versions
- 18 source-grounded atomic nodes with stable IDs
- 8 cross-paper concept and transfer pages
- 6 source-provenance pages with build-PDF SHA-256 hashes
- `manifest.json`, `nodes.jsonl`, and `graph.json` for tool ingestion

## Recommended retrieval path

1. Read `AGENTS.md` and `paper-matrix.md`.
2. Search `index.md` for the implementation problem, not only the paper terminology.
3. Open two to five relevant atomic nodes.
4. Follow related-node and concept links to expose assumptions and incompatibilities.
5. Verify the cited source location before implementing a mechanism.

## Paper pages

1. [Quantum schoolbook multiplication with fewer Toffoli gates](sections/01-litinski-schoolbook-multiplication.md)
2. [Measurement-based uncomputation of quantum circuits for modular arithmetic](sections/02-luongo-measurement-based-uncomputation.md)
3. [A Classical-Quantum Adder with Constant Workspace and Linear Gates](sections/03-gidney-classical-quantum-adder.md)
4. [Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements](sections/04-kornerup-spooky-pebble-game.md)
5. [Verifiable Quantum Advantage via Optimized DQI Circuits](sections/05-khattar-dialog-eea.md)
6. [Improved quantum circuits for elliptic curve discrete logarithms](sections/06-haner-improved-ecdlp-circuits.md)

## Cross-paper concepts

- [Representation And Interface Contracts](concepts/representation-and-interface-contracts.md)
- [Measurement Uncomputation And Phase Debt](concepts/measurement-uncomputation-and-phase-debt.md)
- [Control Locality And Controlled Arithmetic](concepts/control-locality-and-controlled-arithmetic.md)
- [Eea Representations And Inversion](concepts/eea-representations-and-inversion.md)
- [Time Space And Cost Models](concepts/time-space-and-cost-models.md)
- [Producer Consumer And Lifetime Optimization](concepts/producer-consumer-and-lifetime-optimization.md)
- [Cross Paper Opportunity Map](concepts/cross-paper-opportunity-map.md)
- [Import Checklist](concepts/import-checklist.md)

## Sources

- [arXiv:2410.00899v1 — Quantum schoolbook multiplication with fewer Toffoli gates](sources/2410.00899v1.md)
- [arXiv:2407.20167v1 — Measurement-based uncomputation of quantum circuits for modular arithmetic](sources/2407.20167v1.md)
- [arXiv:2507.23079v1 — A Classical-Quantum Adder with Constant Workspace and Linear Gates](sources/2507.23079v1.md)
- [arXiv:2110.08973v3 — Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements](sources/2110.08973v3.md)
- [arXiv:2510.10967v1 — Verifiable Quantum Advantage via Optimized DQI Circuits](sources/2510.10967v1.md)
- [IACR ePrint 2020/077 — Improved quantum circuits for elliptic curve discrete logarithms](sources/2020-077.md)

## Evidence policy

Atomic claims are labelled `PAPER`. Cross-paper compositions are explicitly described as supported compositions, architecture syntheses, transfer requirements, or research hypotheses. The original papers remain authoritative.

Built: 2026-09-10.
