---
kind: research-dossier
id: arithmetic-control-structure
depends_on: [recurrence-state-machine]
---

# Dossier: there is no context-free “best adder”

The repeated arithmetic contract must be classified before selecting a paper
primitive.

## Control contracts exposed by the papers

| Contract | Relevant mechanism | Important limitation |
|---|---|---|
| Quantum value added to quantum target | Schrottenloher replay arithmetic | generic controlled-add cost can dominate |
| Choose add versus subtract | Litinski controlled add-subtract | unwanted branch creates global corrections |
| Add a classical constant under one quantum control | Gidney zero-overhead control | does not apply to a quantum addend |
| Apply an operation at a coherent moving location | Luo location-controlled arithmetic | selection and length updates remain |
| Produce a value immediately consumed by another operation | Häner integrated arithmetic | saving depends on the neighboring consumer |

**[PAPER: Litinski]** A controlled add-subtract without carry-out costs
`n-1` Toffolis, matching an ordinary ripple adder, because the control can be
absorbed through complements. It is not add-or-identity. Global affine
corrections recover the desired product.

**[PAPER: Gidney]** A classical offset can be controlled by replacing each
classical offset bit with its conjunction with the control, adding no
Toffolis or workspace to the constant-adder construction. Carry venting and
dirty-half borrowing trade dynamic phase repair for clean workspace.

**[PAPER: Luo]** Location controls select a subrange whose physical position is
quantum data. This is different from controlling whether an operation happens.

## Inventory the hot loop

For every repeated call, record:

```text
left operand: quantum / runtime classical / compile-time constant
right operand: quantum / runtime classical / compile-time constant
control: identity / quantum bit / add-versus-subtract / coherent location
carry-out: retained / discarded / recomputable
residue range before and after
consumer of the result
scratch live at the global peak
```

Only calls with the same tuple should share an implementation by default.

## Cross-paper bridge hypotheses

- A replay branch may become Litinski-compatible if add-versus-subtract is
  acceptable and its global correction fuses with pseudo-Mersenne folding.
- A modular fold or terminal normalization may become Gidney-compatible when
  its addend is the classical constant `f = 2^32+977`.
- Luo-style location metadata may shrink the active width of a current adder
  without importing the complete four-phase EEA.
- Häner-style consume-before-uncompute may delete a copy or cleanup around an
  otherwise unchanged arithmetic primitive.

All four are **[INFERENCE]** until their closed-shell correction and inverse are
derived.

## Decisive experiment

Select the most frequent contract, then compare:

```text
current complete cell
paper primitive plus all corrections
paper primitive fused with its immediate predecessor and consumer
```

At small width, verify every control branch, carry boundary, inverse, and
relative phase. At full width, count executed Toffoli and hard-ID effect over
the complete repeated interval. Reject a local primitive saving that adds a
full-width correction or fresh register outside the measured cell.
