# Operating rules for the eight-paper frontier

The papers are not eight implementation plans to execute in order. They expose
different answers to a small number of design questions.

## Activation gate

Read:

1. `START.md`
2. `frontier-map.md`
3. `RESEARCH_PROTOCOL.md`

Then determine whether a valid candidate already exists.

If no valid candidate exists, use the bootstrap route in `START.md`. Do not read
all ten dossiers first. Establish correctness and a measured baseline.

If a valid candidate exists, profile:

```text
average executed Toffoli owner
hard maximum-qubit-ID owner
values simultaneously live at that peak
most repeated arithmetic contract
cleanup or inverse protocol at that interval
```

Choose one dossier from those facts.

## Treat every import as a graft

Before importing a mechanism from another paper, write:

```text
base architecture
grafted mechanism
input and output contract
information discarded
information retained
recovery or phase mechanism
field representation
forward protocol
explicit reverse protocol
predicted complete-shell delta_T and delta_Q
smallest falsifying test
```

A shared word such as “adder,” “history,” “inversion,” or “measurement” does
not establish compatibility.

## Limit simultaneous novelty

Prefer one architectural spine and one foreign mechanism per experiment. Two
foreign mechanisms are reasonable only when the bridge between them is the
hypothesis being tested.

Do not combine a recurrence rewrite, a measurement protocol, an allocator
rewrite, and a new reduction representation in one candidate. A failure would
be uninterpretable.

## Frontier reset

Implementing one paper successfully is not a stopping condition. After the
first strong valid candidate, select an untouched axis:

```text
information medium
recurrence/state machine
arithmetic control structure
field representation
output placement
measurement scale
lifetime schedule
cross-paper composition
```

Stop an avenue when a decisive test rejects it. Do not stop the whole search
while a materially different axis remains untested and useful budget remains.

## Correctness order

The trusted benchmark dominates every paper and inference. Every retained
candidate must preserve value, ancilla, classical transcript, relative phase,
and forward/reverse behavior.
