# Decision dossier: where does reversible information live?

Every reversible optimization pays for information somewhere. The important
choice is not simply “store garbage or recompute it,” but which representation
lets the downstream operation consume that information most cheaply.

## Four media exposed by the papers

| Medium | Source example | Quantum-space behavior | Recovery cost / obligation |
|---|---|---|---|
| Packed branch transcript | [Schrottenloher](../evidence/papers/01-schrottenloher.md) | grows as remainders shrink; fixed tape about `2.355n` | replay linear updates, then reverse Euclid |
| Shared live algebraic state | [Luo](../evidence/papers/06-luo.md) | remainders, coefficients, quotient, and lengths overlap | high per-step location-controlled arithmetic |
| Linear transition sequence | [Khattar](../evidence/papers/07-khattar.md) | transition symbols replace explicit Bézout object | apply matrices in order; prime-field transfer unproven |
| Classical phase obligation | [Gidney](../evidence/papers/04-gidney.md), [Spooky](../evidence/papers/05-spooky-pebbling.md) | measured qubits become reusable; classical outcomes remain | recompute deleted function and repair phase |

These are not mutually exclusive. A circuit may store coarse transition
symbols, keep a small live state, and vent selected local flags.

## Diagnose the current representation

For the dominant reversible loop, write:

```text
logical decision made each step
number of possible step symbols
stored physical bits per symbol
whether symbols are independent
whether their distribution is skewed
when each symbol is last needed
consumer of the symbol
cost to recompute the symbol from surviving state
```

This distinguishes several losses:

- **coding loss**: more bits are used than the symbol entropy requires;
- **lifetime loss**: bits remain allocated after their final consumer;
- **semantic loss**: the circuit stores a result even though the consumer only
  needs the transformation that produced it;
- **phase opportunity**: a recoverable Z-basis function is stored as a qubit
  although a measurement record and later repair might suffice;
- **recomputation loss**: aggressive deletion repeats an expensive computation
  more often than the saved hard-ID interval justifies.

## The branch-tape question

Schrottenloher's tape stores `(b0, b0&b1)` for each binary-Euclid step and packs
three ternary-valid pairs into five bits. The source itself distinguishes the
information estimate near `2.12n` from the implemented fixed tape near
`2.355n`. That gap is a concrete research coordinate, not proof that a better
quantum code exists.

Candidate alternatives:

1. larger fixed blocks with a denser reversible code;
2. two-stream storage, separating the common parity sequence from rarer swaps;
3. a variable-rate queue plus a bounded overflow path;
4. transition symbols that combine several Euclid steps;
5. recompute cheap decisions while storing only expensive or ambiguous ones;
6. replace the tape with a direct linear-transition representation.

For each, cost the reversible encoder, random access or reverse iteration,
fixed-capacity failure behavior, and cleanup. Classical compression ratio alone
is not enough.

## The implicit-result question

Khattar's Dialog asks whether the consumer needs an explicit inverse or only
the action of the EEA transformation on another value. Schrottenloher already
uses a related principle: replaying the stored decisions on `(y,0)` performs an
in-place multiplication.

**[INFERENCE]** The benchmark's mathematical use is division
`(target_y-offset_y)/(target_x-offset_x)`. This suggests treating “produce the
inverse” as an optional ABI. A direct division transition may reduce an
intermediate value even when it does not reduce the information needed to
clean the EEA.

## The phase-debt question

Measurement is useful when:

```text
deleted value is recoverable from surviving labels
classical outcome can remain live
freed qubits are used in the standard basis
phase repair can occur before incompatible basis use
recomputation is cheaper than retaining qubits at the hard-ID peak
```

Use [Luongo](../evidence/papers/03-luongo.md) for one Boolean flag,
[Gidney](../evidence/papers/04-gidney.md) for structured carry strings,
[Luo](../evidence/papers/06-luo.md) for a complete field register, and
[Spooky Pebbling](../evidence/papers/05-spooky-pebbling.md) for scheduling many
such obligations.

## Smallest decisive experiments

1. Instrument the current history object: logical symbols, allocated bits,
   dynamic use count, and lifetime peak.
2. Build a classical encoder/decoder for one alternative symbol code and prove
   reverse traversal.
3. Replace only a short block of history at small width; test forward, reverse,
   and capacity failure.
4. Identify one stored flag with a cheap recomputation and test one-bit MBU.
5. Compare complete-shell `delta_T * Q + T * delta_Q`, not tape width alone.

## Stop conditions for this axis

Stop a representation avenue when its encoder/replay overhead exceeds the
maximum product benefit, its capacity cannot meet correctness requirements, or
its recovery labels are unavailable. Then try another medium; do not conclude
that the current tape is globally optimal.
