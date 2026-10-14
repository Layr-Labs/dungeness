---
title: Current local ecdsa.fail ping-pong architecture
source: local benchmark repository and trusted memory notes
tags: [source, benchmark, pingpong, replay, tape]
---

# Benchmark source: live ping-pong path

## Active path

**[BENCHMARK]**

```text
build_circuit
  -> point_add::build()
  -> pingpong_div::build_pingpong_point_add()
```

The older trailmix/dialog path is legacy. Local notes that declare floors for that older path are not automatically floors for ping-pong.

## Architecture

```text
fixed-depth signed binary-GCD-style walk on (u,v)
  -> one sign/history qubit per round
  -> coefficient replay consumes the tape
  -> reverse walk restores the denominator and clears the tape
```

Divide and multiply traversals share the machinery. Replay is interleaved with the walk around tuned checkpoints so some rounds execute before the tape reaches full length.

## Score and correctness

**[BENCHMARK]**

```text
score = round(average executed Toffoli) × (maximum referenced qubit id + 1)
```

- Only executed CCX/CCZ operations are charged.
- Conditional execution changes average Toffoli cost.
- Qubit cost is a hard maximum referenced ID, not merely the conceptual live set.
- The evaluator runs 9,024 deterministic, circuit-seeded shots.
- Any coordinate, phase, ancilla, or reverse failure rejects the candidate.

## Measured historical observations

Trusted local notes document successive states, including:

```text
944,129.342 executed Toffoli × 1,279 qubits
= 1,207,540,991
```

for the first interleaved-replay version, and:

```text
921,558 executed Toffoli × 1,278 qubits
= 1,177,751,124
```

for a later tuned version. The current source has evolved again; these are evidence about mechanism and tradeoff, not a promise of the present score.

## Established local constraints

- Interleaving replay saved 21 qubits for about 4.2k additional executed Toffolis in one trusted version.
- Generic Bennett/hierarchical checkpointing added about 30% Toffoli without lowering the realized peak.
- Radix-4 ping-pong did not improve the product.
- Kaliski-style coefficients grew enough to replace the tape as the peak owner.
- Karatsuba-2 squaring was unfavorable.
- Uniform width-schedule narrowing crossed a correctness cliff.
- The current recurrence loses the sign branch from the post-step value state; both candidate preimages remain valid, so the sign bit cannot simply be recomputed.

## Consequence for paper transfer

Every proposal must target this path and answer:

```text
Does it lower the hard max qubit ID?
Does it alter the tape/replay interval?
What information is discarded?
How is phase repaired?
What is the average executed, not emitted, Toffoli delta?
```
