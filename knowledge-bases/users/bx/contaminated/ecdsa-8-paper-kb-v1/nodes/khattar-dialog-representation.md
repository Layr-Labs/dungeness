---
kind: node
id: khattar-dialog-representation
source: arXiv:2510.10967, section II.B.3
---

# Dialog representation

Each constant-time EEA step is a small invertible matrix:

```text
tau_i
```

The ordered list:

```text
Dialog = [tau_1, tau_2, ..., tau_m]
```

implicitly represents the complete Bézout transformation. Applying the list forward or backward acts on data without explicitly materializing the coefficient polynomials.
