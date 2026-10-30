# Per-run network isolation

Harbor creates and removes each trial's Docker Compose project. Dungeness renders
its network policy; no shared network names, host ports or host network mode are
supplied to a submitted harness.

| Service | Networks | Access |
| --- | --- | --- |
| Agent | Its run's `agent_internal` | Its gateway and optional development scorer |
| Gateway | `agent_internal`, optional `problem_internal`, `external_egress` | Fixed model routes and assigned resources |
| Problem server | Its run's `problem_internal` | Gateway requests only |
| Development scorer | Its run's `agent_internal` | Local feedback and authenticated gateway accounting |
| Final verifier | None | Frozen candidate verification |

Both internal bridges use Docker's native `isolated` gateway mode for IPv4 and
IPv6. Unlike plain `internal: true`, this removes the bridge's host-facing address.
An ordinary internal bridge allows containers to reach host services listening on
that address, including wildcard listeners. No host firewall rules are added by
Dungeness. See [Docker gateway modes](https://docs.docker.com/engine/network/port-publishing/#gateway-modes).

The agent drops `NET_RAW` and `NET_ADMIN`, with `no-new-privileges`, preventing
raw packet injection, routing changes and restoration through setuid/file
capabilities. Normal TCP/UDP, subprocesses and writable workspaces remain
available. The gateway has all capabilities dropped and IPv4/IPv6 forwarding
disabled: its multiple interfaces support application requests, not kernel routing.
The private credential and accounting mounts are never attached to the agent.

This uses Harbor 0.18.0's existing task-authored Compose support and Docker's
bridge driver; it does not add a network-control daemon or replace Harbor's
lifecycle. An engine must support `gateway_mode_ipv4/ipv6=isolated`. Unsupported
engines fail during network creation; do not remove the options to work around
that failure. Local validation used Linux Docker 29.1.3.

## Validation

```sh
make check-run-isolation
```

This Docker check starts two generated run topologies simultaneously with
synthetic model providers, credentials, task resources and scorers. It verifies
own-run operation, denies access to the other run's services and host canaries,
checks IPv4/IPv6 and gateway forwarding, rejects raw sockets and unauthenticated
accounting, and confirms private mounts are absent from the agent. No real model
account or metadata endpoint is contacted. Fixture resources are removed afterward.
The check runs in GitHub Actions on pushes and pull requests.

To reproduce only the old host-access gap with a synthetic listener:

```sh
uv run --locked --group gateway python script/check-run-isolation.py --baseline
```

The full OpenRSI mock integration additionally exercises the actual Harbor
adapter, candidate evaluation, independent verification and Yukon receipt retrieval.

## Scope

These checks test network and mount boundaries, not kernel exploit resistance.
Containers share a host kernel; the trusted gateway and scoring services remain
part of the trusted computing base. A compromised gateway still has its provider
credential and egress interface. API/runtime Docker privilege separation and
host-wide resource exhaustion controls need separate review before increasing
execution concurrency. This patch does not change the number of live workers.
