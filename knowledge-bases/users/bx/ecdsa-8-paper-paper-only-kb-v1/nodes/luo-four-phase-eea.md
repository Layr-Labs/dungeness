---
kind: node
id: luo-four-phase-eea
source: arXiv:2607.13816v2 section 3.1
depends_on: []
related: [luo-uniform-step-bound, luo-shared-work-registers, luo-optimized-eea-step]
---

# Luo four-phase EEA

**[PAPER]** One Euclidean quotient/update is implemented as four shift-and-add phases:

```text
Phase 1: left-align r_i against r_(i-1)
Phase 2: shift right, subtract, and build quotient q_i
Phase 3: consume quotient bits while updating t_(i-1)
Phase 4: restore coefficient alignment
then swap the two EEA roles
```

The logical recurrence is:

```text
r_(i+1) = r_(i-1) - q_i*r_i
t_(i+1) = t_(i-1) + q_i*t_i
```

The algorithm uses only shifts and long add/subtract operations. Different inputs occupy different phases at the same global step, so phase state is quantum data and the circuit must use a fixed global schedule.

This differs from the binary-history EEA in the earlier KB: it retains explicit quotient-processing state rather than recording one compact branch symbol per binary step.
