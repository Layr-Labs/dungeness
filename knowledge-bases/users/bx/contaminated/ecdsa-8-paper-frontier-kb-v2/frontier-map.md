# Decision frontier map

The eight papers are coordinates in a design space, not eight complete
solutions to average together.

| Decision axis | Main evidence | What changes | Primary liability |
|---|---|---|---|
| Information location | Schrottenloher, Luo, Khattar, Spooky Pebbling | branch tape, redundant state, algebraic dialogue, classical phase debt | cleanup and retained-information contract |
| Recurrence/state machine | Schrottenloher, Luo, Khattar, Häner | binary EEA, fixed four-phase EEA, synchronized transition matrices, Kaliski | field and quotient/sign transfer |
| Arithmetic control | Litinski, Gidney, Luongo, Luo, Schrottenloher | add-subtract structure, carry venting, MBU, active windows, special modulus | ancilla/control/cleanup mismatch |
| Field representation | Schrottenloher, Litinski, Häner | canonical pseudo-Mersenne, Montgomery, redundant or pseudo-inverse forms | conversions and equality semantics |
| Output placement | Schrottenloher, Litinski, Luo, Häner | in-place replay, fresh accumulator, register demolition, affine shell reuse | peak live width and reverse path |
| Measurement scale | Luongo, Gidney, Luo, Spooky Pebbling | one flag, carry structure, full register, arbitrary checkpoint | phase repair and expected execution cost |
| Space-time schedule | Schrottenloher, Luo, Spooky Pebbling, Häner | register sharing, active windows, checkpoint schedule, global pebbling | recomputation and hard-ID timing |
| Composition | all | mechanism graft across papers | hidden interface tax |

## Choose from measured owners

| Observation | First dossier | Secondary evidence |
|---|---|---|
| History/transcript owns Q | [`01-information-location.md`](dossiers/01-information-location.md) | Schrottenloher, Luo, Khattar |
| EEA loop owns T | [`02-recurrence-state-machine.md`](dossiers/02-recurrence-state-machine.md) | Schrottenloher, Luo, Khattar, Häner |
| Controlled constant arithmetic repeats | [`03-arithmetic-control-structure.md`](dossiers/03-arithmetic-control-structure.md) | Gidney, Luongo, Litinski |
| Reduction/equality corrections repeat | [`04-field-representation-and-reduction.md`](dossiers/04-field-representation-and-reduction.md) | Schrottenloher, Litinski, Häner |
| Product/result registers create peak | [`05-output-placement-and-affine-dataflow.md`](dossiers/05-output-placement-and-affine-dataflow.md) | Litinski, Luo, Häner |
| Cleanup is expensive or blocks deletion | [`06-measurement-scale.md`](dossiers/06-measurement-scale.md) | Luongo, Gidney, Luo, Spooky |
| A short interval creates hard max ID | [`07-space-time-schedule.md`](dossiers/07-space-time-schedule.md) | Schrottenloher, Luo, Spooky |
| Imported idea appears cheap in isolation | [`08-transfer-barriers.md`](dossiers/08-transfer-barriers.md) | all paper cards |
| One compatible bridge is ready to test | [`09-cross-paper-compositions.md`](dossiers/09-cross-paper-compositions.md) | linked pairs |
| Current paper has been implemented | [`10-after-the-baseline.md`](dossiers/10-after-the-baseline.md) | untouched-axis protocol |

## Source depth

Each dossier links to operational cards under `evidence/papers/`. Those cards
link to exact page files under `source-pages/`. The complete source index is
[`evidence/source-index.md`](evidence/source-index.md).

If a proposed experiment cannot be stated with an explicit forward and reverse
contract after reading those layers, it is not ready to implement.
