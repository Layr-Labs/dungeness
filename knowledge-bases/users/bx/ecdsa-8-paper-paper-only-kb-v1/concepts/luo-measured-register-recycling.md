# Measured field-register recycling

Hadamard-basis measurement of a computational-basis field value `y` produces a
classical string `b` and phase:

```text
(-1)^(b dot y).
```

If `y` can later be reconstructed from surviving quantum values, applying
`Z` corrections selected by `b` cancels that phase. The reconstruction can
then be reversed.

## Lifetime effect

Luo et al. use the reset field register as workspace for inverse EEA, avoiding
a fourth field-sized register in in-place multiplication and division.

## Correctness obligations

- exact recoverability of the deleted value;
- preservation of every measurement outcome;
- matching bit order in the phase dot product;
- explicit phase correction;
- explicit inverse protocol;
- cleanup of the reconstruction.

## Nodes

- [`../nodes/luo-hadamard-register-recycling.md`](../nodes/luo-hadamard-register-recycling.md)
- [`../nodes/luo-in-place-division.md`](../nodes/luo-in-place-division.md)
- [`../nodes/luo-in-place-multiplication.md`](../nodes/luo-in-place-multiplication.md)
