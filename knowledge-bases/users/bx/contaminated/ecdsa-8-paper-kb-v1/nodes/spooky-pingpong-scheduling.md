---
kind: node
id: spooky-pingpong-scheduling
source: benchmark plus cross-paper inference
depends_on: [spooky-line-frontier]
---

# Ping-pong tape scheduling

**[BENCHMARK]** A full checkpoint stores wide walk state; generic checkpointing was about 30% more Toffoli at the same peak. Interleaving replay with the walk did succeed, saving 21 qubits for about 4.2k executed Toffolis in one trusted version.

**[INFERENCE]** Model each round with weighted costs:

```text
state width
tape prefix
replay ladder
walk recomputation
fold/comparison corrections
```

Optimize this nonuniform schedule, not an unweighted line.
