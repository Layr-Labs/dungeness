---
kind: node
id: adder-tradeoffs
source: paper section 4
---

# Adder tradeoffs

Approximate paper costs:

| Primitive | Toffolis | Ancillas |
|---|---:|---:|
| CDKM add/compare | `2n` | almost none |
| CDKM controlled add | `3n` | almost none |
| Gidney add | `n` | about `n` |
| Gidney controlled add | `2n` | about `n` |

Selection rule:

- use Gidney or hybrid adders where phase-local workspace is available;
- use CDKM and low-space constant arithmetic during the replay peak.

Used by:

- [`euclid-history.md`](euclid-history.md)
- [`bezout-replay.md`](bezout-replay.md)
- [`resource-estimates.md`](resource-estimates.md)
