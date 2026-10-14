---
kind: node
id: gidney-benchmark-adaptation
source: cross-paper inference
depends_on: [gidney-constant-workspace-adder, gidney-zero-overhead-control]
---

# Gidney 2025 benchmark adaptation

**[INFERENCE]** Search for a classical-constant add that currently:

- allocates a long clean carry ladder;
- occurs during tape/replay peak;
- is controlled by one bit;
- has target halves available for dirty borrowing.

Do not replace the main quantum-quantum replay adder merely because the paper's headline is `3n`; the current primitive may already cost `n-1` per add under its different operand model.
