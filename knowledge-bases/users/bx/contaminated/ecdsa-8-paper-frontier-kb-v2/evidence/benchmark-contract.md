# Benchmark contract and translation rules

## Functional contract

The task is reversible affine addition of a runtime classical secp256k1 point
to a quantum point. The implementation must respect the repository's exact
input/output and exceptional-case semantics.

The mathematical core is:

```text
lambda = (target_y - offset_y) * (target_x - offset_x)^(-1) mod p
x3     = lambda^2 - target_x - offset_x mod p
y3     = lambda * (target_x - x3) - target_y mod p
p      = 2^256 - 2^32 - 977
```

Runtime classical offsets are not compile-time constants. A circuit optimized
for a hard-coded constant must expose how its controls are driven by runtime
classical bits.

## Correctness contract

A candidate is incomplete if it leaves any of the following:

- wrong forward coordinates;
- wrong reverse coordinates;
- dirty ancilla or history qubits;
- an unreturned borrowed/dirty register;
- classical transcript required for future cleanup but not retained;
- relative phase from measurement or basis change;
- representation mismatch at the public boundary;
- unhandled modular or elliptic-curve exceptional behavior.

## Objective

```text
score =
  round(average executed Toffoli)
  * (maximum referenced qubit ID + 1)
```

Consequences:

- A paper's logical-qubit count is not automatically the benchmark Q factor.
  Allocation timing and the highest referenced ID matter.
- Worst-case or static Toffoli formulas must be translated into average
  executed Toffoli under benchmark inputs and branches.
- Expected measurement-based cleanup must include its repair branches.
- A primitive improvement must be multiplied by its real invocation count,
  including reverse calls.
- A lower-T fresh-output primitive can lose if its accumulator raises the hard
  allocation peak.

## Evidence translation checklist

For every paper number, identify:

1. primitive input/output map;
2. field or arithmetic representation;
3. clean and dirty ancillas;
4. whether controls are classical, quantum, or absent;
5. whether cost includes inverse/uncompute;
6. whether cost is exact, expected, asymptotic, or estimated;
7. whether output is in-place or fresh;
8. whether the paper counts T gates, Toffoli gates, T-depth, or another metric;
9. conversion and correction costs omitted by local scope;
10. complete-shell call count in this benchmark.

The paper cards keep these boundaries explicit.
