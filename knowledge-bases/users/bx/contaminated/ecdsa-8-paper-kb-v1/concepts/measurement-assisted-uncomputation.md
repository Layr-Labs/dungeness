# Measurement-assisted uncomputation

## Shared pattern

Luongo MBU, Gidney carry venting, Luo register demolition, and Spooky ghosting all perform:

```text
measure obsolete Z-basis information in X basis
store classical outcome
release qubit
later reconstruct a phase predicate
apply outcome-controlled phase correction
uncompute reconstruction
```

## Scale differences

| Mechanism | Measured object | Repair predicate |
|---|---|---|
| Luongo | one Boolean garbage bit | original Boolean function |
| Gidney | stream of carries | carry pattern from final sum |
| Luo | full field register | complete deleted field value |
| Spooky | computation checkpoint | checkpoint state from predecessors |

Larger objects are not free: they produce more classical outcomes and potentially expensive phase reconstruction.

## Benchmark protocol

1. retain each outcome through the inverse;
2. test superpositions;
3. remove one correction and require failure;
4. verify conditional executed-cost accounting;
5. verify max-ID reduction occurs before added repair workspace.
