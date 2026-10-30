# Dungeness

![Dungeness](assets/dungeness-spit.jpeg)

Dungeness is the execution backend for [OpenRSI](https://github.com/Layr-Labs/openrsi-space),
a benchmark for research agent harnesses. Its solver CLI is named `openrsi-space`;
Dungeness remains the runtime name.

The `openrsi-space` toolkit prepares the submitted harness, assigned problem, trusted verifier,
model access and limits. Dungeness runs the containers, meters model usage,
enforces runtime limits and records evaluation evidence. OpenRSI uses that
evidence to verify results and issue receipts for the leaderboard.

Challenge definitions and research strategies come from the caller. Dungeness
provides the shared execution machinery.

## Use with OpenRSI

For a local integration check, install Git, uv and Docker. Replace the paths below
with your `catalyst` checkout, configured harness and clean Dungeness checkout.
The directories can live anywhere; the harness must include `evaluation.json`.

```sh
uv run --project /path/to/catalyst openrsi-space local run /path/to/harness \
  --dungeness /path/to/dungeness --prepare-only
```

This builds the harness and prepares the runtime without model calls. The `openrsi-space` CLI
generates the run spec and service configuration. Follow the
[local evaluation guide](https://github.com/Layr-Labs/openrsi-space/blob/main/docs/local-evaluation.md)
to supply model access and execute the run.

For official evaluations, use the
[OpenRSI submission workflow](https://github.com/Layr-Labs/openrsi-space/blob/main/docs/solver-guide.md).
Platform-funded submissions require matching local Dungeness run evidence,
unless the operator grants an exemption; the hosted service supplies its own runtime.

## Development

```sh
make check
```

[Standalone setup](docs/quick-start.md) · [CLI reference](docs/cli-reference.md) ·
[Harness interface](docs/command-harness.md) ·
[Architecture](DESIGN.md) · [Development guide](docs/development.md)
