# Producer-consumer and lifetime optimization

The strongest savings can appear between routines rather than inside either routine.

[KB-HAN-03](../nodes/producer-consumer-and-workspace-reuse.md) gives two concrete patterns:

- consume the multiplication result by adding it into the destination before reversing multiplication garbage;
- clear registers holding known values and borrow them for modular multiplication before completing inversion cleanup.

These optimizations require an explicit lifetime graph:

```text
producer computes value + garbage
        ↓
consumer uses value while garbage is live
        ↓
producer reverses and clears garbage
```

This interacts with measurement-assisted methods. A register freed by [ghosting](../nodes/ghosting-transformation.md) or [venting](../nodes/carry-venting-identity.md) is reusable only if its phase-debt record is tracked and repaired by the required deadline.

Cost arithmetic on isolated black boxes cannot reveal these savings; the producer and consumer interfaces must expose result, garbage, known-value, and correction-state lifetimes.
