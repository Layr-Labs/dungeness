---
kind: research-dossier
id: after-the-baseline
depends_on:
  - recurrence-state-machine
  - field-representation-and-reduction
  - cross-paper-compositions
---

# Dossier: what to do after a paper-derived baseline works

A strong implementation can look complete because its source paper reaches a
clean conclusion. That is a property of the exposition, not evidence that the
benchmark design space is exhausted.

## Perform a cross-paper frontier reset

Classify every major choice:

```text
information medium copied from which paper?
recurrence copied from which paper?
arithmetic control contract copied from which paper?
field representation copied from which paper?
output placement copied from which paper?
measurement boundary copied from which paper?
schedule copied from which paper?
```

For each answer, name a different paper that exposes an incompatible
alternative. The conflict itself is a hypothesis source.

## Generate a three-axis portfolio

| Representation | Algebra | Schedule/cleanup |
|---|---|---|
| branch tape -> transition record | fuse add/subtract with fold | active-window scratch |
| explicit coefficient -> implicit action | consumer-specific multiply-add | weighted history interleaving |
| coherent state -> recomputable ghost | postpone canonicalization | demolish one obsolete register |
| new recurrence symbol | direct division dataflow | phase-specific workspace class |

Choose one row entry from each column. Do not spend all remaining work tuning a
single padding, window, or iteration constant.

## Evidence that research moved beyond a paper

A validated transformation changes at least one of:

- state representation;
- recurrence or transition alphabet;
- replay matrix factorization;
- arithmetic control contract;
- output placement;
- exactness or reduction boundary;
- coherent-versus-classical information boundary;
- cross-phase lifetime schedule.

Parameter tuning can improve score, but it is weaker evidence of a new
direction.

## Stop a branch versus stop the search

Stop a branch when:

```text
inverse collisions occur
the bridge contract is false
closed-shell cost loses decisively
phase mutation tests fail
the predicted hard-ID saving is physically absent
```

Stop the overall search only after:

```text
at least one materially different representation hypothesis was tested
at least one algebraic composition was tested
at least one schedule or measurement hypothesis was tested
their decisive outcomes were recorded
remaining budget cannot support another meaningful falsifier
```

## Final continuation question

Before finalizing, answer:

```text
Which conclusion came from the current evidence?
Which conclusion was merely inherited from the last paper implemented?
Which untouched cross-paper conflict could still change the architecture?
```

If the last question has a concrete answer and useful budget remains, return to
[`frontier-map.md`](../frontier-map.md).
