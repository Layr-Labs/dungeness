# Euclid history tape

Each binary-Euclid step records one of three reachable symbols:

```text
(0,0), (1,0), (1,1).
```

Three symbols therefore have 27 reachable patterns. Schrottenloher uses a
reversible five-bit block code instead of six raw bits.

For a fixed iteration count `L` divisible by three:

```text
tape size = 5L/3.
```

The tape grows while the Euclidean values shrink, allowing shared physical
storage. During replay, the complete tape coexists with two field registers
and becomes the leading space term.

## Design boundary

The block code is local and cheaply reversible, but it is not the
information-theoretic minimum. A replacement must preserve:

- fixed allocation;
- forward and reverse streaming;
- exact action on every reachable symbol block;
- compatible replay order.
