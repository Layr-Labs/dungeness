---
kind: node
id: haner-benchmark-adaptation
source: cross-paper inference
depends_on: [haner-adaptive-pebbling, haner-division-workspace-reuse, haner-resource-baseline]
---

# Häner benchmark adaptation

Use as a control:

1. map the current affine shell against the paper's operation DAG;
2. locate intermediates still copied or uncomputed too early;
3. test one consume-before-uncompute fusion;
4. compare against current specialized arithmetic.

Do not port signed-window lookup or generic Montgomery arithmetic unless the benchmark ABI or measured cost justifies them.
