# Resource and score model

## Paper-level picture

The paper's selected space design is dominated by the replay phase:

```text
history tape: ~2.355n + O(sqrt(n))
two modular registers: 2n
small controls/workspace
```

At `n=256`, the code-level figures are:

```text
tape = 670
pair = 512
base = 1182
reported total ~= 1192-1195
```

The gate-efficient variant spends about 256 more qubits to replace low-space adders/comparators with Gidney variants.

## Paper hot spots

For space-optimized secp256k1:

```text
54% replay/Bézout reconstruction
36% history/GCD construction
39% controlled modular add (including inverse)
22% hybrid adder
19% controlled swaps
15% constant adders
 9% squaring
 8% double/halve
```

Percentages overlap because subcomponents are nested.

## Benchmark product objective

Let base score be:

```text
S = T*Q
```

A candidate wins when:

```text
(T+dT)(Q+dQ) < TQ
```

Exact break-even:

```text
dT < -T*dQ/(Q+dQ)
```

For small changes:

```text
dT/T + dQ/Q < 0
```

Record the exchange rate before each experiment.

Example at the public launch baseline:

```text
T = 3,942,753
Q = 2,715
S = 10,704,574,395
```

One qubit is worth roughly:

```text
T/Q ~= 1,452 Toffolis
```

Thus adding 256 qubits requires saving roughly 337k Toffolis just to break even:

```text
T - T*Q/(Q+256) ~= 339k
```

The paper's gate-efficient tradeoff may win on Toffoli but lose or win on product depending on the starting implementation.

## Emitted versus executed gates

The benchmark may support:

- operations conditioned on classical input bits;
- measurement-conditioned correction;
- shot-dependent branches.

Therefore:

```text
emitted Toffoli != average executed Toffoli
```

Measure both if diagnostics exist, but optimize the canonical executed metric.

## Peak-width reasoning

A wire saving counts only if it lowers the maximum referenced/live width seen by the evaluator.

Common non-wins:

- freeing wires outside the peak region;
- replacing one allocation while a pool expands elsewhere;
- reducing active count but leaving a high qubit id referenced;
- adding a low-gate variant that increases the global peak;
- moving work from one phase to another without changing the max.

Instrument peak ownership or phase-local peaks before redesigning storage.

## Paper-to-launch theoretical comparison

Public launch baseline:

```text
3,942,753 Toffoli * 2,715 qubits ~= 10.70e9
```

Paper-v1 space point, naively multiplied:

```text
~2.385e6 * 1,192 ~= 2.84e9
```

Later companion-code space point:

```text
2,304,135 * 1,195 ~= 2.75e9
```

These are not directly comparable because the ABI and cost semantics differ, but they show that the architectural upside is large enough to justify a port study.

## Optimization order after a working port

1. replay controlled modular add;
2. history subtraction/hybrid adder;
3. controlled swaps;
4. tape encode/decode fusion;
5. double/halve;
6. square-add;
7. lookup logic only in a windowed-Shor setting, not this benchmark ABI.
