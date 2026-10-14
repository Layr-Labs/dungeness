# Decision dossier: recurrence and state machine

The recurrence determines which controls are generated, how much history is
needed, which values shrink, and whether a fixed global schedule exists. It is
usually a larger decision than swapping one adder.

## Source state machines

| State machine | Iteration control | Main stored information | Strong point | Main liability |
|---|---|---|---|---|
| Compact binary Euclid | parity and comparison; probabilistic fixed padding | packed branch tape | cheap decisions and linear replay | approximate capacity and replay tape |
| Four-phase exact EEA | phase, lengths, quotient position | live shared state + logarithmic metadata | exact fixed bound and low width | expensive location-controlled arithmetic |
| Swap-normalized Kaliski | four cases normalized by swaps | active-round controls and coefficient state | common round body; mature prime-field path | `2n` rounds and pseudo-inverse correction |
| Synchronized classical EEA | quotient digits and cycle counter | quotient in shared padding | direct quotient handling | polynomial proof does not transfer directly |
| Division-free Dialog | swap decision and field coefficient | sequence of transition symbols | linear implicit access | polynomial field and coefficient-size mismatch |

Evidence:
[Schrottenloher](../evidence/papers/01-schrottenloher.md),
[Luo](../evidence/papers/06-luo.md),
[Häner](../evidence/papers/08-haner.md), and
[Khattar](../evidence/papers/07-khattar.md).

## Compare recurrences by interfaces

Before replacing a loop, derive:

```text
input normalization
fixed iteration or step bound
per-step transition
halting representation
coefficient sign convention
output representation
history required for inversion
reverse transition
exceptional input handling
```

A recurrence with fewer mathematical iterations can still lose if each
iteration requires wide quantum addressing or produces a large quotient.

## Normalize cases before optimizing arithmetic

Häner's Kaliski design uses controlled swaps to place four cases into one common
arithmetic body. Schrottenloher similarly exposes parity and ordering before a
common subtract/halve step. Luo encodes phase and length so one global circuit
acts on branches at different logical positions.

**[INFERENCE]** Search for a normalization that reduces the number of distinct
controlled arithmetic bodies, even if it adds cheap swaps or metadata. This can
make later adder improvements multiply across more calls.

## Fixed-time versus exactness

- Schrottenloher chooses iteration and register-padding margins calibrated on
  random inputs. Failure probability belongs to the algorithm.
- Luo proves an exact common upper bound below `6.316n` steps.
- Häner runs a fixed `2n` Kaliski schedule and carries a pseudo-inverse factor.
- Khattar proves fixed polynomial schedules, including a `6n` bound for its
  synchronized construction.

Do not compare only constants. Record whether the benchmark permits
probabilistic failure and how it scores rare branches. Exactness can change both
the test oracle and average execution count.

## Quotient granularity

Binary recurrences avoid large quotient digits but take more transitions.
Classical EEA extracts a quotient, potentially reducing iterations while
requiring storage and quantum arithmetic for that quotient. A middle ground is
a bounded-radix digit:

```text
one bit per step
small signed digit per step
run-length encoded repeated halve/subtract
windowed quotient digit
full quotient
```

**[INFERENCE]** A small signed transition alphabet may reduce transcript
entropy and replay calls simultaneously. Its value depends on reversible digit
selection and worst-case capacity.

## State-machine experiments

1. Implement each recurrence classically over small primes with the exact
   benchmark sign and division convention.
2. Record distributions of transitions, iterations, digit sizes, and active
   widths over benchmark-like inputs.
3. Derive a reversible state tuple and explicit inverse for one promising
   transition.
4. Estimate:

```text
steps * cost_per_step
history_bits
replay_steps * cost_per_replay
metadata and addressing
```

5. Build a small-width circuit for the transition and reverse it.
6. Replace only the inversion core behind the existing public ABI.

## High-value bridge hypotheses

- compact binary decisions with Luo-style exact active-window bounds;
- Kaliski case normalization with Gidney constant-offset arithmetic;
- a prime-field small-digit Dialog replayed directly onto the numerator;
- quotient stored in proven shrinking-register padding rather than a separate
  register;
- coarse checkpoints plus recomputation instead of every transition symbol.

Each is an inference. None of the papers establishes the combined result.
