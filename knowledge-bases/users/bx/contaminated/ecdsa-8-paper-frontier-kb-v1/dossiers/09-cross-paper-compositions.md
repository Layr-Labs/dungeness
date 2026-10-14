---
kind: research-dossier
id: cross-paper-compositions
depends_on:
  - information-location
  - arithmetic-control-structure
  - output-placement-and-affine-dataflow
  - measurement-scale
  - space-time-schedule
  - transfer-barriers
---

# Dossier: compose contracts, not headlines

Compatibility is directed. A mechanism may graft cheaply into one architecture
while requiring a reconstruction of another.

## Promising grafts

| Base | Graft | Why it may fit | Decisive condition |
|---|---|---|---|
| Schrottenloher replay | Gidney controlled constant adder | pseudo-Mersenne folds use classical `f` | saves peak scratch or repeated fold T after phase repair |
| Schrottenloher replay | Litinski add-subtract | replay symbols already select signed linear actions | global correction fuses with an existing fold or normalization |
| Any one-bit cleanup | Luongo MBU | exact Boolean predicate already exists | expected repair plus inverse is cheaper than coherent erase |
| Low-T arithmetic spine | Luo active-window bounds | imports liveness metadata without full EEA | active region shortens real scratch or hard ID |
| Affine point-add shell | Luo field-register demolition | an old coordinate may become redundant | exact recomputation is cheaper and release crosses the peak |
| Any arithmetic spine | Häner consumer-aware scheduling | changes lifetimes without changing field algebra | copied result or recomputation is actually removed |
| Compact walk/replay | weighted Spooky schedule | history production and use are line-like | nonuniform recomputation lies below product break-even |
| New prime-field recurrence | Khattar Dialog | one transition record could drive recovery and division | sign/quotient information is uniquely recoverable |

These are **[INFERENCE]** candidates, not established benchmark improvements.

## Compositions that can double-count a saving

### Two ways of storing the same lost information

Keeping a full branch tape and a full Dialog usually duplicates the
reversibility channel. A hybrid is useful only if one representation replaces a
specific interval of the other.

### Two measurement wrappers around one predicate

Luongo MBU and Gidney carry venting share the same phase economy at different
granularity. Applying both to the same carry does not produce two independent
half-cost savings.

### Representation conversion inside a repeated loop

Litinski/Häner Montgomery arithmetic and Schrottenloher pseudo-Mersenne replay
may each be efficient in isolation. Converting every round is likely to erase
the gain. A mixed design needs a long phase boundary.

### Ghosting a state already cheap to recompute

Spooky scheduling matters only when coherent storage is expensive relative to
reconstruction. If a Häner-style dataflow change removes the intermediate
entirely, ghosting it is obsolete.

## Composition protocol

For one candidate:

```text
1. choose the base spine;
2. identify the exact interval being replaced;
3. state the graft's native contract;
4. derive one bridge lemma;
5. include conversion, correction, cleanup, and inverse;
6. predict delta_T and delta_Q;
7. run the bridge falsifier;
8. integrate only if the closed interval wins.
```

Prefer one graft at a time. If two mechanisms are inseparable, compare:

```text
base
base + A
base + B
base + A + B
```

This reveals whether the mechanisms are complementary or merely claim the same
saving.
