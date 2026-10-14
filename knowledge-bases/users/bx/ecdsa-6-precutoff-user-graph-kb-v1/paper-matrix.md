# Paper matrix

| Paper | Main reusable idea | Representation | Cost model | Main import warning |
|---|---|---|---|---|
| [arXiv:2410.00899v1](sections/01-litinski-schoolbook-multiplication.md) | Replace shifted controlled additions by controlled add-subtract operations and repair the aggregate affine offset globally. | binary integers; Montgomery residues for the prime-modulus construction | exact Toffoli count | The prime-modulus construction is out-of-place, uses Montgomery representation, and produces garbage. |
| [arXiv:2407.20167v1](sections/02-luongo-measurement-based-uncomputation.md) | Measure a one-bit predicate, accept the free branch, and invoke a self-adjoint repair computation only on the phase-error branch. | binary modular arithmetic with measurement and classical feed-forward | expected Toffoli count | The repair must implement the one-bit self-adjoint XOR-oracle contract; expected cost assumes equiprobable measurement branches. |
| [arXiv:2507.23079v1](sections/03-gidney-classical-quantum-adder.md) | Vent carry garbage into deferred phase corrections and trade clean workspace for dirty borrowing. | quantum binary target plus classical addend | asymptotic Toffoli count with clean/dirty workspace split | The construction is a classical-offset adder; the measurement outcomes create phase-correction obligations. |
| [arXiv:2110.08973v3](sections/04-kornerup-spooky-pebble-game.md) | Recycle qubits by replacing a computed value with a phase ghost indexed by retained classical measurement data. | reversible computation graph with quantum pebbles and classical ghosts | time-space pebbling bound; quantum and classical memory distinguished | Quantum space is recycled, but the classical measurement record remains live until unghosting. |
| [arXiv:2510.10967v1](sections/05-khattar-dialog-eea.md) | Represent the EEA as an executable transition trace (“Dialog”) and replay it on a different vector to divide directly. | polynomials and transition matrices over \(\mathrm{GF}(2^b)\) | underlying field-operation counts and circuit costs specialized to binary extension fields | The quantitative analysis is specialized to polynomial arithmetic over \(\mathrm{GF}(2^b)\), not large-prime integer arithmetic. |
| [IACR ePrint 2020/077](sections/06-haner-improved-ecdlp-circuits.md) | Normalize four Kaliski branches into one swapped round body, run a fixed schedule, and fuse correction and cleanup. | Montgomery residues and reversible binary-GCD/Kaliski state | Toffoli/T-depth/qubit resource accounting at component and ECDLP levels | The inversion and multiplication stack uses Montgomery-form arithmetic and tightly coupled register lifetimes. |

## Quick route by problem

| Problem | Start with |
|---|---|
| Reduce multiplication Toffolis | [KB-LIT-01](nodes/controlled-add-subtract.md), [KB-LIT-02](nodes/intermediate-expression-and-cost.md) |
| Reduce modular-adder cleanup cost | [KB-LUO-01](nodes/one-bit-mbu-branches.md), [KB-LUO-02](nodes/gidney-modular-adder-costs.md) |
| Add a caller control cheaply | [KB-LUO-03](nodes/external-control-scope.md), [KB-GID-03](nodes/outer-control-at-zero-toffoli.md) |
| Reduce clean workspace | [KB-GID-01](nodes/workspace-toffoli-tradeoffs.md), [KB-KSS-02](nodes/spooky-pebble-binomial-bound.md) |
| Track measurement-induced obligations | [Measurement synthesis](concepts/measurement-uncomputation-and-phase-debt.md) |
| Avoid materializing an inverse | [KB-KHA-01](nodes/explicit-vs-implicit-bezout.md), [KB-KHA-02](nodes/direct-division-by-dialog-replay.md) |
| Build fixed-round prime-field inversion | [KB-HAN-01](nodes/normalized-kaliski-round.md), [KB-HAN-02](nodes/fixed-rounds-and-pseudoinverse-correction.md) |
| Exploit register lifetimes | [KB-HAN-03](nodes/producer-consumer-and-workspace-reuse.md) |
