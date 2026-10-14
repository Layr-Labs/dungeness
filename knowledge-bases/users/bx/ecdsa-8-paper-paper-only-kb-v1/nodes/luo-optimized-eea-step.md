---
kind: node
id: luo-optimized-eea-step
source: arXiv:2607.13816v2 Algorithm 3
depends_on: [luo-four-phase-eea, luo-shared-work-registers, luo-length-registers]
related: [luo-location-controlled-swap, luo-location-controlled-add-sub]
---

# Optimized one-step EEA circuit

**[PAPER]** Algorithm 3 merges operations that the direct four-phase realization repeats at phase boundaries.

One global step contains:

```text
if Phase1=0:
  pre-shift Work2
  r-side subtract
  conditionally restore with r-side add

if Phase1 xor Phase2:
  one location-controlled swap of Sign and the current q bit
  increment or decrement ell_q

if Phase1=1:
  t-side conditional subtract
  t-side add
  post-shift Work2

update Phase1, Phase2, Sign

if ell_q=0 and ell_s=0:
  full swap Work1 <-> Work2
  refresh ell_t and ell_r'
  toggle Iter
```

At the abstraction level of one step, the dominant variable-position work is:

```text
one location-controlled swap
two location-controlled additions
two location-controlled subtractions
four position shifts
optional full n+3 Work swap and length updates
```

The explicit circuit is exact and reversible. Its low space comes with substantial gate overhead from dynamic positioning and length maintenance.
