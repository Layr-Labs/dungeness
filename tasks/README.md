# Task definitions

`projects/dungeness/ecdsa-starter/` is the maintained local example. A trusted
task defines the statement, source interface, candidate paths, verifier,
network policy and resource limits. Task statements describe the problem;
research strategy belongs to the harness.

Catalyst supplies its own trusted task and checkpoint configuration at run
preparation time. Its runs do not look up a bundled Dungeness task or statement.
The starter is a standalone local example, not Catalyst's challenge contract.

Author new tasks in a deliberate namespace and commit their trusted definitions.
A task can use the immutable problem-service interface described in
[the problem-service guide](../docs/problem-service.md). Solvers cannot replace
that service or the verifier through their submitted agent package.

The evaluator supports `evaluation: {mode: full-benchmark}`. Historical split
case evaluators and personal reconstruction tasks have been retired.
