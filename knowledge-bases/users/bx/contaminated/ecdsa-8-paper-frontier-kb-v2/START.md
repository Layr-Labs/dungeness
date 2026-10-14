# Start with evidence, then reopen the architecture

The benchmark is reversible affine addition by a runtime classical point on
secp256k1:

```text
lambda = (target_y - offset_y) / (target_x - offset_x) mod p
x3     = lambda^2 - target_x - offset_x mod p
y3     = lambda * (target_x - x3) - target_y mod p

p = 2^256 - 2^32 - 977
```

The target coordinates are quantum input/output registers. The offset
coordinates are runtime classical-bit registers. The accepted circuit must
clean values, ancillas, transcripts, phases, and reverse errors. The benchmark
score is:

```text
round(average executed Toffoli) * (maximum referenced qubit ID + 1)
```

Read [`evidence/benchmark-contract.md`](evidence/benchmark-contract.md) before
transferring a paper count.

## Stage 1: establish the measured object

If the repository already has a valid candidate:

1. preserve it;
2. measure average executed Toffoli;
3. find the instruction or region that establishes the hard maximum qubit ID;
4. list the values live at that instant;
5. identify the dominant repeated arithmetic shell.

If no valid candidate exists, use one coherent paper-derived spine only long
enough to obtain a valid measured baseline. The closest source-domain spine is
Schrottenloher's compact binary-Euclid history plus linear replay and
pseudo-Mersenne point-addition schedule. Start with the
[`Schrottenloher card`](evidence/papers/01-schrottenloher.md), then verify every
needed detail in its linked page evidence.

This is a bootstrap route, not a conclusion that the spine is optimal.

## Stage 2: diagnose a decision, not a paper

Use [`frontier-map.md`](frontier-map.md) to map the current owner to one
decision dossier:

```text
high history width          -> information location
high inversion arithmetic   -> recurrence/state machine
high controlled-add cost    -> arithmetic control structure
high reduction overhead     -> field representation
high live-output width       -> output placement and dataflow
expensive cleanup           -> measurement scale
high hard-ID peak           -> space-time schedule
paper baseline exhausted    -> cross-paper compositions / after the baseline
```

Read one dossier, then one or two linked operational cards. Search the source
pages only for the precise algorithm, invariant, or boundary condition needed
to make the experiment executable.

## Stage 3: write a bridge hypothesis

Before changing code, state:

```text
base architecture
mechanism to import
input/output register contract
field representation
where discarded information goes
forward protocol
explicit reverse or phase-repair protocol
predicted complete-shell delta_T
predicted hard-ID delta_Q
smallest falsifying test
```

Words such as “adder,” “inversion,” “history,” and “measurement” do not prove
compatibility.

## Stage 4: continue after implementing a paper

Implementing a published architecture is a milestone, not a terminal state.
After every accepted baseline or large improvement:

1. update the T owner and Q owner;
2. choose one untouched decision axis;
3. form a new bridge or representation hypothesis;
4. run the smallest decisive experiment;
5. record why it worked or failed;
6. repeat while a materially different axis and useful budget remain.

Do not continue polishing a paper's own endpoint by default. Reopen the
representation of information, recurrence, output placement, or lifetime
schedule.

## Useful searches

```text
fixed tape replay coefficient multiplication
Dialog length invariant direct division
four phase exact iteration active window
controlled add subtract no carry global correction
dirty ancilla carry venting zero overhead control
measurement based uncomputation expected repair
ghost qubit classical phase debt weighted schedule
Montgomery fresh accumulator copy uncompute
Kaliski pseudo inverse correction point division
exceptional modular addition x plus y equals p
```
