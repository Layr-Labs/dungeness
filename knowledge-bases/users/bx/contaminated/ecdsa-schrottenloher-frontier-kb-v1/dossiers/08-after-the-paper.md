---
kind: research-dossier
id: after-the-paper
depends_on:
  - affine-dataflow-frontier
  - history-information-channel
  - recurrence-redesign
  - replay-linear-compiler
  - reduction-regimes
  - measurement-phase-economy
  - space-is-a-schedule
---

# Dossier: what to do after the paper works

A valid implementation of history, replay, pseudo-Mersenne arithmetic, and
measurement cleanup is a milestone, not a proof of local optimality.

## Perform a frontier reset

Classify the current candidate:

```text
architecture copied from paper?
recurrence copied from paper?
history alphabet copied from paper?
replay factorization copied from paper?
arithmetic exactness boundaries copied from companion code?
cleanup boundaries copied from primitive APIs?
schedule copied from phase order?
```

Every “yes” is a remaining research axis.

## Generate three non-overlapping hypotheses

Choose one from each column:

| Representation | Algebra | Schedule |
|---|---|---|
| change recurrence symbol | fuse replay operations | interleave walk/replay |
| change sign convention | absorb modular correction | phase-specific adders |
| recompute instead of retain | recode controlled branch | release exact-prefix scratch |

Do not spend the entire remaining budget tuning one width or iteration constant.

## Evidence of deeper research

A trajectory has moved beyond paper implementation when it validates a change
to at least one of:

- the state representation;
- the recurrence;
- the replay matrix factorization;
- the placement of exact versus approximate arithmetic;
- the cross-phase lifetime schedule.

Parameter tuning can improve score, but it is weaker evidence of a new research
direction.

## Stopping test

Before finalizing, answer:

```text
Which materially different frontier was tested after the first strong valid
paper-derived candidate?
What decisive result accepted or rejected it?
How much budget remains?
```

If no frontier was tested and substantial budget remains, return to
`frontier-map.md`.
