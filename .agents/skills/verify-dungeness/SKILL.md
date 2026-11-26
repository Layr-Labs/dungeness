---
name: verify-dungeness
description: Run Dungeness Runtime verification after changes to launch, gateway routing, isolation, usage, or scoring. Drive the offline Harbor fixture and detect seeded faults at their expected assertions.
---

# Launch

Use a local Docker engine. Use Python 3.12 and the repository's uv lock. Set these inputs before you run the loop.

- Set `DUNGENESS_VERIFY_UV_CACHE` to the local uv cache with the locked gateway and Harbor packages.
- Set `DUNGENESS_VERIFY_IMAGE` to the full `sha256:…` ID of a local Linux image for the host architecture. The image must contain Python 3.12, Bash, and the exact packages in `services/gateway/requirements.txt`. The image ID and package versions must match. It builds the gateway from the checkout.
- Set `DUNGENESS_VERIFY_GOOGLE_PYTHON` to the Python 3.12 executable in an approved local environment with `google-genai==3.6.1` and the gateway dependencies. The loop uses this environment directly and requires the pinned SDK version.
- Set `DUNGENESS_VERIFY_STOCK_ADAPTER` to the local copy of `src/openrsi_space/integrations/dungeness/stock_adapter.py` from OpenRSI Space dev commit `ac5b68b4268f94fd10d011e923526086d8973ef4`. The file must match the pinned SHA-256 digest.

Set the Docker CLI on `PATH`. On macOS, select a Docker context that shares the checkout path with its Linux VM. The loop uses the local Docker builder with image IDs as base references. Use an approved local cache for every input.

For Linux CI, set repository variables `RUNTIME_VERIFY_CACHE_KEY` and `RUNTIME_VERIFY_IMAGE_ID`. The cache contains `uv/`, `stock_adapter.py`, `google/bin/python`, and `image.tar` at its root. Use an x86-64 image and uv cache. The workflow restores that exact key and runs proof mode.

# Doctor

Run `python3 script/verify-runtime.py --doctor` to print the image, Docker and Compose versions, and stock adapter digest. Each check fails if its Python packages are absent. Read the named log for the exact missing package.

# Drive

1. Run `make verify`. Check the core and Harbor tests, route discovery, Docker gateway isolation, scored Harbor run, pinned Google SDK, and Linux run isolation.
2. Run `make verify PROVE=1`. The loop requires a clean pass before it creates a separate copy for each fault. A command failure must show the expected assertion.
3. Use `python3 script/verify-runtime.py --leg scored-run` or `--leg gateway-isolation` to diagnose a single leg. Use `--leg faults` to diagnose fault assertions. These commands do not establish a full pass.

The scored run writes a candidate from the local Anthropic Messages response. The stock adapter retries one settled 429. The gateway rejects the next request after the synthetic charge exhausts the run budget. The offline verifier checks the candidate and records score 42. The loop checks both gateway and provider counts.

# Evidence

Read `.verify/evidence.json` for the latest invocation. Read `.verify/verify/evidence.json` and `.verify/prove/evidence.json` for complete loop results. The corresponding directories hold redacted command logs. Compare the commit, image and fixture hashes, test counts, usage state, and fault assertions.

# Cleanup

The loop removes its scratch copies and Docker resources after each check. Keep the evidence for review. If Docker teardown fails, inspect only the run or image names in the failing log. Remove a resource only after you check that it belongs to that invocation.

# Gotchas

- The host-bridge isolation check and fault require Linux x86-64. Docker on macOS puts that bridge inside a Linux VM.
- The loop records Docker's bind-mount UID and GID. The scored fixture uses that owner when the Mac engine maps bind ownership differently from the host.
- Image preflight requires a preloaded local image. The verification loop makes zero paid model calls.
- A fixture score and simulated charges establish local behavior. Live entitlements, provider billing, signed Mac execution, and official verifier receipts require separate checks.
- The runner rewrites provider destinations in the scratch fixture. The score applies to that fixture route. Adjacent consumers and their deployed pins require their own loops.
- A Docker engine that grants another UID access to private bind-mounted files fails the gateway isolation check. Use a compatible local engine for a full pass.
