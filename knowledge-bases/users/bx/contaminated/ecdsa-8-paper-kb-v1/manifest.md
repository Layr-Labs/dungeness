# KB manifest

## Coverage

```text
papers:              8
paper-section notes: 29
atomic concept nodes: 80
concept syntheses:   24
source records:      11
```

The source-record count includes two companion-code maps and one live-benchmark architecture record in addition to the eight papers.

## Paper-to-node coverage

| Paper | Atomic nodes | Main decomposition |
|---|---:|---|
| Schrottenloher | 22 | point-add shell, Euclid history, replay, arithmetic, approximation, resources |
| Litinski | 5 | controlled add-subtract, correction algebra, multipliers, transfer |
| Luongo et al. | 5 | MBU lemma, expected cost, modular shells, transfer |
| Gidney | 7 | redundant carries, venting, repair, borrowing, controls, transfer |
| Spooky Pebbling | 5 | ghosts, line frontier, computation, DAG/tree, ping-pong scheduling |
| Luo et al. | 18 | shared EEA, active windows, location control, demolition, resources, transfer |
| Khattar et al. | 8 | explicit/implicit access, quotient sharing, Dialog, direct division, transfer |
| Häner et al. | 10 | Montgomery arithmetic, fusion, pebbling, inversion, point-add shell, resources |

## Source artifacts inspected

```text
2606.02235.pdf
2410.00899-litinski.pdf
2407.20167-luongo.pdf
2507.23079-gidney.pdf
2110.08973-spooky.pdf
2607.13816v2-luo.pdf
2510.10967-khattar.pdf
2020-077-haner.pdf
```

Text extraction was checked against representative rendered pages containing circuit diagrams, algorithms, or resource tables. The KB paraphrases the sources and records formulas needed for retrieval; it does not reproduce the papers.

## Evidence integrity

- Direct claims and reported resources use **[PAPER]**.
- Companion implementation observations use **[CODE]**.
- Local evaluator/source/trusted-run facts use **[BENCHMARK]**.
- Rankings, compatibility judgments, and proposed ports use **[INFERENCE]**.

## Validation

- All relative Markdown links resolve.
- Every new paper has a source record, section-level notes, and atomic nodes.
- Current benchmark guidance points to ping-pong walk/replay, not the superseded legacy path.
- The unified KB has one top-level agent pack and one index.
