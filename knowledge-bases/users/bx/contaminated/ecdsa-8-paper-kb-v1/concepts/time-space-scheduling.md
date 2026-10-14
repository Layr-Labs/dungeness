# Time–space scheduling

## Three levels

### Local lifetime fusion

Häner consumes a product or square before uncomputing it and reuses division workspace.

### History/replay interleaving

The live ping-pong implementation replays some rounds before the tape reaches full length.

### General ghost/checkpoint schedules

Spooky Pebbling gives asymptotic frontiers and lower bounds.

## Current lesson

Generic checkpointing loses because a checkpoint is a wide walk state and recomputation is expensive. Interleaving wins because it exploits exact order compatibility between walk and replay.

Therefore schedule proposals should be expressed as:

```text
dependency order
state width by round
replay footprint by round
recomputation count
maximum ID layout
```

The abstract number of checkpoints is insufficient.
