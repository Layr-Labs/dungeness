# Cross-paper knowledge graph

## Mechanism map

```text
                                  ecdsa.fail
                         fixed-depth ping-pong replay
                                      |
              +-----------------------+-----------------------+
              |                       |                       |
       arithmetic cost           tape / state width      cleanup / phase
              |                       |                       |
   Schrottenloher folds       Schrottenloher history       Luongo MBU
   Litinski add-subtract      Khattar Dialog               Gidney venting
   Gidney const adders        Luo shared EEA               Luo demolition
   Häner Montgomery/fusion    Spooky scheduling            Spooky ghosting
```

## History-representation graph

```text
current sign tape
   |
   +-> Schrottenloher compact branch symbols -> Bézout replay
   |
   +-> Luo explicit shared values -> active-window arithmetic
   |
   +-> Khattar quotient storage -> explicit Bézout coefficients
   |
   +-> Khattar Dialog -> implicit coefficient action
   |
   +-> Spooky checkpoints -> recompute plus phase correction
```

Constraint:

```text
discarded path information
  must become
  another quantum representation
  OR classical measurement outcomes + a phase oracle
  OR recomputation from surviving state
```

## Measurement graph

```text
Luongo one-bit MBU
       |
       +-> Gidney carry venting -> carry-xor repair
       |
       +-> Luo full-register demolition -> recompute field value
       |
       +-> Spooky ghosting -> recompute checkpoint
```

All four require phase correction. Their costs differ mainly in the complexity of the reconstructed predicate.

## Arithmetic graph

```text
quantum-quantum replay add
       |
       +-> Schrottenloher pseudo-Mersenne specialization
       |
       +-> Litinski add/subtract substitution -- requires global correction

classical-constant correction
       |
       +-> Gidney constant-workspace adder
       +-> Gidney zero-cost control
       +-> Luongo predicate MBU

full multiplication
       |
       +-> Litinski schoolbook/Montgomery -- fresh output
       +-> Häner Montgomery/windowed -- integrated shell
       +-> Schrottenloher in-place replay -- closest contract
```

## Scheduling graph

```text
Häner consume-before-uncompute
        -> local lifetime fusion

current replay interleaving
        -> schedule-specific tape reduction

Spooky line frontier
        -> asymptotic design bounds

generic Bennett checkpointing
        -> measured current non-win
```

## Recommended traversal

```text
benchmark-contract
 -> current-benchmark-architecture
 -> mechanism-selection
 -> compatibility-and-conflicts
 -> experiment-priority
 -> selected paper node
 -> smallest falsifying experiment
```
