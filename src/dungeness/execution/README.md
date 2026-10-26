# Execution lifecycle

`harbor.py` renders jobs and interprets results. `runner.py` orchestrates a run,
`process.py` manages subprocesses, and `environments.py` cleans up Docker resources.
`credentials.py` stages private gateway credentials for the run's lifetime.

Receive validated inputs and explicit paths. Record persistence is supplied by
the caller; model policy and accounting belong to the gateway.
