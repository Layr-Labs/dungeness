# Agent instructions

Your goal is to use this paper knowledge while preserving value correctness, ancilla cleanliness, relative phase, and explicit forward/reverse behavior.

## Required reading order

1. Read `index.md`.
2. Read `concepts/luo-resource-tradeoffs.md`.
3. Read `concepts/luo-measured-register-recycling.md`.
4. Read `concepts/luo-porting-to-ecdsa-fail.md`.
5. Read only the nodes relevant to the measured peak or subroutine you intend to change.

For a compact one-shot run, use `agent-pack.md`.

## Evidence discipline

- Treat **[PAPER]** and **[CODE]** as source knowledge, not implementation proof.
- Treat **[INFERENCE]** as a hypothesis.
- Keep paper claims and later companion-code claims distinct.
- Do not claim a win from source inspection, a reduced test, or projected arithmetic.
- Record failed experiments when they establish a reusable constraint.

## Architecture summary

The paper's low-space path is:

```text
four-phase EEA
-> two shared n+3 work registers
-> four coherent length registers
-> active-window location-controlled arithmetic
-> forward inversion with retained Gamma(x)
-> measured field-register recycling
-> three-register affine point addition
```

The construction is exact, but minimizing width adds substantial selector, ripple-arithmetic, and length-update cost.

## Recommended adoption order

1. Measure the current peak owner.
2. Identify an obsolete field value that remains exactly recomputable.
3. Test Hadamard-basis demolition and phase repair at tiny width.
4. Recycle one real field register without changing the arithmetic architecture.
5. Apply liveness-only overlap and dirty borrowing.
6. Microbenchmark unary selection against the current control pattern.
7. Port location-controlled arithmetic only where necessary.
8. Port the complete four-phase EEA only after projecting both score factors.

## Dynamic-circuit warning

Measurement, reset, and feed-forward are not inverted by reversing a gate list.

Before using full-register recycling, establish:

- retention of every measurement outcome;
- correct bit order for `b dot y`;
- support for classically controlled `Z`;
- superposition-sensitive phase tests;
- an explicit inverse protocol;
- conditional-operation scoring.

A mutation test should fail if any phase-correction bit is removed.

## Benchmark discipline

- Edit only authorized implementation paths.
- Do not modify the evaluator, score computation, tests, or seeds.
- Do not erase quantum data with unsupported reset.
- Do not accept rare failures if the benchmark requires all shots.
- Compare the complete objective, not qubits alone:

```text
average executed Toffoli * peak qubits
```

## Logging

Append to `log.md`:

```text
## [YYYY-MM-DD] experiment | short title
- Base commit:
- Paper hypothesis:
- Peak owner before:
- Files changed:
- Result:
- Score / executed Toffoli / peak qubits:
- Basis correctness:
- Phase and forward/reverse correctness:
- Interpretation:
- Next action:
```

