# Knowledge-base index

## Browse by paper

1. [Quantum schoolbook multiplication with fewer Toffoli gates](sections/01-litinski-schoolbook-multiplication.md)
2. [Measurement-based uncomputation of quantum circuits for modular arithmetic](sections/02-luongo-measurement-based-uncomputation.md)
3. [A Classical-Quantum Adder with Constant Workspace and Linear Gates](sections/03-gidney-classical-quantum-adder.md)
4. [Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements](sections/04-kornerup-spooky-pebble-game.md)
5. [Verifiable Quantum Advantage via Optimized DQI Circuits](sections/05-khattar-dialog-eea.md)
6. [Improved quantum circuits for elliptic curve discrete logarithms](sections/06-haner-improved-ecdlp-circuits.md)

## Atomic nodes

### arXiv:2410.00899v1 — Quantum schoolbook multiplication with fewer Toffoli gates

- [KB-LIT-01 — Replacement for shifted controlled addition](nodes/controlled-add-subtract.md) — A controlled add-subtract adds the shifted multiplicand for control 1 and subtracts it for control 0 at the cost of an uncontrolled adder.
- [KB-LIT-02 — Exact intermediate expression and non-modular cost](nodes/intermediate-expression-and-cost.md) — The affine intermediate value is globally corrected and shifted to obtain multiplication in \(n^2+4n+3\) Toffolis.
- [KB-LIT-03 — Prime-field interface limitation](nodes/prime-field-interface-limit.md) — The prime multiplier is not a drop-in in-place canonical-field operation because it is out-of-place, Montgomery-form, and garbage-producing.
### arXiv:2407.20167v1 — Measurement-based uncomputation of quantum circuits for modular arithmetic

- [KB-LUO-01 — The two branches of the one-bit MBU lemma](nodes/one-bit-mbu-branches.md) — Outcome 0 erases the predicate for free; outcome 1 leaves phase kickback and invokes a self-adjoint XOR-oracle repair.
- [KB-LUO-02 — Gidney modular-adder costs after MBU](nodes/gidney-modular-adder-costs.md) — MBU lowers the expected costs to \(3.5n\) and \(4.5n+0.5\) Toffolis for uncontrolled and controlled modular addition.
- [KB-LUO-03 — Where the external control is actually required](nodes/external-control-scope.md) — Only the initial addition and final flag-erasing comparison require the caller’s control.
### arXiv:2507.23079v1 — A Classical-Quantum Adder with Constant Workspace and Linear Gates

- [KB-GID-01 — Principal workspace/Toffoli tradeoffs](nodes/workspace-toffoli-tradeoffs.md) — The principal operating points trade three clean ancillas for \(4n\) Toffolis or use \(n-2\) dirty ancillas to reach \(3n\).
- [KB-GID-02 — Carry identity used for venting](nodes/carry-venting-identity.md) — The carry string can be reconstructed after addition, allowing X-basis measurement to replace carry garbage with deferred phase work.
- [KB-GID-03 — Why an outer control adds no Toffolis](nodes/outer-control-at-zero-toffoli.md) — The outer control substitutes for hardwired one-bits of the classical offset, adding no nonlinear gates in the paper’s accounting.
### arXiv:2110.08973v3 — Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements

- [KB-KSS-01 — Ghosting transformation and precondition](nodes/ghosting-transformation.md) — Ghosting resets a quantum value while retaining a classical string that indexes the resulting phase; distinct labels prevent amplitude collisions.
- [KB-KSS-02 — Binomial line-length relation](nodes/spooky-pebble-binomial-bound.md) — Binomial relations characterize the line length reachable with a bounded number of pebbles and a time parameter.
- [KB-KSS-03 — Memory that remains live](nodes/live-classical-memory.md) — Recycled qubits leave behind a live classical measurement record and an unresolved phase obligation.
### arXiv:2510.10967v1 — Verifiable Quantum Advantage via Optimized DQI Circuits

- [KB-KHA-01 — Explicit versus implicit Bézout access](nodes/explicit-vs-implicit-bezout.md) — Explicit access materializes the total Bézout matrix; implicit access keeps the EEA transition sequence executable.
- [KB-KHA-02 — Direct division without materializing \(B^{-1}\)](nodes/direct-division-by-dialog-replay.md) — Applying the EEA transition product to \([0,A]^T\) emits \(AB^{-1}\) directly without storing \(B^{-1}\).
- [KB-KHA-03 — What the Dialog encodes and transfer limitation](nodes/dialog-and-prime-field-transfer-limit.md) — Dialog records elementary EEA transitions, but its \(\mathrm{GF}(2^b)\) resource counts do not transfer directly to carry-based prime-field arithmetic.
### IACR ePrint 2020/077 — Improved quantum circuits for elliptic curve discrete logarithms

- [KB-HAN-01 — Normalizing the four Kaliski cases](nodes/normalized-kaliski-round.md) — Conditional swaps orient all four Kaliski cases into a single subtract/add, halve, and double round body.
- [KB-HAN-02 — Fixed rounds and integrated pseudo-inverse correction](nodes/fixed-rounds-and-pseudoinverse-correction.md) — The circuit schedules \(2n\) rounds and performs the \(2n-k\) correction doublings concurrently with reverse cleanup.
- [KB-HAN-03 — Producer/consumer and workspace-reuse examples](nodes/producer-consumer-and-workspace-reuse.md) — Consume a producer’s result before reversing its garbage, and reuse registers that temporarily hold known constants.

## Browse by concept

- [Representation And Interface Contracts](concepts/representation-and-interface-contracts.md)
- [Measurement Uncomputation And Phase Debt](concepts/measurement-uncomputation-and-phase-debt.md)
- [Control Locality And Controlled Arithmetic](concepts/control-locality-and-controlled-arithmetic.md)
- [Eea Representations And Inversion](concepts/eea-representations-and-inversion.md)
- [Time Space And Cost Models](concepts/time-space-and-cost-models.md)
- [Producer Consumer And Lifetime Optimization](concepts/producer-consumer-and-lifetime-optimization.md)
- [Cross Paper Opportunity Map](concepts/cross-paper-opportunity-map.md)
- [Import Checklist](concepts/import-checklist.md)

## Machine-readable indexes

- [`manifest.json`](manifest.json): package and source metadata
- [`nodes.jsonl`](nodes.jsonl): one complete atomic-node record per line
- [`graph.json`](graph.json): node relationships
