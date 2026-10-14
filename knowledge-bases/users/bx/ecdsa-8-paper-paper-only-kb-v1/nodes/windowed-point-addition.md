---
kind: node
id: windowed-point-addition
source: paper section 2
depends_on: [shor-point-multiplication]
---

# Windowed point addition

```text
|i>|R> -> |i>|R+P_i>
```

For a window size `w=16`, scalar multiplication becomes a sequence of point additions selected from precomputed windows.

Paper-specific costs:

```text
window qubits = 16
three lookups = 3*2^16 Toffolis
```

The first addition is replaced by a lookup and the last three are removed with classical post-processing, leaving 28 additions for secp256k1.

The lookup schedule belongs to the paper's full scalar-multiplication wrapper.
See [`paper-interface-boundaries.md`](paper-interface-boundaries.md).
