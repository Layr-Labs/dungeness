# Unified ECDSA.fail Research Knowledge Base

This is one consolidated, implementation-oriented knowledge base built from eight papers that approach low-resource elliptic-curve or reversible arithmetic from deliberately different directions.

The KB is not a stack of paper summaries. Each source is decomposed into small, retrievable concepts, then connected to the current `ecdsa.fail` point-addition architecture and to the other papers.

## The eight papers

| # | Source | Primary dimension | Role in this KB |
|---:|---|---|---|
| 1 | Schrottenloher, arXiv:2606.02235 | compact Euclid history and Bézout replay | closest architectural match |
| 2 | Litinski, arXiv:2410.00899 | cheaper controlled addition and schoolbook multiplication | arithmetic component donor |
| 3 | Luongo et al., arXiv:2407.20167 | measurement-based uncomputation | dynamic-circuit cleanup framework |
| 4 | Gidney, arXiv:2507.23079 | constant-workspace classical adders | ancilla and controlled-arithmetic donor |
| 5 | Kornerup, Sadun, and Soloveichik, arXiv:2110.08973v3 | spooky pebbling | time–space scheduling theory |
| 6 | Luo et al., arXiv:2607.13816v2 | very low-space EEA and measured register recycling | space-minimizing reference |
| 7 | Khattar et al., arXiv:2510.10967 | explicit, implicit, and dialog EEA representations | alternative history representation |
| 8 | Häner et al., ePrint 2020/077 | integrated ECDLP arithmetic and scheduling | established baseline and control |

## Start here

- [`agent-pack.md`](agent-pack.md) — compact unified brief for an implementation agent.
- [`index.md`](index.md) — complete paper, concept, node, and source navigation.
- [`paper-matrix.md`](paper-matrix.md) — what each paper contributes, overlaps with, and cannot directly replace.
- [`experiment-map.md`](experiment-map.md) — ranked experiments for the current benchmark architecture.
- [`graph.md`](graph.md) — cross-paper mechanism and dependency graph.
- [`manifest.md`](manifest.md) — coverage and source-traceability record.
- [`AGENTS.md`](AGENTS.md) — operating and evidence rules.

The versioned Dungeness reference for this corpus is
`knowledge-base:users/bx/contaminated/ecdsa-8-paper-kb-v1`.

## Organization

- [`sections/`](sections/) follows the eight papers in source order.
- [`nodes/`](nodes/) contains atomic algorithms, claims, cost formulas, caveats, and transfer hypotheses.
- [`concepts/`](concepts/) synthesizes mechanisms across papers.
- [`sources/`](sources/) records provenance, reported resources, and transfer limitations.

## Evidence labels

- **[PAPER]** A claim, construction, or number reported by a paper.
- **[CODE]** A fact recovered from a pinned companion implementation.
- **[BENCHMARK]** A fact from the local benchmark contract, source tree, or trusted run.
- **[INFERENCE]** A proposed connection, port, ranking, or experiment that still requires testing.

Do not blend these labels. In particular, a paper resource table is not an `ecdsa.fail` score.

## Current benchmark context

**[BENCHMARK]** The local implementation uses a fixed-depth ping-pong division/multiplication architecture with a signed binary-GCD-style walk, a stored sign/history tape, coefficient replay, and a reverse walk. The replay/tape interval owns the global peak. The objective is:

```text
score = average executed Toffoli × (maximum referenced qubit id + 1)
```

Only a passing untouched full benchmark establishes a valid score. The current architecture is newer than the dialog/trailmix architecture described by some older local notes, so this KB treats those notes as historical rather than binding.

## Recommended reading path

1. [`concepts/benchmark-contract.md`](concepts/benchmark-contract.md)
2. [`concepts/current-benchmark-architecture.md`](concepts/current-benchmark-architecture.md)
3. [`paper-matrix.md`](paper-matrix.md)
4. [`concepts/mechanism-selection.md`](concepts/mechanism-selection.md)
5. [`experiment-map.md`](experiment-map.md)
6. The nodes for the exact peak interval or primitive being changed

## Central conclusion

**[INFERENCE]** No paper should be transplanted wholesale. The strongest program is:

```text
current ping-pong walk/replay architecture
  + proven secp256k1 arithmetic improvements
  + phase-correct measurement cleanup where supported
  + schedule-specific tape/replay interleaving
  + explicit information-recovery proofs for any history compression
```

The KB records both promising transfers and known incompatibilities so an agent does not repeatedly rediscover the same dead ends.
