---
kind: node
id: haner-signed-windowing
source: IACR ePrint 2020/077, section 5
---

# Signed windowing

Signed digits reduce the number of scalar-multiplication point additions. A window index addresses a sequential quantum lookup of a precomputed classical point.

This mechanism belongs to full Shor scalar multiplication. The benchmark supplies one runtime classical offset point, so the lookup wrapper does not transfer directly.
