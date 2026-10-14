---
kind: section
paper_section: 4
title: Approximate arithmetic and modular arithmetic
---

# Section 4 — Approximate arithmetic and modular arithmetic

## Three optimization layers

1. Choose exact arithmetic primitives based on available ancillas.
2. Truncate comparisons to high bits.
3. Specialize reduction to the pseudo-Mersenne secp256k1 prime.

## Adder tradeoff

```text
CDKM addition:            ~2n Toffolis, almost no ancillas
CDKM controlled addition: ~3n Toffolis
Gidney addition:          ~n Toffolis, ~n ancillas
Gidney controlled add:    ~2n Toffolis, ~n ancillas
```

The paper uses Gidney/hybrid arithmetic when workspace is available and CDKM/low-space constant arithmetic at the replay peak.

## Approximate comparison

Compare only 40-50 most significant bits when the probability of a near-equality is sufficiently small. This affects Euclid branch choice and modular reduction flags.

## Generic modular arithmetic

- modular double: shift, approximate comparison with `p`, controlled subtract;
- controlled modular add: ordinary controlled add, approximate overflow test, controlled subtract `p`, uncompute flag with `result < addend`.

## secp256k1 specialization

```text
p = 2^256 - f
f = 2^32 + 977
```

Overflow can be folded by adding `f` to low bits. Full-width add/subtract by `p` is avoided.

## Exceptional equality

Early replay iterations can produce `x+y=p`, requiring a special controlled adder. Later iterations use a cheaper variant that assumes this equality does not occur.

## Nodes

- [`../nodes/adder-tradeoffs.md`](../nodes/adder-tradeoffs.md)
- [`../nodes/approximate-comparison.md`](../nodes/approximate-comparison.md)
- [`../nodes/generic-modular-doubling.md`](../nodes/generic-modular-doubling.md)
- [`../nodes/pseudo-mersenne-doubling.md`](../nodes/pseudo-mersenne-doubling.md)
- [`../nodes/generic-controlled-modular-addition.md`](../nodes/generic-controlled-modular-addition.md)
- [`../nodes/pseudo-mersenne-controlled-addition.md`](../nodes/pseudo-mersenne-controlled-addition.md)
- [`../nodes/x-plus-y-equals-p.md`](../nodes/x-plus-y-equals-p.md)
- [`../nodes/measurement-based-uncomputation.md`](../nodes/measurement-based-uncomputation.md)
- [`../nodes/failure-model.md`](../nodes/failure-model.md)

## Next section

[`05-discussion.md`](05-discussion.md)
