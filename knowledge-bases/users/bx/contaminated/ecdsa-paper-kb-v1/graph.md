# Knowledge graph

## Main dependency path

```text
secp256k1-prime
  -> pseudo-mersenne-doubling
  -> pseudo-mersenne-controlled-addition
  -> bezout-replay

shor-point-multiplication
  -> windowed-point-addition
  -> affine-point-addition
  -> in-place-modular-multiplication

euclid-history
  -> register-sharing
  -> history-compression
  -> bezout-replay
  -> in-place-modular-multiplication

adder-tradeoffs
  -> euclid-history
  -> bezout-replay

approximate-comparison
  -> euclid-history
  -> generic-modular-doubling
  -> generic-controlled-modular-addition
  -> pseudo-mersenne-controlled-addition

implementation-parameters
  -> failure-model
  -> euclid-history
  -> register-sharing
  -> approximate-comparison
  -> x-plus-y-equals-p

in-place-modular-multiplication
  -> resource-estimates
  -> cost-hotspots
  -> benchmark-adaptation
```

## Node catalog

### Algorithm hierarchy

- [`nodes/shor-point-multiplication.md`](nodes/shor-point-multiplication.md)
- [`nodes/windowed-point-addition.md`](nodes/windowed-point-addition.md)
- [`nodes/affine-point-addition.md`](nodes/affine-point-addition.md)
- [`nodes/in-place-modular-multiplication.md`](nodes/in-place-modular-multiplication.md)

### Euclid/dialog architecture

- [`nodes/euclid-history.md`](nodes/euclid-history.md)
- [`nodes/register-sharing.md`](nodes/register-sharing.md)
- [`nodes/history-compression.md`](nodes/history-compression.md)
- [`nodes/bezout-replay.md`](nodes/bezout-replay.md)

### Arithmetic

- [`nodes/adder-tradeoffs.md`](nodes/adder-tradeoffs.md)
- [`nodes/approximate-comparison.md`](nodes/approximate-comparison.md)
- [`nodes/generic-modular-doubling.md`](nodes/generic-modular-doubling.md)
- [`nodes/pseudo-mersenne-doubling.md`](nodes/pseudo-mersenne-doubling.md)
- [`nodes/generic-controlled-modular-addition.md`](nodes/generic-controlled-modular-addition.md)
- [`nodes/pseudo-mersenne-controlled-addition.md`](nodes/pseudo-mersenne-controlled-addition.md)
- [`nodes/x-plus-y-equals-p.md`](nodes/x-plus-y-equals-p.md)
- [`nodes/measurement-based-uncomputation.md`](nodes/measurement-based-uncomputation.md)
- [`nodes/secp256k1-prime.md`](nodes/secp256k1-prime.md)

### Evidence and use

- [`nodes/implementation-parameters.md`](nodes/implementation-parameters.md)
- [`nodes/failure-model.md`](nodes/failure-model.md)
- [`nodes/resource-estimates.md`](nodes/resource-estimates.md)
- [`nodes/cost-hotspots.md`](nodes/cost-hotspots.md)
- [`nodes/benchmark-adaptation.md`](nodes/benchmark-adaptation.md)
