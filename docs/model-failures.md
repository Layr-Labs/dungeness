# Model transport diagnostics

The gateway records safe `failure_category` and `failure_stage` fields on a
`model.accounting` event when an upstream request or stream raises an exception.
Categories cover connection/read/other transport timeouts, protocol errors,
connection errors, task cancellation and an unknown fallback. Stages distinguish
request setup, streaming and non-streaming response reads. These classify the
observed boundary; they do not establish whether the provider, network or local
infrastructure caused it. No exception message, URL or credential is exposed.

An HTTP 200 can precede a failed stream. `status: stream_interrupted` describes
that transport outcome; `accounting_method` independently says whether usage was
captured. A stream with trusted usage can remain accounted even if transport
subsequently fails. Without usage, accounting remains `unavailable`, further
model admissions fail closed, and downstream verifiers must not treat the
placeholder zero normalized cost as measured zero usage.

The upstream reader continues after the harness disconnects so final usage can
still arrive on the same request. Separate later requests are not a reconciliation
mechanism for a missing receipt. Current consumers must retain the incomplete
state rather than estimate usage or mint receipts from it. Local harness tests
cannot rule out future upstream interruptions.

`test_command_gateway.py` checks interrupted streams with and without final usage,
safe failure labels and unchanged admission behavior. `test_gateway.py` covers
usage capture after downstream disconnects and accounting during shutdown.
