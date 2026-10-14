---
kind: node
id: luo-location-controlled-swap
source: arXiv:2607.13816v2 section 4.1 and Figure 8
depends_on: [luo-unary-iteration, luo-length-registers]
related: [luo-optimized-eea-step]
---

# Location-controlled swap

**[PAPER]** The current quotient-bit position is:

```text
ell_t + ell_q + 1
```

The circuit swaps `Sign` with that selected `Work1` qubit under phase control. Unary iteration restricts selection to the current active window.

For a window `[k,K]`, the dominant reported cost is:

```text
2(K-k) Toffolis
4(K-k) CNOTs
```

Algorithm 3 merges the separate phase-2 and phase-3 swaps because they target the same physical location. The direction of the corresponding `ell_q` update is selected by `Phase1`.

**[INFERENCE]** The general pattern is useful whenever a moving boundary carries one state bit: merge read and erase operations at the boundary before optimizing their selector.

