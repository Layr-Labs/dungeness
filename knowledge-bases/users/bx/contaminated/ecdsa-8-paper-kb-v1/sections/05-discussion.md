---
kind: section
paper_section: 5
title: Discussion and cost concentration
---

# Section 5 — Discussion and cost concentration

## Main conclusion

The difference between secp256k1 and a generic prime comes almost entirely from modular addition/doubling and, more specifically, replacing full-modulus constant arithmetic with low-bit additions of `f`.

## Cost breakdown

| Component | secp256k1 | generic prime |
|---|---:|---:|
| Modular squaring | 9% | 10% |
| In-place multiplier and inverse | 90% | 90% |
| Bézout replay | 54% | 64% |
| GCD/history construction | 36% | 24% |
| Controlled swap | 19% | 12% |
| Hybrid adder | 22% | 14% |
| Controlled modular add/inverse | 39% | 45% |
| Modular double/inverse | 8% | 24% |
| Constant adders | 15% | 34% |

Percentages overlap because some rows are subcomponents of others.

## Optimization priority

After implementing the architecture:

1. controlled modular add in replay;
2. history subtraction/hybrid adder;
3. controlled swaps;
4. constant arithmetic;
5. modular double;
6. squaring;
7. tape-codec fusion.

## Nodes

- [`../nodes/resource-estimates.md`](../nodes/resource-estimates.md)
- [`../nodes/cost-hotspots.md`](../nodes/cost-hotspots.md)
- [`../nodes/secp256k1-prime.md`](../nodes/secp256k1-prime.md)
- [`../nodes/benchmark-adaptation.md`](../nodes/benchmark-adaptation.md)
