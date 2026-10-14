# Start: one spine first, cross-paper research second

The benchmark asks for reversible affine addition on secp256k1:

```text
lambda = (target_y-offset_y)/(target_x-offset_x) mod p
x3     = lambda^2-target_x-offset_x mod p
y3     = lambda*(target_x-x3)-target_y mod p

p = 2^256 - 2^32 - 977
```

**[BENCHMARK]** The target coordinates are quantum input/output registers. The
offset coordinates are runtime classical-bit registers. The accepted circuit
must leave no value, ancilla, transcript, phase, or reverse error. Cost is:

```text
round(average executed Toffoli) * (maximum referenced qubit ID + 1)
```

## Phase A: bootstrap without surveying eight papers

If the repository already contains a valid candidate, preserve it and measure
its current owners. Do not reconstruct an older paper architecture.

If no valid candidate exists, the nearest paper-derived spine is:

```text
Schrottenloher affine dataflow
  -> compact fixed-depth binary-Euclid history
  -> linear coefficient replay
  -> secp256k1 pseudo-Mersenne arithmetic
  -> reverse history cleanup
```

**[INFERENCE]** This is a bootstrap choice, not a declaration that the spine is
optimal. It has a close match to the field, in-place multiplication/division,
and joint T/Q objective. Import only enough to reach a valid measured baseline.

Do not use the eight papers by averaging their architectures. In particular:

- do not add a fresh product register merely because a multiplier paper uses
  one;
- do not replace prime-field arithmetic by polynomial-field counts;
- do not measure garbage without an explicit phase and reverse protocol;
- do not adopt a low-qubit full architecture without costing its complete T
  increase.

## Phase B: reopen the architecture

Once a valid candidate exists, use the papers as coordinates:

| Decision axis | Papers that expose alternatives |
|---|---|
| Reversible information | Schrottenloher, Luo, Khattar, Spooky Pebbling |
| EEA recurrence and state | Schrottenloher, Luo, Khattar, Häner |
| Controlled arithmetic | Litinski, Gidney, Luo, Schrottenloher |
| Reduction representation | Schrottenloher, Litinski, Häner |
| Output placement and dataflow | Schrottenloher, Litinski, Luo, Khattar, Häner |
| Measurement scale | Luongo, Gidney, Luo, Spooky Pebbling |
| Lifetime scheduling | Schrottenloher, Luo, Spooky Pebbling, Häner |

The useful question is not “Which paper is best?” It is:

```text
Which decision currently owns the score, and can a mechanism from another
paper cross the required interface without importing its liabilities?
```

## First frontier action

1. Identify the current T owner and hard-ID owner.
2. Read one matching dossier in [`frontier-map.md`](frontier-map.md).
3. State one bridge hypothesis.
4. Run the smallest decisive experiment.
5. Return to the map after acceptance or rejection.

Useful retrieval queries:

```text
branch tape versus dialog
prime-field transfer quotient sign
fresh accumulator output placement
constant offset zero overhead control
field register demolition phase repair
weighted ghost checkpoint replay
active window hard maximum id
controlled add-subtract global correction
```
