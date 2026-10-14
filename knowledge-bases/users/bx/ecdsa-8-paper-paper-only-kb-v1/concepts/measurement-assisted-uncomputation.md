# Measurement-assisted uncomputation

## Shared pattern

Luongo, Gidney, Luo, and Kornerup et al. all use:

```text
measure obsolete computational-basis information in the Hadamard basis
retain a classical outcome
reuse the released qubit
later reconstruct a phase predicate
apply outcome-controlled phase correction
uncompute the reconstruction
```

## Scale

| Source | Measured object | Repair object |
|---|---|---|
| Luongo | one Boolean garbage bit | the Boolean function |
| Gidney | streamed carry bits | the carry pattern |
| Luo | one field register | the complete deleted field value |
| Kornerup et al. | a checkpoint state | the checkpoint reconstructed from dependencies |

Larger measured objects produce larger classical records and potentially more
expensive reconstruction. Measurement changes where reversibility information
is stored; it does not remove that information requirement.
