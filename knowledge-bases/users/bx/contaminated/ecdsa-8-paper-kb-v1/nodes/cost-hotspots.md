---
kind: node
id: cost-hotspots
source: paper Table 3
---

# Cost hot spots

Space-optimized secp256k1:

| Component | CCX share |
|---|---:|
| in-place multiplier and inverse | 90% |
| Bézout replay | 54% |
| history/GCD construction | 36% |
| controlled modular add/inverse | 39% |
| hybrid adder | 22% |
| controlled swaps | 19% |
| constant adders | 15% |
| modular square | 9% |
| double/inverse | 8% |

Rows overlap because some are nested subcomponents.

Optimization order:

```text
replay add -> history adder -> swaps -> constants -> double -> square -> codec
```

Generic-prime circuits spend substantially more on full-width constant adders and modular double.
