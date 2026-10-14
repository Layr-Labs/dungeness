# ECDSA.fail Paper Knowledge Base

This directory turns André Schrottenloher's paper, *Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms* (arXiv:2606.02235), into an implementation-oriented knowledge base for agents working on the secp256k1 point-addition benchmark.

The material is split at two levels:

- [`sections/`](sections/) follows the paper in reading order and explains how each section fits into the complete construction.
- [`nodes/`](nodes/) contains small, independently retrievable claims, algorithms, parameters, caveats, and benchmark mappings.

There are also two convenient entry points:

1. Give an agent [`agent-pack.md`](agent-pack.md). This is the compact, self-contained version designed for a single benchmark run.
2. Copy the whole directory into a research workspace and tell the agent to follow [`AGENTS.md`](AGENTS.md). This version preserves provenance, cross-links, and open questions.

Start with [`index.md`](index.md) when reading the decomposed wiki.

## Scope

The knowledge base distinguishes four kinds of statements:

- **[PAPER]** A result or claim from arXiv:2606.02235 v1.
- **[CODE]** A fact recovered from the authors' companion Qarton implementation.
- **[BENCHMARK]** A fact about the ecdsa.fail harness or repository.
- **[INFERENCE]** A proposed mapping, optimization, or conclusion that must be tested.

That distinction is important. The paper's windowed-addition setting, approximate-success criterion, and emitted gate counts are not identical to the benchmark's ABI, all-shots validation, and average executed-Toffoli score.

## Primary sources

- Paper: https://arxiv.org/abs/2606.02235
- Companion implementation: https://gitlab.inria.fr/capsule/qarton-projects/ec-point-addition
- Benchmark: https://ecdsa.fail/
- Benchmark repository: https://github.com/Layr-Labs/ecdsafail-challenge

## Suggested agent workflow

1. Read the five section pages in order.
2. Traverse the linked atomic nodes only where more detail is needed.
3. Read the benchmark-adaptation node before transferring a paper technique.
4. Use the compact agent pack when context space is limited.

The wiki explains the paper and its likely benchmark relevance. It is not evidence that a circuit implementation works; only the benchmark's trusted evaluator can establish that.
