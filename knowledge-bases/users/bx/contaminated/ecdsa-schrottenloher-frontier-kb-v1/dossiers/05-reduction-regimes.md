---
kind: research-dossier
id: reduction-regimes
depends_on: [replay-linear-compiler]
---

# Dossier: modular reduction has several regimes

## Prime structure

**[PAPER]**

```text
p = 2^256 - f
f = 2^32 + 977
2^256 == f mod p
```

An overflow can therefore be folded by adding `f` into a bounded low slice.

## Fast regime

For ordinary additions:

```text
compute 256-bit sum and carry
if carry: add f to low bits
erase carry from an output relation or truncated comparison
```

For doubling:

```text
shift through an overflow bit
if overflow: add f to a low slice
erase overflow from a deterministic relation
```

## Exceptional regime

**[PAPER/CODE]** Overflow folding alone does not canonicalize an exact sum of
`p` to zero. Early replay states can create this relation. The companion
implementation therefore retains a more exact prefix before using the cheaper
bulk path.

## Research frontier

The useful question is not simply “exact or approximate?” It is:

```text
which state regimes can produce equality with p?
which rounds can produce a long carry?
which output relation is cheapest for flag erasure?
can a neighboring replay operation absorb the correction?
```

**[INFERENCE]** Different replay symbols may admit different correction
circuits. A single generic modular-add routine can hide repeated special cases
that could be compiled away.

## Safe experiment ladder

1. Exact full-width arithmetic.
2. Exact pseudo-Mersenne fold.
3. Separate exceptional-prefix and bulk routines.
4. Bounded low-slice carry propagation.
5. Truncated flag comparison.
6. Reduced prefix length or margins.

After every step run the complete benchmark; a local random arithmetic test is
not enough to establish phase-clean reversible behavior.
