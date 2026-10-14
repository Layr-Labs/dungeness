# Agent pack

## Start here

1. Read [`paper-matrix.md`](paper-matrix.md) to choose the relevant sources.
2. Read [`concepts/mechanism-selection.md`](concepts/mechanism-selection.md).
3. Follow the selected concept into atomic files under [`nodes/`](nodes/).
4. Use [`sections/`](sections/) for paper-level context.
5. Follow source-page links from the corresponding [`paper-cards/`](paper-cards/).

## Core architectural choices

```text
compact branch transcript and replay      -> Schrottenloher
fresh-output signed multiplication        -> Litinski
one-bit measured cleanup                  -> Luongo
vented-carry classical offset addition    -> Gidney
general ghost-and-recompute scheduling    -> Kornerup et al.
exact shared-register EEA                 -> Luo et al.
implicit transition representation        -> Khattar et al.
integrated Montgomery/Kaliski stack       -> Häner et al.
```

## Before composing mechanisms

Write down:

```text
input representation
output placement
operand types
controls
garbage
measurement outcomes
phase repair
inverse
resource convention
```

Use [`concepts/compatibility-and-conflicts.md`](concepts/compatibility-and-conflicts.md)
as the type checker.

## Research continuation

The papers establish particular constructions. They do not close:

- transcript entropy and reversible coding;
- integer transition alphabets;
- combinations of transcript replay and field demolition;
- exact lifetime sharing without moving-value arithmetic;
- complete-shell combinations of fresh-output multiplication and
  producer-consumer fusion.

See [`concepts/hypotheses.md`](concepts/hypotheses.md) and
[`experiment-map.md`](experiment-map.md).
