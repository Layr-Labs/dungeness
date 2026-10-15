# Dungeness implementation notes

- [Harness-owned knowledge](knowledge-base-preload.md) explains the removal of
  the knowledge-base service and how to migrate older runs.
- [Command harnesses](../docs/command-harness.md) describes agent-owned research
  loops and the trusted execution interface.
- [Runtime distribution](../docs/runtime-distribution.md) describes source bundles
  and retention of historical experiments.

Dungeness owns isolation, model accounting and independent evaluation. Research
strategy, memory, evaluation cadence and completion decisions belong to the
harness. The former research-state controller is no longer part of the runtime.
