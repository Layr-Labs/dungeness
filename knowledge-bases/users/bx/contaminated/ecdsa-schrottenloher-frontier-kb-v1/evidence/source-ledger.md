# Evidence ledger

## Primary source

**[PAPER]** André Schrottenloher, *Optimized Point Addition Circuits for
Elliptic Curve Discrete Logarithms*, arXiv:2606.02235v1.

Material represented in the dossiers:

- affine point-add scheduling;
- fixed binary-Euclid history construction;
- compressed history and register sharing;
- Bézout/linear replay;
- in-place modular multiplication and division;
- secp256k1 pseudo-Mersenne doubling and controlled addition;
- approximation parameters and failure model;
- measurement-based uncomputation.

## Companion implementation

**[CODE]** The pinned companion implementation supplies concrete engineering
choices such as:

- fixed iteration and padding constants;
- three-step history compression into five bits;
- separate early exceptional and later fast replay adders;
- truncated comparison and carry windows;
- implementation-specific register conventions.

These are evidence about one implementation, not immutable requirements.

## Benchmark adaptation

**[BENCHMARK]**

- target coordinates are quantum input/output registers;
- offset coordinates are runtime classical-bit registers;
- every ancilla and phase must be clean;
- validation runs progressively through all 9,024 shots;
- score is average executed Toffoli multiplied by hard qubit count.

## Deliberate omissions

This KB does not include discoveries from later Astra runs, including their
new recurrences, fused arithmetic, tuned schedules, or final parameters. The
experiment is intended to test whether question-first preprocessing can prompt
the solver to derive improvements rather than retrieve those answers.
