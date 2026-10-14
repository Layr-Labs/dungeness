# Research frontier map

This map is organized by questions whose answers can change the architecture.

| Current question | Dossier | Primary score dimension |
|---|---|---|
| Can the affine shell expose a cheaper intermediate? | [`01-affine-dataflow.md`](dossiers/01-affine-dataflow.md) | T and lifetime |
| Where does reversibility information actually live? | [`02-history-information.md`](dossiers/02-history-information.md) | Q |
| Can the recurrence be redesigned before compressing it? | [`03-recurrence-redesign.md`](dossiers/03-recurrence-redesign.md) | T and Q |
| Can replay operations be fused as one linear cell? | [`04-replay-linear-compiler.md`](dossiers/04-replay-linear-compiler.md) | T |
| Which corrections need exact arithmetic, and when? | [`05-reduction-regimes.md`](dossiers/05-reduction-regimes.md) | T |
| Can measurement replace coherent cleanup safely? | [`06-measurement-phase-economy.md`](dossiers/06-measurement-phase-economy.md) | expected T and Q |
| Can liveness be changed rather than only gate counts? | [`07-space-is-a-schedule.md`](dossiers/07-space-is-a-schedule.md) | Q |
| What should happen after the paper works? | [`08-after-the-paper.md`](dossiers/08-after-the-paper.md) | research depth |

## Interactions worth testing

```text
recurrence redesign
  -> changes history alphabet
  -> changes replay cell
  -> changes tape width and scheduling

replay fusion
  -> changes correction predicates
  -> changes measurement opportunities
  -> changes available scratch at the peak

affine dataflow
  -> changes which operand survives
  -> changes whether multiplication is truly in place
  -> changes cleanup and inverse cost
```

Do not optimize a node in isolation if its output representation forces a more
expensive neighboring step.
