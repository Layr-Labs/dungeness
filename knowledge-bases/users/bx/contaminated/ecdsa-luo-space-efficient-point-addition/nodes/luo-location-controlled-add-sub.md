---
kind: node
id: luo-location-controlled-add-sub
source: arXiv:2607.13816v2 section 4.1 and Figures 9-11
depends_on: [luo-unary-iteration, luo-shared-work-registers]
related: [luo-active-windows, luo-optimized-eea-step]
---

# Location-controlled addition and subtraction

**[PAPER]** The endpoints and alignment of both operands are encoded in length registers. The circuit combines:

- unary selection of the active start or endpoint;
- ripple majority/unmajority arithmetic cells;
- phase and sign controls;
- the circular interpretation of `Work2`.

Per active span, the paper reports:

```text
r-side add/sub:
  11(K1-k1) Toffolis
  12(K1-k1) CNOTs

t-side add/sub:
   9(K3-k3) Toffolis
  10(K3-k3) CNOTs
```

`r`-side operations act between:

```text
ell_t + ell_q + 2
and
n + 3 - ell_s
```

`t`-side operations act on the first `ell_t+1` positions, interpreted with the shifted/wrapped `t'`.

These gates are the price of storing multiple logical values in position-varying shared registers. A port should compare the width saved against the added selection and ripple cost.

