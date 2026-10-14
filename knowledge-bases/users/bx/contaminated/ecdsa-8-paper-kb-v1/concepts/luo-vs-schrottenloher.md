# Luo et al. versus Schrottenloher

These papers should not be ranked on qubits alone. They optimize different architectures.

| Dimension | Schrottenloher, 2606.02235 | Luo et al., 2607.13816v2 |
|---|---|---|
| Main objective | low gate count at moderate space | minimum standard-circuit logical space |
| EEA representation | compact branch-history/dialog tape | explicit four-phase quotient state |
| Core space method | delay Bézout work and replay history | share shrinking remainders with growing coefficients |
| Dynamic metadata | compressed ternary history | four coherent length registers and phase state |
| Measurement use | selected flag/predicate cleanup | demolition and recycling of a complete field register |
| Point-add width at `n=256` | about 1192 qubits, paper space variant | 835 qubits |
| Point-add Toffoli at `n=256` | about `2^21.19` excluding lookup window | 70.10 million, about `2^26.06` |
| Full ECDLP table value | `2^26.11` | `2^30.88` |
| Approximation | empirical margins and rare-failure parameters | exact fixed schedule and exact state bounds |
| Benchmark fit | closer to low-Toffoli objective | stronger source of qubit-reduction techniques |

## Important count distinction

The Luo comparison table's `2^30.88` is for the complete signed-window ECDLP circuit. Its 70.10 million count is one controlled point addition. The Schrottenloher comparison-table `2^26.11` is also a complete-ECDLP estimate under that table's conventions. Do not compare a per-addition count to a full-algorithm count.

## Combined design thesis

**[INFERENCE]**

```text
Schrottenloher supplies the low-gate computational core.
Luo supplies aggressive liveness and register-recycling mechanisms.
```

The first hybrid to test is therefore not a four-phase EEA rewrite. It is:

```text
existing low-gate multiplier/inversion
+ whole-register measurement recycling where recoverability holds
+ allocator reuse from explicit lifetime bounds
```

Only if that cannot reduce the peak should location-controlled arithmetic be considered.

Relevant nodes:

- [`luo-hybridization-opportunities.md`](../nodes/luo-hybridization-opportunities.md)
- [`luo-resource-estimates.md`](../nodes/luo-resource-estimates.md)

