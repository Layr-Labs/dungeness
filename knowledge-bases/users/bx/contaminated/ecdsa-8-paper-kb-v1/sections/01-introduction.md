---
kind: section
paper_section: 1
title: Introduction and reported results
---

# Section 1 — Introduction and reported results

## Purpose

The paper reconstructs a public logical-circuit architecture comparable to the private circuits reported by Babbush et al. It targets Shor's elliptic-curve discrete-logarithm algorithm over prime fields, especially secp256k1.

## Main claims

- The proposed secp256k1 circuits use about 1.5% more qubits than Babbush et al.'s reported points.
- They use about 6.5-10% fewer Toffoli-like gates under the paper's counting convention.
- The selected space architecture scales as roughly `4.355n + O(sqrt(n))` qubits.
- A more aggressive encoding could approach `4.12n + O(sqrt(n))` at likely higher gate cost.
- The circuits are approximate and are validated empirically on random inputs.

## Reported point-add resources

| Variant | Qubits | Toffolis |
|---|---:|---:|
| secp256k1, space optimized | 1192 | `2^21.19` |
| secp256k1, gate optimized | 1446 | `2^20.83` |
| generic prime, space optimized | 1192 | `2^21.78` |
| generic prime, gate optimized | 1446 | `2^21.42` |

The 16-qubit lookup window and `3*2^16` lookup cost are excluded from these rows.

## Architectural thesis

The paper argues that the largest gain comes from replacing conventional reversible inversion with:

```text
Euclid branch discovery -> compressed history -> delayed Bézout replay
```

This directly implements modular in-place multiplication and avoids keeping Euclid inputs and coefficients live together.

## Nodes

- [`../nodes/resource-estimates.md`](../nodes/resource-estimates.md)
- [`../nodes/in-place-modular-multiplication.md`](../nodes/in-place-modular-multiplication.md)
- [`../nodes/failure-model.md`](../nodes/failure-model.md)
- [`../nodes/secp256k1-prime.md`](../nodes/secp256k1-prime.md)

## Next section

[`02-high-level-structure.md`](02-high-level-structure.md)
