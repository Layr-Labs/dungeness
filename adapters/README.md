# Execution adapters

`harbor/` bridges command harnesses to the pinned Harbor SDK. Keep SDK-specific
imports and stable adapter entry points here; generic lifecycle code lives in
[`src/dungeness/execution/`](../src/dungeness/execution/).

See [command harnesses](../docs/command-harness.md).
