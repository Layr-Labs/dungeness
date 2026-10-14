---
kind: node
id: luo-hybridization-opportunities
source: implementation inferences from arXiv:2607.13816v2
depends_on: [luo-benchmark-adaptation, luo-hadamard-register-recycling]
related: [luo-active-windows, luo-dirty-length-update, luo-space-efficient-modular-inversion]
---

# Selective adoption opportunities

These are **[INFERENCE]** hypotheses, not paper claims.

## Priority 1 — field-register recycling around the current arithmetic core

Use the paper's full-register Hadamard demolition and phase repair around an existing working inversion or multiplication implementation. The objective is to remove one live 256-bit region before importing the complete four-phase EEA.

## Priority 2 — liveness metadata before literal location-controlled arithmetic

Translate active-window proofs into allocator ranges:

```text
step -> definitely inactive high/low slices
```

Reuse those slices or borrow them dirty while keeping fixed-position adders.

## Priority 3 — dirty borrowing in length/comparison logic

Replace clean helper pools with restored dirty field bits where lifetime analysis proves safety.

## Priority 4 — selected unary operation

Where current code runs many equality-controlled candidates, use one interval selector. Measure the selector overhead at the benchmark's actual span.

## Priority 5 — full four-phase EEA

Attempt only if peak width dominates and the gate increase is tolerable. The paper's 835-qubit result is attractive, but its `70.10M` point-add Toffoli count makes a literal port an unlikely first score win.

Every hypothesis must be evaluated by:

```text
delta peak qubits
delta average executed Toffoli
phase and garbage correctness
full score product
```
