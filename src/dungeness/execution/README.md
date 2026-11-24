# Execution lifecycle

`harbor.py` renders jobs and interprets results. `runner.py` orchestrates a run,
`process.py` manages subprocesses, and `environments.py` cleans up Docker resources.
`credentials.py` adapts the compiled run and legacy env-file precedence to
`dungeness.credential_access`. That shared resolver stages selected key/token
values and recipe-selected fields from private JSON files for the run's lifetime.
The solver-agent and launcher contracts are in
[`docs/integrating-model-access.md`](../../../docs/integrating-model-access.md).

Receive validated inputs and explicit paths. Record persistence is supplied by
the caller; model policy and accounting belong to the gateway.
