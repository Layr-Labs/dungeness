# Research protocol: turn papers into falsifiable mechanism grafts

The purpose of this KB is not to make the agent recite more papers. It is to
make research transitions cheaper and less directionless.

## 1. Establish a measured baseline

Record:

```text
validity status
average executed Toffoli
maximum referenced qubit ID + 1
score
top three dynamic Toffoli regions
instruction establishing hard maximum ID
values live at that instruction
cleanup protocol active there
```

The T owner and Q owner may be different. Optimize the product, not a paper's
preferred metric.

## 2. Select a representation-level question

A research hypothesis should change at least one meaningful interface:

- where reversible information resides;
- how the recurrence exposes its controls;
- whether output is in-place or fresh;
- which field representation persists globally;
- what scale of state is measured;
- when large registers coexist.

Replacing a gate decomposition inside an unmeasured non-owner is maintenance,
not a frontier experiment.

## 3. Build a compatibility ledger

For the base and graft, fill in:

| Field | Base | Graft | Required bridge |
|---|---|---|---|
| input representation | | | |
| output representation | | | |
| output location | | | |
| classical controls | | | |
| quantum controls | | | |
| clean ancillas | | | |
| dirty ancillas | | | |
| discarded information | | | |
| reverse protocol | | | |
| exceptional cases | | | |
| local cost | | | |
| whole-shell use count | | | |

If the bridge is larger than the graft, test the bridge first.

## 4. Translate cost into the benchmark

Estimate:

```text
delta_T_dynamic =
  forward calls
  + reverse calls
  + expected measurement-repair calls
  + conversions
  + correction arithmetic
  + extra controls

delta_Q_hard =
  change in highest simultaneously referenced allocation,
  not sum of all logical workspace descriptions
```

Then estimate the product at the complete point-addition shell. Reject obvious
losses before building them, but retain uncertain ideas for a small test.

## 5. Run the smallest decisive experiment

Prefer this order:

1. standalone primitive correctness and reverse correctness;
2. representative-width resource measurement;
3. one invocation in the real caller;
4. complete affine shell;
5. full benchmark distribution.

For measurement-assisted methods, include every branch and phase repair in the
test. For representation changes, include entry and exit conversion unless the
representation is intentionally made global.

## 6. Record negative information

A rejected experiment should leave:

```text
hypothesis
measured delta
failure mechanism
scope of rejection
condition under which it may become useful
```

Do not generalize “this bridge lost in one shell” into “this paper is useless.”

## 7. Force a frontier reset

After an accepted improvement or completed paper baseline:

1. recompute owners;
2. mark the axis just explored;
3. select a materially different untouched axis;
4. search the dossiers and source evidence for one mechanism;
5. write the next falsifiable bridge.

Only stop when remaining axes are measured non-owners, decisively rejected,
incompatible under the benchmark contract, or beyond the remaining budget.
