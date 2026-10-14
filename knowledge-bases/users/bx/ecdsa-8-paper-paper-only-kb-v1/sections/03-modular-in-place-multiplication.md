---
kind: section
paper_section: 3
title: Modular in-place multiplication
---

# Section 3 — Modular in-place multiplication

## Core transformation

```text
|x>|y> -> |x>|xy mod p>
```

Its inverse multiplies `y` by `x^-1`. The point-add circuit uses both directions.

## Phase A: Euclid history

Run a fixed number of binary Euclid steps on `(p,x)`. Each step records:

```text
b0 = parity(v)
b0_and_b1 = b0 & (u > v)
```

Then conditionally swap, subtract, and divide `v` by two.

## Phase B: history replay

Read the record backwards while updating two modular registers:

```text
s <- 2s
if b0:        s <- s+r
if b0&b1:     swap(r,s)
```

Starting from `(y,0)`, the traversal direction specified in the paper produces
the multiplication action.

## Phase C: restore input

Reverse the Euclid-history circuit to recover `x`, leaving `xy` in place.

## Space mechanisms

- fixed iteration bound;
- shrinking `u,v` register slices;
- reuse cleared high wires as history;
- three iterations compressed from six raw bits to five;
- low-space arithmetic during replay.

## Paper-level sizing

The fixed iteration budget is approximately:

```text
1.413n + O(sqrt(n))
```

and the compressed transcript occupies approximately:

```text
2.355n + O(sqrt(n))
```

## Nodes

- [`../nodes/euclid-history.md`](../nodes/euclid-history.md)
- [`../nodes/register-sharing.md`](../nodes/register-sharing.md)
- [`../nodes/history-compression.md`](../nodes/history-compression.md)
- [`../nodes/bezout-replay.md`](../nodes/bezout-replay.md)
- [`../nodes/in-place-modular-multiplication.md`](../nodes/in-place-modular-multiplication.md)
- [`../nodes/paper-parameter-boundaries.md`](../nodes/paper-parameter-boundaries.md)

## Next section

[`04-approximate-and-modular-arithmetic.md`](04-approximate-and-modular-arithmetic.md)
