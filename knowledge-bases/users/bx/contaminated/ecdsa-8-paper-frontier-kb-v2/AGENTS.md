# Operating rules for this knowledge base

This KB is an evidence ladder. Use the smallest layer that can answer the
current question, but descend whenever implementation depends on a detail.

## Retrieval ladder

1. Read `START.md`, `frontier-map.md`, and the benchmark contract.
2. Select one decision dossier from measured owners.
3. Read the linked paper card for the candidate mechanism.
4. Follow page links for exact algorithms, formulas, edge cases, and inverse
   behavior.
5. Use the raw PDF when layout, a circuit diagram, or extraction ambiguity
   matters.

Do not survey all 227 pages before producing a baseline. Do not rely on a
one-paragraph synthesis when implementing a reversible protocol.

## Search tactics

The source corpus is page-addressable Markdown, so search exact technical
phrases and symbols alongside the paper or mechanism name:

```text
Schrottenloher Algorithm 3 replay
Schrottenloher exceptional x plus y q
Litinski ModMultStep correction Montgomery
Luongo two-sided comparator measurement uncomputation
Gidney venting carry xor repair dirty
spooky ghost phase b dot y
Luo Work1 Work2 length register active window
Khattar Dialog transition matrix length
Häner Kaliski pseudo inverse uncompute
```

If a search result is a page extraction, inspect its adjacent page when the
sentence begins or ends mid-argument.

## Evidence and inference

- Preserve `[EVIDENCE]` and `[INFERENCE]` distinctions in notes.
- Treat formulas as local to the source paper's register contract and cost
  model until translated explicitly.
- Prefer source-linked claims over memory.
- If extraction and a rendered equation disagree, the PDF is authoritative.
- Never describe a probabilistic or expected cleanup as exact without its
  branch protocol.

## Every mechanism is a graft

Before importing a mechanism, record:

```text
base architecture
grafted mechanism
input and output placement
clean and dirty ancilla requirements
classical versus quantum controls
representation before and after
information retained or discarded
cleanup / inverse / phase-repair path
complete-shell use count
delta in average executed Toffoli
delta in maximum referenced qubit ID
```

A local primitive win can lose after conversion, copy/uncompute, fresh-output
space, control synthesis, or cleanup.

## Limit simultaneous novelty

Prefer one architectural spine plus one foreign mechanism per experiment. Use
two foreign mechanisms only when their interface is the hypothesis being
tested. A recurrence rewrite, allocator rewrite, measurement protocol, and
field-representation change in one patch cannot produce interpretable
evidence.

## Prevent premature stopping

After a paper implementation succeeds, explicitly test at least one axis that
the paper treats as fixed:

- information medium;
- recurrence/state machine;
- control structure;
- field representation;
- output placement;
- cleanup scale;
- lifetime schedule;
- composition with a mechanism from another paper.

An avenue may stop after a decisive rejection. The research run should not
stop merely because the current paper has reached its own conclusion.

## Correctness order

The benchmark oracle dominates every paper and every dossier. Validate:

1. forward values;
2. reverse values;
3. clean ancillas and transcripts;
4. relative phase where measurement or basis changes occur;
5. exceptional modular and elliptic-curve cases;
6. average executed Toffoli and hard maximum qubit ID.
