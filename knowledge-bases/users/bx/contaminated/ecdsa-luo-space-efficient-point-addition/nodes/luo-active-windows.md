---
kind: node
id: luo-active-windows
source: arXiv:2607.13816v2 section 4.2 and appendix A.2
depends_on: [luo-uniform-step-bound, luo-length-registers]
related: [luo-unary-iteration, luo-location-controlled-add-sub, luo-dirty-length-update]
---

# Step-dependent active windows

**[PAPER]** For each global step `T`, the possible physical locations of an operation are bounded over all valid inputs:

```text
k_j(T) <= selected index or endpoint <= K_j(T)
```

The paper derives separate windows for:

```text
j=1: r-side add/subtract
j=2: quotient-bit swap
j=3: t-side add/subtract
j=4: ell_t update
j=5: ell_r' update
```

Examples:

```text
r-side upper endpoint: K1(T) = n+3
swap upper endpoint:   K2(T) = min(floor(T/2)+2, n+2)
t-side upper endpoint: K3(T) = min(ceil(T/4)+1, n+1)
```

The lower bounds use the uniform-growth constants:

```text
c = 3/log2(2+sqrt(3))
delta ≈ 0.726208
```

Only wires in `[k_j(T),K_j(T)]` need selection circuitry. The actual location remains coherent and is selected by a length register.

**[INFERENCE]** Even without porting the paper's adders, these bounds suggest step-indexed liveness metadata that can shrink a compiler's live ranges and expose dirty scratch regions.

