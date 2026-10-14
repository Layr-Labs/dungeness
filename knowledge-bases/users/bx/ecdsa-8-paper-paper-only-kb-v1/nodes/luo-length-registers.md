---
kind: node
id: luo-length-registers
source: arXiv:2607.13816v2 section 3.2
depends_on: [luo-shared-work-registers]
related: [luo-active-windows, luo-dirty-length-update]
---

# Quantum length registers

**[PAPER]** Four coherent length values define the logical partitions inside the two shared work registers:

```text
ell_t   = active length of t
ell_q   = active length of partial quotient q
ell_r'  = active length of r'
ell_s   = circular-shift/alignment amount
```

Each has:

```text
floor(log2 n)+1 qubits
```

They are quantum registers because different inputs in superposition have different EEA sizes, phase boundaries, and alignments.

Control state also includes:

```text
Phase1, Phase2
Iter
Sign
Ctrl
```

Length registers replace fixed field partitions, but every arithmetic primitive must then be selected by these values. Their updates are infrequent but expensive, so the paper uses active windows and dirty borrowed bits.
