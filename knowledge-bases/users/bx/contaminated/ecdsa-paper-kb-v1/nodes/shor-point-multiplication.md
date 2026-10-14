---
kind: node
id: shor-point-multiplication
source: paper section 2
---

# Shor point multiplication

Transformation:

```text
|u,v>|0> -> |u,v>|[u]P+[v]Q>
```

The semiclassical Fourier transform recycles scalar-register qubits, so logical resources are approximated by the point-multiplication circuit.

Decomposes into repeated [`windowed-point-addition.md`](windowed-point-addition.md).
