# Decision dossier: choose the scale of measurement-based deletion

The source set contains measurement protocols at four scales. They share a
principle—turn recoverable Z-basis information into a classical phase
obligation—but their costs and preconditions differ.

## Scale ladder

| Scale | Source | Deleted object | Repair mechanism | Cost form |
|---|---|---|---|---|
| one bit | [Luongo](../evidence/papers/03-luongo.md) | comparator or reduction flag | run its self-inverse computation on one outcome | half inverse cost in expectation |
| structured bit stream | [Gidney](../evidence/papers/04-gidney.md) | carry qubits | carry-XOR plus classically controlled phases | deterministic linear protocol with random phase bits |
| full field register | [Luo](../evidence/papers/06-luo.md) | old multiplicand/dividend | recreate full word, apply `Z_b`, uncompute | extra multiplication/recomputation |
| arbitrary checkpoint | [Spooky](../evidence/papers/05-spooky-pebbling.md) | intermediate state block | replay dependency subgraph and unghost | schedule-dependent time-space tradeoff |

Choose the smallest scale that removes the actual Q owner.

## Common semantic core

Suppose a register contains a deterministic standard-basis function `g(x)` of
surviving labels `x`. Hadamard-basis measurement returns classical bits `b`
and resets the logical register, but leaves:

```text
phase = (-1)^(b dot g(x))
```

To finish:

1. retain `b`;
2. keep enough information to recompute `g(x)`;
3. reuse freed qubits only in an allowed basis regime;
4. later recreate `g(x)`;
5. apply `b`-controlled Z corrections;
6. uncompute the recreation.

If any step is missing, the operation is not a valid deletion in superposition.

## One-bit MBU

Use Luongo's lemma when:

- the garbage is one Boolean value;
- an inverse comparator or Boolean computation already exists;
- that computation is self-adjoint or can be placed in the required repair
  pattern;
- average executed gates count in the benchmark.

The expected saving is half of the final cleanup computation, not half of the
whole modular operation.

First targets:

```text
overflow flag
modulus-subtraction flag
range-test flag
outer exceptional-case flag
```

## Carry venting

Use Gidney's construction when the garbage is specifically the carry process
of adding a classical offset. Carries are recoverable from the final target and
offset through the paper's complement identity. The specialized carry-XOR
repair is cheaper than treating each carry as an independent general flag.

Do not generalize the result to quantum-quantum addition without deriving a new
recovery identity.

## Full-register demolition

Use Luo's pattern when a fresh result is available but the old target register
blocks cleanup. The old word can be measured and reset, allowing it to serve as
workspace for reversing the producer. Phase repair then recomputes the entire
old word from surviving input and result.

This is attractive only if:

```text
freed register removes the hard-ID peak
recomputation is not already the T owner
old value is uniquely recoverable
classical measurement storage is acceptable
```

## Global ghost scheduling

Spooky pebbling applies when several large temporaries compete over time.
Build a weighted dependency graph rather than assuming a uniform line:

```text
node Q weight
forward computation T
uncomputation T
phase-repair T
last standard-basis-safe interval
measurement record size
```

Search for one checkpoint whose removal changes the high-water allocation.

## Decision procedure

1. Identify the exact register/flag owning Q or cleanup T.
2. Prove it is a function of surviving distinct labels.
3. Select the smallest applicable protocol.
4. Write the phase equation.
5. Implement all measurement outcomes in a small-width test.
6. Test interference-sensitive behavior, not only basis-state values.
7. Measure expected executed Toffoli and maximum ID.

## Failure modes

- resetting a measured register without retaining outcomes;
- reusing ghosted qubits in an incompatible basis;
- losing the labels needed for recomputation;
- counting only the favorable measurement branch;
- applying one-bit MBU independently to correlated multi-bit garbage without a
  valid joint phase repair;
- freeing logical width below an unchanged maximum-ID allocation;
- allowing measurement records to outlive the run without a cleanup plan.

## Cross-scale hypotheses

- one-bit MBU for the reduction flag inside a vented constant adder;
- carry venting inside a pseudo-Mersenne correction while retaining exact
  equality handling;
- full-register demolition around Litinski's fresh multiplier;
- spooky scheduling for when to retain or demolish the transcript/replay
  workspace;
- a mixed protocol that stores rare transition symbols and ghosts common
  recoverable flags.
