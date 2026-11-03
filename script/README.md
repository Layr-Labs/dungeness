# Repository maintenance

`check.py` runs the offline component suites; `export_runtime.py` exports only
committed, allowlisted runtime files. Run `make check` from a full checkout.

See [development](../docs/development.md) and
[runtime distribution](../docs/runtime-distribution.md).

`check-run-isolation.py` tests two simultaneous generated Docker topologies,
including host/other-run denial and own-run inference/resources. Run it with
`make check-run-isolation`; no paid model access is used.
