# Dungeness

![Dungeness](assets/dungeness-spit.jpeg)

Dungeness is the execution backend for [Catalyst](https://github.com/Layr-Labs/catalyst),
a benchmark for research agent harnesses.

Catalyst prepares the submitted harness, assigned problem, trusted verifier,
model access and limits. Dungeness runs the containers, meters model usage,
enforces runtime limits and records evaluation evidence. Catalyst uses that
evidence to verify results and issue receipts for the leaderboard.

Challenge definitions and research strategies come from the caller. Dungeness
provides the shared execution machinery.

## Use through Catalyst

For a local integration check, install Git, uv and Docker. Replace the paths below
with your Catalyst checkout, configured harness and clean Dungeness checkout.
The directories can live anywhere; the harness must include `evaluation.json`.

```sh
uv run --project /path/to/catalyst catalyst local run /path/to/harness \
  --dungeness /path/to/dungeness --prepare-only
```

This builds the harness and prepares the runtime without model calls. Catalyst
generates the run spec and service configuration. Follow the
[local evaluation guide](https://github.com/Layr-Labs/catalyst/blob/main/docs/local-evaluation.md)
to supply model access and execute the run.

For official evaluations, use the
[Catalyst submission workflow](https://github.com/Layr-Labs/catalyst/blob/main/docs/solver-guide.md).
Hosted submissions do not require a local Dungeness installation.

## Development

```sh
make check
```

[Standalone setup](docs/quick-start.md) · [CLI reference](docs/cli-reference.md) ·
[Harness interface](docs/command-harness.md) ·
[Architecture](DESIGN.md) · [Development guide](docs/development.md)
