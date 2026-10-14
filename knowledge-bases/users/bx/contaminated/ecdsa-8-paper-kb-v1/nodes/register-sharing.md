---
kind: node
id: register-sharing
source: paper section 3.1
depends_on: [euclid-history]
---

# Register sharing

The live bit-width of `u,v` shrinks approximately as:

```text
width(i) ~= n - 0.5*log2(8/3)*i + c_pad*sqrt(n)
         ~= n - 0.7075*i + c_pad*sqrt(n)
```

Operations use only the active low slices. Cleared high wires become storage for history.

Purpose:

- prevent `u,v` plus history from being additive in space;
- keep history construction around `2.355n + O(sqrt(n))` qubits.

Failure condition: a true `u` or `v` value exceeds the chosen scheduled width.

Parameter node: [`implementation-parameters.md`](implementation-parameters.md).
