---
kind: research-dossier
id: history-information-channel
depends_on: [affine-dataflow-frontier]
---

# Dossier: history is an information channel

## Paper representation

**[PAPER]** A fixed binary-Euclid iteration begins with `(u,v)=(p,x)` and
records predicates sufficient to reverse the branch:

```text
b0 = v mod 2
b1 = u > v
record b0 and (b0 & b1)
if b0 & b1: swap(u,v)
if b0:      v -= u
v >>= 1
```

Replay later applies a linear action to modular coefficient registers. The
reverse walk restores the denominator and clears the history.

## Conservation law

Reversibility requires enough surviving information to distinguish reachable
preimages. That information need not remain in the paper's exact bit layout.
It may be represented by:

```text
branch symbols
sign symbols
quotient digits
transition matrices
recomputable state
measurement outcomes plus phase correction
```

Only the first representation is supplied by the paper.

## Why compression is not the only question

Compressing the existing symbols preserves the existing recurrence. A more
fundamental possibility is to change the recurrence so that:

- fewer branch cases are reachable;
- one branch predicate becomes algebraically implicit;
- the same symbol controls both walk and replay;
- the post-step state exposes a reversible relation absent from the original
  recurrence.

## Required proof before deleting information

For each candidate symbol alphabet:

1. Enumerate all reachable small-width states.
2. Map every pre-state, symbol, and post-state.
3. Check whether post-state plus symbol uniquely recovers pre-state.
4. Check whether the symbol also determines the replay action.
5. Count the arithmetic required to compute and erase the symbol.

## Decisive experiment

Use widths 4 through 12 and exhaust all odd moduli and valid operands. Compare:

```text
bits recorded per round
Toffoli-like Boolean operations per round
number of rounds
coefficient replay operations
```

A smaller symbol that requires a much more expensive round may lose the score
product; evaluate the combined walk-plus-replay cell.
