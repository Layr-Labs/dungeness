# Knowledge graph

```mermaid
flowchart TD
    PA[Affine point addition]
    IPM[In-place multiplication and division]
    EH[Euclid history]
    HC[History compression]
    BR[Linear replay]
    PM[Pseudo-Mersenne arithmetic]

    PA --> IPM
    IPM --> EH
    EH --> HC
    HC --> BR
    BR --> PM

    LIT[Controlled add-subtract]
    LUO[Shared-register EEA]
    KHA[Dialog transitions]
    HAN[Integrated Montgomery/Kaliski stack]

    LIT --> PA
    LUO --> PA
    KHA --> IPM
    HAN --> PA

    MBU[One-bit measured cleanup]
    VENT[Vented carries]
    DEMO[Field-register demolition]
    SPOOK[Ghosted checkpoints]

    MBU --> PM
    VENT --> PM
    DEMO --> LUO
    SPOOK --> TS[Time-space scheduling]
    HAN --> TS
    EH --> TS

    BOUND[Interface boundaries]
    BOUND --> LIT
    BOUND --> LUO
    BOUND --> KHA
    BOUND --> MBU
    BOUND --> VENT
```

## Main routes

- Point-addition route:
  [`concepts/point-addition.md`](concepts/point-addition.md)
- Representation route:
  [`concepts/history-and-bezout-representations.md`](concepts/history-and-bezout-representations.md)
- Measurement route:
  [`concepts/measurement-assisted-uncomputation.md`](concepts/measurement-assisted-uncomputation.md)
- Scheduling route:
  [`concepts/time-space-scheduling.md`](concepts/time-space-scheduling.md)
- Compatibility route:
  [`concepts/paper-interface-boundaries.md`](concepts/paper-interface-boundaries.md)
