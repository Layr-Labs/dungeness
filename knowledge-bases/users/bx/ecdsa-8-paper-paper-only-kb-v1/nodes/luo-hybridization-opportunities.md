---
kind: node
id: luo-hybridization-opportunities
source: cross-paper inference from arXiv:2607.13816v2 and arXiv:2606.02235
depends_on: [luo-transfer-boundaries, luo-hadamard-register-recycling]
related: [in-place-modular-multiplication, register-sharing, measurement-based-uncomputation]
---

# Hybridization opportunities

These are **[SYNTHESIS]** combinations of mechanisms from the two papers, not
resource results established by either source.

## Field-register recycling around a transcript core

Combine Luo's full-register Hadamard demolition and phase repair with a
transcript-based multiplier. The compatibility question is whether the deleted
field value can be reconstructed from the surviving transcript interface.

## Liveness metadata without moving-value arithmetic

Translate active-window proofs into allocator ranges:

```text
step -> definitely inactive high/low slices
```

Reuse those slices or borrow them dirty while keeping fixed-position adders.

## Dirty borrowing in length and comparison logic

Replace clean helper pools with restored dirty field bits where lifetime analysis proves safety.

## Selected unary operation

Where an algorithm performs many equality-controlled candidate operations, use
one interval selector and include its linear selection cost.

## Full four-phase EEA

The complete Luo architecture is a distinct design point, with 835 qubits and
70.10 million Toffolis for the paper's 256-bit point-addition circuit. Compare
complete interfaces:

```text
representation
output placement
cleanup
measurement transcript
logical width
gate count
```
