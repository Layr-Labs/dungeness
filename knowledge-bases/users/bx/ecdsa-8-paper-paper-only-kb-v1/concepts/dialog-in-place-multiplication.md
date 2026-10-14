# Transcript replay and in-place multiplication

## Construction

Schrottenloher separates:

1. branch discovery on `(p,x)`;
2. compact storage of the branch sequence;
3. linear replay on `(y,0)`;
4. reversal of branch discovery.

The resulting interface is:

```text
|x>|y> -> |x>|xy mod p>.
```

The inverse circuit divides by `x`.

## Why replay works

Each retained symbol selects a linear update of a two-component coefficient
vector. Initializing the vector with arbitrary `y` applies the same accumulated
Euclidean transformation to `y`.

## Related representations

- Khattar's Dialog also stores a sequence of invertible linear transitions.
- Luo stores explicit EEA values in shared moving ranges instead of a compact
  branch transcript.
- Häner retains Kaliski round controls and schedules correction during reverse
  traversal.

## Nodes

- [`../nodes/euclid-history.md`](../nodes/euclid-history.md)
- [`../nodes/history-compression.md`](../nodes/history-compression.md)
- [`../nodes/bezout-replay.md`](../nodes/bezout-replay.md)
- [`../nodes/in-place-modular-multiplication.md`](../nodes/in-place-modular-multiplication.md)
