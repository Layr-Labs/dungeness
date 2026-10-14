---
kind: research-dossier
id: information-location
depends_on: []
---

# Dossier: where should reversible information live?

Every irreversible-looking arithmetic step loses distinctions between possible
preimages. A reversible circuit must preserve those distinctions somewhere.
The papers propose different storage media, not merely different encodings.

## Four information media

| Medium | Source example | What remains | Recovery bill |
|---|---|---|---|
| Coherent branch tape | Schrottenloher binary-Euclid history | branch symbols | reverse walk and coefficient replay |
| Explicit shared state | Luo four-phase EEA | remainders, coefficients, quotient/phase metadata | inverse EEA over shared registers |
| Implicit transition list | Khattar Dialog | ordered invertible transition matrices | replay every transition when a coefficient is needed |
| Classical phase obligations | Luongo, Gidney, Spooky Pebbling | measurement outcomes | recompute a predicate or checkpoint and repair phase |

**[PAPER]** Schrottenloher records three reachable binary-Euclid symbols and
compresses blocks of them. Luo retains explicit quotient-processing state while
sharing shrinking remainders with growing coefficients. Khattar represents an
EEA transform as an ordered Dialog of small matrices over a polynomial-field
construction. Measurement papers exchange coherent garbage for classical
outcomes plus later phase correction.

## Conservation rule

**[INFERENCE]** For a candidate interval, create an information ledger:

```text
pre-state distinctions
  = surviving quantum distinctions
  + coherent history/dialog
  + classical measurement record with phase obligation
  + distinctions exactly recomputable from surviving state
```

Deleting a tape or register without filling the right side is not compression;
it is loss of reversibility.

## Bridge hypotheses

### Branch tape to Dialog

A prime-field transition alphabet might encode both predecessor recovery and
coefficient action more densely than separate branch bits.

Required bridge:

- define integer prime-field transition matrices;
- prove every reachable predecessor is unique;
- encode subtraction direction or sign;
- bound transition storage and replay work;
- show terminal normalization is reversible.

Khattar's polynomial-field counts do not prove this bridge.

### Coherent history to classical ghosts

A produced history block might be measured and released if its value can later
be recomputed from a cheaper checkpoint.

Required bridge:

- retain all measurement outcomes;
- reconstruct the exact history predicate;
- apply its outcome-controlled phase;
- provide an explicit reverse protocol;
- save a hard-ID qubit interval large enough to pay for recomputation.

### Explicit state to shared physical storage

Luo's key reusable idea is not the exact four-phase EEA but a liveness proof:
remainders shrink while coefficients grow. A different recurrence may admit a
similar shared layout if monotone worst-case bounds hold for every input.

## Decisive experiment

For widths 4 through 12, exhaust reachable states and record:

```text
raw information bits retained per round
maximum coherent storage
classical outcomes retained
arithmetic needed for recovery
uniqueness of the inverse
coefficient action supplied by the same representation
```

Reject a representation immediately if two reachable preimages map to the same
surviving state and record, or if its recovery requires a second copy of the
state it was meant to remove.
