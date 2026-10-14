# Approximate arithmetic

## Paper mechanisms

Schrottenloher reduces cost by:

- fixing an iteration budget with a statistical tail margin;
- shrinking active Euclidean slices according to a width model;
- comparing only high-order bits where near-equality is unlikely;
- limiting pseudo-Mersenne carry propagation to a retained low slice.

These mechanisms trade exact worst-case coverage for a quantified source
distribution.

## Obligations

Every approximation needs:

```text
failure event
retained margin
input distribution
interaction with reversibility
interaction with exceptional arithmetic cases
```

The equality `x+y=p` is structurally possible during an early replay prefix and
is handled separately by the paper.

## Nodes

- [`../nodes/approximate-comparison.md`](../nodes/approximate-comparison.md)
- [`../nodes/failure-model.md`](../nodes/failure-model.md)
- [`../nodes/x-plus-y-equals-p.md`](../nodes/x-plus-y-equals-p.md)
- [`../nodes/paper-parameter-boundaries.md`](../nodes/paper-parameter-boundaries.md)
