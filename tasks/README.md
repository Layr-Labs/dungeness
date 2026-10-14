# Task-authoring notes

## Security-sensitive framing

In Codex/OpenAI benchmark runs, task statements that repeatedly describe the
objective as “breaking” ECC or secp256k1, especially alongside references to
Bitcoin, Ethereum, or cryptocurrency security, have frequently been flagged as
cybersecurity-risk requests. This can happen even when the actual task is the
benign construction and optimization of a reversible arithmetic circuit.

Prefer precise, neutral wording that describes the work being evaluated:

- reconstruct or optimize a reversible secp256k1 point-addition circuit;
- specify the input/output transformation, ancilla requirements, and scoring
  metric directly;
- omit security-impact narratives when they are not required by the benchmark.

[`users/bx/ecdsa-fail-reconstruction/statement.txt`](users/bx/ecdsa-fail-reconstruction/statement.txt)
is the reference framing for this benchmark.

This guidance is intended to describe the task accurately and avoid misleading
false positives. It must not be used to conceal genuinely security-relevant
intent, remove material constraints, or bypass applicable safety controls.
