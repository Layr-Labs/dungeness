# History and Bézout representations

## Four designs

### Current ping-pong

One sign bit per round, replayed later.

### Schrottenloher

Two branch predicates per binary-Euclid step, compressed across groups of iterations, then replayed as linear Bézout updates.

### Luo

Explicit EEA values share two large work registers; quantum length registers select active windows.

### Khattar

Either store quotients inside shrinking polynomial state or store a Dialog of small transition matrices.

## Conservation principle

Reversibility requires enough information to identify the path or reproduce its action. It may live in:

```text
branch tape
quotient digits
explicit coefficients
transition matrices
measurement outcomes plus phase oracle
recomputed checkpoints
```

Deleting one form is valid only after proving another form contains the same needed information.

## Research question

Can the ping-pong recurrence be changed so a smaller transition symbol is sufficient, without increasing per-round arithmetic enough to lose the score product?
