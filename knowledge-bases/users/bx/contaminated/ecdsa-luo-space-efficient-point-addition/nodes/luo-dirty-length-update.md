---
kind: node
id: luo-dirty-length-update
source: arXiv:2607.13816v2 section 4.1 and Figures 12-13
depends_on: [luo-length-registers, luo-unary-iteration]
related: [luo-active-windows]
---

# Dirty-ancilla length update

**[PAPER]** At an EEA-iteration boundary, the circuit must replace a stored logical length by the bit length of the newly swapped value.

Within an active endpoint window `[k,K]`, the construction:

- borrows `K-k+1` work-register bits as dirty ancillas;
- uses unary iteration to locate the significant endpoint;
- writes or updates the logarithmic length value;
- restores every borrowed bit to its unknown input state.

Dominant cost per length update:

```text
24(K-k) Toffolis
32(K-k) CNOTs
```

Clean selection workspace is only:

```text
O(log(K-k))
```

The updates run only at step indices divisible by four and only when an EEA iteration terminates.

**[INFERENCE]** This is directly relevant to peak-width optimization: an inactive slice need not be clean to serve as scratch if the borrowed-bit protocol restores it exactly.

