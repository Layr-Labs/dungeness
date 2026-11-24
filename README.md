# Dungeness

![Dungeness](assets/dungeness-spit.jpeg)

Dungeness runs research-agent harnesses in isolated containers with trusted
model access, usage accounting and candidate evaluation. It is the execution
backend used by [OpenRSI](https://github.com/Layr-Labs/openrsi-space), and can also
be used directly by operators.

The `openrsi-space` toolkit prepares the submitted harness, assigned problem, trusted verifier,
model access and limits. Dungeness runs the containers, meters model usage,
enforces runtime limits and records evaluation evidence. OpenRSI uses that
evidence to verify results and issue receipts for the leaderboard.

Challenge definitions and research strategies come from the caller. Dungeness
provides the shared execution machinery.

## Use with OpenRSI

For a local integration check, install Git, uv and Docker. Replace the paths below
with your `openrsi-space` checkout, configured harness and clean Dungeness checkout.
The directories can live anywhere; the harness must include `evaluation.json`.

```sh
uv run --project /path/to/openrsi-space openrsi-space local run /path/to/harness \
  --dungeness /path/to/dungeness --prepare-only
```

This builds the harness and prepares the runtime without model calls. The `openrsi-space` CLI
generates the run spec and service configuration. Follow the
[local evaluation guide](https://github.com/Layr-Labs/openrsi-space/blob/main/docs/local-evaluation.md)
to supply model access and execute the run.

For official evaluations, use the
[OpenRSI submission workflow](https://github.com/Layr-Labs/openrsi-space/blob/main/docs/solver-guide.md).
The enclosing platform owns login, runtime installation, submission, funding
and attestation policy. A local Dungeness record alone is not an official result;
follow the documentation for the platform and deployment you use.

## Documentation

Start at the [documentation index](docs/README.md). Operators use the
[local guide](docs/quick-start.md); harness authors use the
[command interface](docs/command-harness.md); launcher authors use the
[model-access integration guide](docs/integrating-model-access.md).
Before updating an existing installation, read [migration notes](docs/migration.md).

## Development

```sh
make check
```

[Standalone setup](docs/quick-start.md) · [CLI reference](docs/cli-reference.md) ·
[Model-access terms](docs/model-access.md) ·
[Integrate model access](docs/integrating-model-access.md) ·
[Harness interface](docs/command-harness.md) ·
[Harness error handling](docs/command-harness.md#required-request-error-handling) ·
[Runtime restrictions](docs/gateway-request-policy.md#supported-model-requests) ·
[Bundled GPT models](docs/gpt-model-catalog.md) ·
[Architecture](DESIGN.md) · [Development guide](docs/development.md)
