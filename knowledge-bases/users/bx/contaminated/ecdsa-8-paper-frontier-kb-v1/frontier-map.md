# Cross-paper research frontier

Choose by the current uncertainty, not by paper order.

| Current question | Dossier | Main score axis |
|---|---|---|
| Where should the information needed for reversibility live? | [`01-information-location.md`](dossiers/01-information-location.md) | Q and reconstruction T |
| Should the EEA recurrence change before its state is compressed? | [`02-recurrence-state-machine.md`](dossiers/02-recurrence-state-machine.md) | T and Q |
| Which arithmetic primitive matches the actual control contract? | [`03-arithmetic-control-structure.md`](dossiers/03-arithmetic-control-structure.md) | repeated T and scratch |
| Which residue and reduction regime should cross phase boundaries? | [`04-field-representation-and-reduction.md`](dossiers/04-field-representation-and-reduction.md) | T and correctness |
| Where should division, multiplication, and affine results land? | [`05-output-placement-and-affine-dataflow.md`](dossiers/05-output-placement-and-affine-dataflow.md) | Q and cleanup T |
| How large an object is economical to measure and phase-repair? | [`06-measurement-scale.md`](dossiers/06-measurement-scale.md) | expected T and Q |
| Can the peak be changed by scheduling rather than local gates? | [`07-space-time-schedule.md`](dossiers/07-space-time-schedule.md) | hard Q for added T |
| What must be proved before a paper result transfers? | [`08-transfer-barriers.md`](dossiers/08-transfer-barriers.md) | validity |
| Which mechanisms compose, and which duplicate the same cost? | [`09-cross-paper-compositions.md`](dossiers/09-cross-paper-compositions.md) | architectural gain |
| What should happen after a strong paper-derived baseline? | [`10-after-the-baseline.md`](dossiers/10-after-the-baseline.md) | research depth |

## Dependency loops worth exploiting

```text
recurrence
  -> determines lost information
  -> determines history/dialog representation
  -> determines replay arithmetic
  -> determines tape width and schedule

output placement
  -> determines which old value is obsolete
  -> determines whether measurement is useful
  -> determines the phase-repair predicate
  -> determines when workspace can be reused

field representation
  -> determines correction algebra
  -> determines whether Litinski-style add/subtract can fuse
  -> determines which Gidney constant offsets apply
  -> determines canonicalization and exceptional cases
```

An optimization that improves one box but forces a more expensive neighboring
box is not a cross-paper synthesis.
