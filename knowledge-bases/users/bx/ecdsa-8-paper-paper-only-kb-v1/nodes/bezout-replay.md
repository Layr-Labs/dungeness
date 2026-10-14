---
kind: node
id: bezout-replay
source: paper section 3.2, Algorithm 3
depends_on: [euclid-history, history-compression]
---

# Bézout replay

Read history in reverse. For each symbol:

```text
s <- 2s mod p
if b0:      s <- s+r mod p
if b0&b1:   swap(r,s)
```

The updates are linear. Starting from `(y,0)` applies the Euclid-derived linear map directly to `y`.

In the traversal convention stated by the paper:

```text
(y,0) -> (0,xy mod p)
```

The inverse circuit multiplies by `x^-1`.

Replay is the peak-space phase because it holds:

```text
history tape + r + s + arithmetic workspace
```

Arithmetic dependencies:

- [`pseudo-mersenne-doubling.md`](pseudo-mersenne-doubling.md)
- [`pseudo-mersenne-controlled-addition.md`](pseudo-mersenne-controlled-addition.md)
- [`x-plus-y-equals-p.md`](x-plus-y-equals-p.md)
