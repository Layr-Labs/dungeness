# Start: reconstruct, then reopen the problem

The paper's central construction is a strong starting architecture:

```text
affine point-add dataflow
  -> in-place division/multiplication
  -> fixed binary-Euclid history
  -> linear coefficient replay
  -> reverse history cleanup
```

The purpose of this KB is not to stop there.

## Establish the first architecture

The affine formulas are:

```text
lambda = (target_y-offset_y)/(target_x-offset_x) mod p
x3     = lambda^2-target_x-offset_x mod p
y3     = lambda*(target_x-x3)-target_y mod p
```

The paper uses an in-place modular multiplication engine and its inverse so that
division and multiplication share one history/replay mechanism.

For secp256k1:

```text
p = 2^256 - f
f = 2^32 + 977
2^256 == f mod p
```

## Do not inherit the paper's decomposition as fixed

Once a valid version exists, ask which boundary is artificial:

- Must history construction and replay be separate phases?
- Must a round record the paper's exact pair of predicates?
- Must replay be implemented as separate double, add, and swap primitives?
- Must every modular correction use the same exactness regime?
- Must an obsolete Boolean be coherently uncomputed?
- Must point-add follow the paper's exact intermediate representation?

These questions are indexed in [`frontier-map.md`](frontier-map.md).

## Retrieval strategy

Search for the current obstacle:

```text
recover sign branch
fuse replay double add
peak tape coefficients overlap
exceptional x+y=p
measure comparator phase repair
affine slope cleanup identity
```

Read one dossier deeply, implement its smallest decisive experiment, and return
to the map after the result.
