# Experiment map for the current ping-pong architecture

This ranking is an **[INFERENCE]** based on the eight papers and the current local benchmark architecture. Re-profile before implementation.

## Tier 1 — strongest immediate tests

### 1. Replay arithmetic differential audit

Compare every current replay operation with the secp256k1-specific add, double, halve, comparison, and fold constructions in Schrottenloher.

Success condition:

```text
same live layout
lower average executed Toffoli
no new high qubit id
all phase/reverse tests pass
```

Why first: replay is both gate-heavy and peak-owning.

### 2. Peak-local constant/controlled adder substitution

Use Gidney's constant-workspace adder or Litinski's controlled add-subtract only where operand type and controls match exactly.

Precondition: record whether the current primitive already reaches the known lower-cost shape. A theoretically elegant adder that adds a clean register is a loss at the peak.

### 3. Tiny measurement-uncomputation conformance test

Implement the Luongo one-bit lemma in the benchmark IR and verify:

```text
basis states
superpositions
retained measurement result
conditional phase repair
explicit inverse
conditional gate accounting
```

Only then consider a comparator bit, carry bit, or fold predicate.

## Tier 2 — architectural but bounded

### 4. More aggressive walk/replay interleaving

The local implementation already benefits from replay interleaving. Use Spooky Pebbling to reason about the minimum stored frontier, but design around this particular dependency graph.

Do not repeat generic Bennett checkpointing: a local experiment already paid roughly 30% more Toffoli without lowering the peak.

### 5. Recoverability study for implicit/dialog history

Before coding Khattar-style dialog or implicit division, formalize:

```text
state transition
discarded sign/quotient information
reconstruction algorithm
prime-field reversible cost
peak interval
```

If the signs cannot be recovered from surviving state and a smaller side channel, the idea cannot replace the tape.

### 6. Whole-field register demolition

Use Luo-style Hadamard measurement only for a complete obsolete field value that is exactly recomputable from surviving data. Count the classical outcomes and phase-repair recomputation.

## Tier 3 — conditional component studies

### 7. Litinski multiplication shell

Test only if a fresh accumulator can occupy already-free wires and the wrapper can restore or remove the old operand without a second inversion. Otherwise the paper's leading-order Toffoli gain does not translate to the in-place interface.

### 8. Active-window narrowing

Use Luo's active-window proofs to shorten physical lifetimes or operation spans. The current local width schedule already found uniform narrowing ineffective; require a nonuniform, phase-specific proof.

### 9. Häner reconstruction control

Rebuild or model one Häner arithmetic block to validate the benchmark cost model and to provide a stable comparison point. Do not expect this alone to beat the live architecture.

## Explicitly deprioritized

| Idea | Why |
|---|---|
| literal Luo point-add circuit | roughly 70.10M paper Toffolis makes the product uncompetitive |
| generic Bennett checkpointing | already measured negative locally |
| radix-4 ping-pong walk | already tested without a favorable product |
| Kaliski-style explicit coefficient growth | coefficient state increases peak |
| uniform width-schedule narrowing | already failed to lower the relevant peak |
| Karatsuba-2 square | local experiment did not beat the existing square |
| drop-in Litinski multiplier | output placement and cleanup do not match |
| delete sign tape and infer later | no recovery proof; the tape carries lost branch information |

## Experiment record template

```text
source:
node(s):
base commit:
target phase:
peak owner:
information retained/discarded:
phase protocol:
predicted dT:
predicted dQ:
break-even:
small test:
full result:
interpretation:
```
