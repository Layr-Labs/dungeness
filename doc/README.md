# Dungeness documentation

This directory collects implementation notes for the
current Dungeness research-effort controller.

## Documents

- [ResearchState runtime path](research-state-runtime-path.md) is the recommended
  starting point. It explains the key distinction between continuous gateway
  injection and the Codex completion hook, the exact Codex changes, and the
  gateway-free portability limitation.
- [ResearchState evaluation-cadence implementation](research-state-evaluation-cadence.md)
  is the detailed implementation note covering state, cadence calculation,
  event ownership, completion lifecycle, and tests.
- [Run-scoped knowledge bases](knowledge-base-preload.md) explains retrieval,
  raw-paper access, and behavior feedback.

## Current scope

The current prototype applies the same progressive mechanism independently to
web-search and authoritative-evaluation effort. Unit coverage verifies both
paths. Keep live-run evidence and experiment reports in local or service artifact
storage.

The canonical implementation is in:

- `services/research-state/server.py`
- `services/gateway/gateway.py`
- `services/gateway/kimi_adapter.py`
- `adapters/harbor/build.py`
- `adapters/harbor/codex_gateway.py`
