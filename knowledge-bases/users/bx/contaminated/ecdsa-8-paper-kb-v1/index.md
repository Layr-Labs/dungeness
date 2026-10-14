# Unified KB index

## Fast path

- [`README.md`](README.md)
- [`agent-pack.md`](agent-pack.md)
- [`paper-matrix.md`](paper-matrix.md)
- [`experiment-map.md`](experiment-map.md)
- [`manifest.md`](manifest.md)
- [`concepts/benchmark-contract.md`](concepts/benchmark-contract.md)
- [`concepts/current-benchmark-architecture.md`](concepts/current-benchmark-architecture.md)
- [`concepts/compatibility-and-conflicts.md`](concepts/compatibility-and-conflicts.md)
- [`graph.md`](graph.md)

## Paper 1 — Schrottenloher, arXiv:2606.02235

Sections:

- [`sections/01-introduction.md`](sections/01-introduction.md)
- [`sections/02-high-level-structure.md`](sections/02-high-level-structure.md)
- [`sections/03-modular-in-place-multiplication.md`](sections/03-modular-in-place-multiplication.md)
- [`sections/04-approximate-and-modular-arithmetic.md`](sections/04-approximate-and-modular-arithmetic.md)
- [`sections/05-discussion.md`](sections/05-discussion.md)

Atomic nodes:

- [`nodes/secp256k1-prime.md`](nodes/secp256k1-prime.md)
- [`nodes/shor-point-multiplication.md`](nodes/shor-point-multiplication.md)
- [`nodes/windowed-point-addition.md`](nodes/windowed-point-addition.md)
- [`nodes/affine-point-addition.md`](nodes/affine-point-addition.md)
- [`nodes/euclid-history.md`](nodes/euclid-history.md)
- [`nodes/register-sharing.md`](nodes/register-sharing.md)
- [`nodes/history-compression.md`](nodes/history-compression.md)
- [`nodes/bezout-replay.md`](nodes/bezout-replay.md)
- [`nodes/in-place-modular-multiplication.md`](nodes/in-place-modular-multiplication.md)
- [`nodes/adder-tradeoffs.md`](nodes/adder-tradeoffs.md)
- [`nodes/approximate-comparison.md`](nodes/approximate-comparison.md)
- [`nodes/generic-modular-doubling.md`](nodes/generic-modular-doubling.md)
- [`nodes/pseudo-mersenne-doubling.md`](nodes/pseudo-mersenne-doubling.md)
- [`nodes/generic-controlled-modular-addition.md`](nodes/generic-controlled-modular-addition.md)
- [`nodes/pseudo-mersenne-controlled-addition.md`](nodes/pseudo-mersenne-controlled-addition.md)
- [`nodes/x-plus-y-equals-p.md`](nodes/x-plus-y-equals-p.md)
- [`nodes/measurement-based-uncomputation.md`](nodes/measurement-based-uncomputation.md)
- [`nodes/implementation-parameters.md`](nodes/implementation-parameters.md)
- [`nodes/failure-model.md`](nodes/failure-model.md)
- [`nodes/resource-estimates.md`](nodes/resource-estimates.md)
- [`nodes/cost-hotspots.md`](nodes/cost-hotspots.md)
- [`nodes/benchmark-adaptation.md`](nodes/benchmark-adaptation.md)

Source:

- [`sources/2606.02235.md`](sources/2606.02235.md)
- [`sources/companion-code-map.md`](sources/companion-code-map.md)

## Paper 2 — Litinski, arXiv:2410.00899

Sections:

- [`sections/2410.00899-01-controlled-add-subtract.md`](sections/2410.00899-01-controlled-add-subtract.md)
- [`sections/2410.00899-02-multiplication-and-transfer.md`](sections/2410.00899-02-multiplication-and-transfer.md)

Nodes:

- [`nodes/litinski-controlled-add-subtract.md`](nodes/litinski-controlled-add-subtract.md)
- [`nodes/litinski-global-corrections.md`](nodes/litinski-global-corrections.md)
- [`nodes/litinski-schoolbook-multiplication.md`](nodes/litinski-schoolbook-multiplication.md)
- [`nodes/litinski-prime-modular-multiplication.md`](nodes/litinski-prime-modular-multiplication.md)
- [`nodes/litinski-benchmark-adaptation.md`](nodes/litinski-benchmark-adaptation.md)

Source: [`sources/2410.00899.md`](sources/2410.00899.md)

## Paper 3 — Luongo et al., arXiv:2407.20167

Sections:

- [`sections/2407.20167-01-mbu-framework.md`](sections/2407.20167-01-mbu-framework.md)
- [`sections/2407.20167-02-modular-adders.md`](sections/2407.20167-02-modular-adders.md)
- [`sections/2407.20167-03-benchmark-transfer.md`](sections/2407.20167-03-benchmark-transfer.md)

Nodes:

- [`nodes/luongo-single-qubit-mbu.md`](nodes/luongo-single-qubit-mbu.md)
- [`nodes/luongo-expected-cost-semantics.md`](nodes/luongo-expected-cost-semantics.md)
- [`nodes/luongo-modular-adder-shell.md`](nodes/luongo-modular-adder-shell.md)
- [`nodes/luongo-controlled-and-constant-mbu.md`](nodes/luongo-controlled-and-constant-mbu.md)
- [`nodes/luongo-benchmark-adaptation.md`](nodes/luongo-benchmark-adaptation.md)

Source: [`sources/2407.20167.md`](sources/2407.20167.md)

## Paper 4 — Gidney, arXiv:2507.23079

Sections:

- [`sections/2507.23079-01-venting-and-repair.md`](sections/2507.23079-01-venting-and-repair.md)
- [`sections/2507.23079-02-borrowing-and-controls.md`](sections/2507.23079-02-borrowing-and-controls.md)

Nodes:

- [`nodes/gidney-z-redundant-carries.md`](nodes/gidney-z-redundant-carries.md)
- [`nodes/gidney-carry-venting.md`](nodes/gidney-carry-venting.md)
- [`nodes/gidney-carry-xor-repair.md`](nodes/gidney-carry-xor-repair.md)
- [`nodes/gidney-dirty-half-borrowing.md`](nodes/gidney-dirty-half-borrowing.md)
- [`nodes/gidney-constant-workspace-adder.md`](nodes/gidney-constant-workspace-adder.md)
- [`nodes/gidney-zero-overhead-control.md`](nodes/gidney-zero-overhead-control.md)
- [`nodes/gidney-benchmark-adaptation.md`](nodes/gidney-benchmark-adaptation.md)

Source: [`sources/2507.23079.md`](sources/2507.23079.md)

## Paper 5 — Kornerup, Sadun, and Soloveichik, arXiv:2110.08973v3

Sections:

- [`sections/2110.08973-01-ghosting-model.md`](sections/2110.08973-01-ghosting-model.md)
- [`sections/2110.08973-02-line-tradeoffs.md`](sections/2110.08973-02-line-tradeoffs.md)
- [`sections/2110.08973-03-benchmark-transfer.md`](sections/2110.08973-03-benchmark-transfer.md)

Nodes:

- [`nodes/spooky-ghosting-semantics.md`](nodes/spooky-ghosting-semantics.md)
- [`nodes/spooky-line-frontier.md`](nodes/spooky-line-frontier.md)
- [`nodes/spooky-general-computation.md`](nodes/spooky-general-computation.md)
- [`nodes/spooky-dag-and-tree.md`](nodes/spooky-dag-and-tree.md)
- [`nodes/spooky-pingpong-scheduling.md`](nodes/spooky-pingpong-scheduling.md)

Source: [`sources/2110.08973.md`](sources/2110.08973.md)

## Paper 6 — Luo et al., arXiv:2607.13816v2

Sections:

- [`sections/2607.13816-01-introduction-and-contributions.md`](sections/2607.13816-01-introduction-and-contributions.md)
- [`sections/2607.13816-02-preliminaries-and-shor.md`](sections/2607.13816-02-preliminaries-and-shor.md)
- [`sections/2607.13816-03-space-efficient-eea.md`](sections/2607.13816-03-space-efficient-eea.md)
- [`sections/2607.13816-04-location-controlled-circuits.md`](sections/2607.13816-04-location-controlled-circuits.md)
- [`sections/2607.13816-05-measured-point-addition.md`](sections/2607.13816-05-measured-point-addition.md)
- [`sections/2607.13816-06-resources-and-ecdlp.md`](sections/2607.13816-06-resources-and-ecdlp.md)

Nodes:

- [`nodes/luo-four-phase-eea.md`](nodes/luo-four-phase-eea.md)
- [`nodes/luo-uniform-step-bound.md`](nodes/luo-uniform-step-bound.md)
- [`nodes/luo-shared-work-registers.md`](nodes/luo-shared-work-registers.md)
- [`nodes/luo-length-registers.md`](nodes/luo-length-registers.md)
- [`nodes/luo-optimized-eea-step.md`](nodes/luo-optimized-eea-step.md)
- [`nodes/luo-space-efficient-modular-inversion.md`](nodes/luo-space-efficient-modular-inversion.md)
- [`nodes/luo-active-windows.md`](nodes/luo-active-windows.md)
- [`nodes/luo-unary-iteration.md`](nodes/luo-unary-iteration.md)
- [`nodes/luo-location-controlled-swap.md`](nodes/luo-location-controlled-swap.md)
- [`nodes/luo-location-controlled-add-sub.md`](nodes/luo-location-controlled-add-sub.md)
- [`nodes/luo-dirty-length-update.md`](nodes/luo-dirty-length-update.md)
- [`nodes/luo-hadamard-register-recycling.md`](nodes/luo-hadamard-register-recycling.md)
- [`nodes/luo-in-place-division.md`](nodes/luo-in-place-division.md)
- [`nodes/luo-in-place-multiplication.md`](nodes/luo-in-place-multiplication.md)
- [`nodes/luo-horner-modular-multiplication.md`](nodes/luo-horner-modular-multiplication.md)
- [`nodes/luo-resource-estimates.md`](nodes/luo-resource-estimates.md)
- [`nodes/luo-benchmark-adaptation.md`](nodes/luo-benchmark-adaptation.md)
- [`nodes/luo-hybridization-opportunities.md`](nodes/luo-hybridization-opportunities.md)

Sources:

- [`sources/2607.13816.md`](sources/2607.13816.md)
- [`sources/2607.13816-code-map.md`](sources/2607.13816-code-map.md)

## Paper 7 — Khattar et al., arXiv:2510.10967

Sections:

- [`sections/2510.10967-01-explicit-vs-implicit.md`](sections/2510.10967-01-explicit-vs-implicit.md)
- [`sections/2510.10967-02-synchronized-eea.md`](sections/2510.10967-02-synchronized-eea.md)
- [`sections/2510.10967-03-dialog.md`](sections/2510.10967-03-dialog.md)
- [`sections/2510.10967-04-prime-field-transfer.md`](sections/2510.10967-04-prime-field-transfer.md)

Nodes:

- [`nodes/khattar-explicit-vs-implicit-bezout.md`](nodes/khattar-explicit-vs-implicit-bezout.md)
- [`nodes/khattar-in-register-quotient.md`](nodes/khattar-in-register-quotient.md)
- [`nodes/khattar-unified-eea-cycle.md`](nodes/khattar-unified-eea-cycle.md)
- [`nodes/khattar-dialog-representation.md`](nodes/khattar-dialog-representation.md)
- [`nodes/khattar-growing-dialog.md`](nodes/khattar-growing-dialog.md)
- [`nodes/khattar-direct-division.md`](nodes/khattar-direct-division.md)
- [`nodes/khattar-prime-field-barriers.md`](nodes/khattar-prime-field-barriers.md)
- [`nodes/khattar-benchmark-adaptation.md`](nodes/khattar-benchmark-adaptation.md)

Source: [`sources/2510.10967.md`](sources/2510.10967.md)

## Paper 8 — Häner et al., ePrint 2020/077

Sections:

- [`sections/2020-077-01-arithmetic-components.md`](sections/2020-077-01-arithmetic-components.md)
- [`sections/2020-077-02-pebbling-windowing.md`](sections/2020-077-02-pebbling-windowing.md)
- [`sections/2020-077-03-inversion-and-point-addition.md`](sections/2020-077-03-inversion-and-point-addition.md)
- [`sections/2020-077-04-resources-and-transfer.md`](sections/2020-077-04-resources-and-transfer.md)

Nodes:

- [`nodes/haner-montgomery-windowed-multiplication.md`](nodes/haner-montgomery-windowed-multiplication.md)
- [`nodes/haner-integrated-multiply-add.md`](nodes/haner-integrated-multiply-add.md)
- [`nodes/haner-adaptive-pebbling.md`](nodes/haner-adaptive-pebbling.md)
- [`nodes/haner-signed-windowing.md`](nodes/haner-signed-windowing.md)
- [`nodes/haner-swap-normalized-kaliski.md`](nodes/haner-swap-normalized-kaliski.md)
- [`nodes/haner-pseudoinverse-correction.md`](nodes/haner-pseudoinverse-correction.md)
- [`nodes/haner-division-workspace-reuse.md`](nodes/haner-division-workspace-reuse.md)
- [`nodes/haner-affine-point-add-shell.md`](nodes/haner-affine-point-add-shell.md)
- [`nodes/haner-resource-baseline.md`](nodes/haner-resource-baseline.md)
- [`nodes/haner-benchmark-adaptation.md`](nodes/haner-benchmark-adaptation.md)

Source: [`sources/2020-077.md`](sources/2020-077.md)

## Cross-paper concepts

- [`concepts/benchmark-contract.md`](concepts/benchmark-contract.md)
- [`concepts/current-benchmark-architecture.md`](concepts/current-benchmark-architecture.md)
- [`concepts/resource-model.md`](concepts/resource-model.md)
- [`concepts/mechanism-selection.md`](concepts/mechanism-selection.md)
- [`concepts/arithmetic-primitives.md`](concepts/arithmetic-primitives.md)
- [`concepts/history-and-bezout-representations.md`](concepts/history-and-bezout-representations.md)
- [`concepts/measurement-assisted-uncomputation.md`](concepts/measurement-assisted-uncomputation.md)
- [`concepts/time-space-scheduling.md`](concepts/time-space-scheduling.md)
- [`concepts/controlled-constant-arithmetic.md`](concepts/controlled-constant-arithmetic.md)
- [`concepts/field-model-transfer.md`](concepts/field-model-transfer.md)
- [`concepts/compatibility-and-conflicts.md`](concepts/compatibility-and-conflicts.md)
- [`concepts/experiment-priority.md`](concepts/experiment-priority.md)
- [`concepts/standalone-kb-expectations.md`](concepts/standalone-kb-expectations.md)

Source-specific concepts retained from the earlier two-paper KB:

- [`concepts/dialog-in-place-multiplication.md`](concepts/dialog-in-place-multiplication.md)
- [`concepts/garbage-tape.md`](concepts/garbage-tape.md)
- [`concepts/approximate-arithmetic.md`](concepts/approximate-arithmetic.md)
- [`concepts/point-addition.md`](concepts/point-addition.md)
- [`concepts/porting-to-ecdsa-fail.md`](concepts/porting-to-ecdsa-fail.md)
- [`concepts/hypotheses.md`](concepts/hypotheses.md)
- [`concepts/luo-location-controlled-arithmetic.md`](concepts/luo-location-controlled-arithmetic.md)
- [`concepts/luo-measured-register-recycling.md`](concepts/luo-measured-register-recycling.md)
- [`concepts/luo-vs-schrottenloher.md`](concepts/luo-vs-schrottenloher.md)
- [`concepts/luo-porting-to-ecdsa-fail.md`](concepts/luo-porting-to-ecdsa-fail.md)
- [`concepts/luo-hypotheses.md`](concepts/luo-hypotheses.md)

## Benchmark provenance

- [`sources/benchmark-live-pingpong.md`](sources/benchmark-live-pingpong.md)
- [`log.md`](log.md)
