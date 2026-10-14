---
kind: node
id: spooky-general-computation
source: arXiv:2110.08973v3
depends_on: [spooky-line-frontier]
---

# General sequential computation

The line result converts to simulation of a classical computation with time `T` and space `S`.

Representative regimes include:

```text
O(T/epsilon) gates with O(T^epsilon S^(1-epsilon)) qubits
O(T^(1+epsilon) S^(-epsilon)/epsilon) gates with O(S/epsilon) qubits
```

The advantage is specifically qubit space; classical ghost records remain.
