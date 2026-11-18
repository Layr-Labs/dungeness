# Native Antigravity qualification probe

This is an operator experiment, not an enabled model provider. It tests Google's
unmodified Linux ARM64 `agy` CLI against synthetic Gemini responses. It does not
use subscription credentials, call a live model, or establish attestation
eligibility.

The archive is pinned to the official release manifest in `cli-release.json`.
Download that URL to a temporary directory and run:

```sh
python3 tools/antigravity-probe/run.py \
  --archive /path/to/cli_linux_arm64.tar.gz \
  --image openrsi-guest-gateway:dev
```

Python 3.11+ and Docker are required. `--image` can name another **locally
installed Linux ARM64 image with Python 3 and glibc**. No image is pulled. The
wrapper verifies the archive SHA-512 and selects the local image by its immutable
ID. It copies one ELF executable without unpacking archive paths.

The container has no external network, no host credentials, no Docker socket,
no writable host mounts, a read-only root, and a non-root UID. Its only writable
storage is disposable `/tmp`. The synthetic endpoint runs on container loopback.
The MCP fixture returns a fixed string; it never executes its command argument.
One negative test asks the CLI to invoke an undeclared shell tool that would
create a harmless temporary marker if incorrectly accepted.

The report includes:

- text-only usage compared with the synthetic server's observed requests;
- a tool call in both default and unattended permission modes;
- an explicitly allowed MCP tool, both lazy-loaded and eager-loaded;
- invocation-hook coverage compared with the observed model calls;
- rejection of an undeclared shell tool;
- the CLI archive digest and container image ID.

Exit `0` means these bounded checks pass, **not that subscription access or the
whole execution boundary is qualified**. Exit `2` means the completed report
contains a failed check. Other failures print a diagnostic.

## Observed on 2026-11-18

Official CLI `1.5.11`:

| Case | Requests observed | Usage reported | Result |
| --- | --- | --- | --- |
| Text | 1 Carbon | 1 Carbon | Matches |
| MCP, default permissions | 1 Carbon + 1 Flash Lite review | 1 Carbon | Tool not completed; CLI still returns success |
| MCP, unattended | 2 Carbon + 1 Flash Lite review | 2 Carbon | Tool completed; helper usage missing |
| Undeclared shell | 2 Carbon | 2 Carbon | Shell rejected; marker absent |
| MCP, explicit allow rule | 2 Carbon + 1 Flash Lite review | 2 Carbon | Tool completed; helper usage missing |
| Eager MCP, explicit allow rule | 2 Carbon + 1 Flash Lite review | 2 Carbon | Tool completed; helper usage missing |
| MCP, invocation hooks | 2 Carbon + 1 Flash Lite review | 2 Carbon | Both hook types see only the two Carbon invocations |

The resumed observations are in
[`observed-1.5.11-resumed.json`](observed-1.5.11-resumed.json). The original report
is retained separately. Actual tool completion comes from a journal in the MCP
fixture, not from the CLI's `DONE` state or `SUCCESS` result. This prevents a
declined or invalid tool call from appearing to solve the accounting gap.

The eager tool request uses the CLI's actual `parametersJsonSchema`, including
the added `toolSummary` field. The completed eager case is not a schema-error
shortcut around the review call. `PreInvocation` and `PostInvocation` hook
payloads identify the Carbon model and invocation index but contain no usage
counts and omit the reviewer invocation entirely.

The review fixture returns valid JSON, including severity, confidence and reason.
The helper's `modelVersion` matches the requested model. Every response includes
usage metadata. These controls rule out a malformed review response as the
reason for the missing helper usage.

For each synthetic response, the upstream supplies 100 input tokens (20 cached),
5 candidate tokens and 3 thought tokens. The CLI reports input 80, output 8,
thinking 3, cached 20 and total 88. Output already includes thinking; input and
total exclude cache. Never sum per-step usage with the cumulative final usage.

The model-facing tool declarations exclude `run_command` for the custom agent,
and the CLI rejects an injected call to it. The `init.tools` array nevertheless
lists built-in tools; it is not a reliable record of the effective tool set.
This single negative test is not a complete credential-isolation audit.

These observations use the documented Gemini API-key transport with a **dummy
key and offline endpoint**. They do not demonstrate actual Google billing,
subscription entitlement, or identical behavior on the subscription transport.

See the [integration assessment](../../docs/native-antigravity.md) for the
remaining work across Dungeness, the VM, and the manager.
