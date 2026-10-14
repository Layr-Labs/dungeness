# Operating rules for the research-frontier KB

The dossiers are not a checklist whose completion ends the task. They are
alternative lenses on the same circuit.

## First pass

1. Read `START.md`.
2. Read `frontier-map.md`.
3. Obtain a valid candidate early.
4. Measure the current Toffoli and hard maximum-qubit-ID owners.

## Research pass

Choose a dossier by the current uncertainty, not by paper order:

```text
lost branch information       -> history and recurrence dossiers
replay arithmetic dominates   -> replay compiler and reduction dossiers
peak width dominates          -> scheduling dossier
cleanup dominates             -> measurement dossier
valid but apparently finished -> after-the-paper dossier
```

For every architectural proposal write down:

```text
surviving information
discarded information
recovery mechanism
forward and inverse protocol
predicted delta in executed Toffoli
predicted delta in hard maximum qubit ID
smallest falsifying test
```

## Frontier reset

After reaching a strong valid score, do not conclude merely because the paper's
construction has been implemented. Re-profile and select an untouched axis:

```text
recurrence
history representation
replay algebra
modular correction
measurement protocol
lifetime schedule
affine-shell dataflow
```

Stop an avenue when a decisive test rejects it. Do not stop the overall search
while a materially different frontier remains untested and budget remains.

## Correctness order

The trusted benchmark dominates paper claims and all inferences. Every retained
candidate must pass value, ancilla, phase, and forward/reverse checks.
