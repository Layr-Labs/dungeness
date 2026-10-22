# Dungeness

![Dungeness](assets/dungeness-spit.jpeg)

A runtime for evaluating research agent harnesses. Dungeness runs your harness
in an isolated container, meters model usage, enforces resource limits, and
independently verifies candidate solutions. It records the inputs, usage and
results needed to reproduce and compare runs.

You supply the harness and trusted challenge definitions. Catalyst uses Dungeness
as its evaluation backend.

## Get started

Requires Git, uv and Docker; use Linux for isolated final verification.

```sh
git clone https://github.com/Layr-Labs/dungeness.git
cd dungeness
./dungeness setup
./dungeness init --namespace users/alice
```

[Configure and commit your task, verifier, harness, model access and run spec](docs/quick-start.md), then:

```sh
./dungeness run run-specs/users/alice/run.yaml
./dungeness runs run-specs/users/alice/run.yaml
./dungeness evals RUN_ID
```

Runs consume the model access you configure. Results stay under `runs/`.

## Development

```sh
make check
```

[CLI reference](docs/cli-reference.md) · [Harness interface](docs/command-harness.md) ·
[Architecture](DESIGN.md) · [Development guide](docs/development.md)
