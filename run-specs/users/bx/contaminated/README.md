# Remote run-spec contamination inventory

Last audited: 2026-09-11.

Remote source: `origin/main` at `e29a8c1fdc7c`.

This inventory includes only run directories tracked on `origin/main`, as
enumerated by:

```text
git ls-tree -r --name-only origin/main runs/users
```

Local-only run directories are excluded. A run is classified as contaminated
when its `record.json` associates it with a knowledge base listed as
**CONTAMINATED** in
[`knowledge-bases/users/bx/README.md`](../../../../knowledge-bases/users/bx/README.md).
A run-spec is listed below when at least one remote run made from that spec is
contaminated.

Historical records use the former references
`knowledge-base:users/bx/<id>`. The same knowledge bases now use
`knowledge-base:users/bx/contaminated/<id>`.

Existing run-spec definitions covered by this inventory are stored in this
directory. Their manifest namespace and canonical references remain
`users/bx`; this is a physical organization boundary, not an identity change.

## Summary

- Remote run directories inspected: **48**
- Runs contaminated through a preloaded knowledge base: **29**
- Recorded run-spec IDs with at least one contaminated remote run: **23**
- Existing run-spec definitions moved here: **18**
- Historical-only run-spec IDs with no current YAML definition: **5**

## Contaminated run-specs

| Contaminated knowledge base | Recorded run-spec | Contaminated remote runs |
| --- | --- | ---: |
| `ecdsa-32-paper-bundle-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-kb-32-paper-bundle-12usd` | 1 |
| `ecdsa-8-paper-frontier-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-8-paper-frontier-36usd` | 1 |
| `ecdsa-8-paper-frontier-kb-v2` | `run-spec:users/bx/ecdsa-astra-high-8-paper-frontier-v2-36usd` | 1 |
| `ecdsa-8-paper-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-kb-8-paper-12usd` | 3 |
| `ecdsa-8-paper-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-kb-8-paper-36usd` | 1 |
| `ecdsa-8-paper-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-kb-8-paper-36usd-r2` | 1 |
| `ecdsa-8-paper-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-kb-8-paper-persistent-64usd` | 1 |
| `ecdsa-8-paper-kb-v1` | `run-spec:users/bx/ecdsa-gpt56-high-kb-8-paper-12usd` | 1 |
| `ecdsa-luo-space-efficient-point-addition` | `run-spec:users/bx/ecdsa-legacy-luo-space-efficient-kb-12usd-r1` | 1 |
| `ecdsa-luo-space-efficient-point-addition` | `run-spec:users/bx/ecdsa-reconstruction-luo-space-efficient-kb-12usd-r1` | 1 |
| `ecdsa-luo-space-efficient-point-addition` | `run-spec:users/bx/ecdsa-reconstruction-luo-space-efficient-kb-36usd-r1` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-kb-v1-regression-12usd` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-claude-code-fable-kb-v1-12usd-r1` | 2 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-claude-code-fable-kb-v1-36usd-r1` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-codex-fable-kb-v1-12usd-r1` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-codex-legacy-kb-36usd-r1` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-codex-legacy-kb-36usd-r2` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-codex-legacy-kb-36usd-r3` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-gpt56-high-kb-v1-regression-12usd` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-kimi-subscription-llm-wiki-max-12usd-knowledge-base` | 2 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-reconstruction-kimi-max-36usd-kb-r1` | 1 |
| `ecdsa-paper-kb-v1` | `run-spec:users/bx/ecdsa-reconstruction-pilot-knowledge-base` | 3 |
| `ecdsa-schrottenloher-frontier-kb-v1` | `run-spec:users/bx/ecdsa-astra-high-schrottenloher-frontier-12usd` | 1 |

## Historical-only run-spec IDs

These contaminated IDs occur in remote run records, but their YAML definitions
are no longer present and therefore could not be moved:

- `run-spec:users/bx/ecdsa-claude-code-fable-kb-v1-12usd-r1`
- `run-spec:users/bx/ecdsa-claude-code-fable-kb-v1-36usd-r1`
- `run-spec:users/bx/ecdsa-codex-fable-kb-v1-12usd-r1`
- `run-spec:users/bx/ecdsa-codex-legacy-kb-36usd-r3`
- `run-spec:users/bx/ecdsa-reconstruction-kimi-max-36usd-kb-r1`

## Qualification

The remote contains three records for
`run-spec:users/bx/ecdsa-kimi-subscription-llm-wiki-max-12usd-knowledge-base`.
Two preload the contaminated `ecdsa-paper-kb-v1` and are counted above. The
third was an earlier startup failure that instructed the agent to maintain its
own workspace wiki but did not preload a Dungeness knowledge base; it is not
counted as KB-contaminated.

No remote run currently uses `ecdsa-8-paper-paper-only-kb-v1`. The existing
paper-only persistent run is local-only and is therefore intentionally absent
from this inventory.

Run-spec definitions using contaminated knowledge bases but having no run
tracked on `origin/main` are also intentionally left outside this directory.
