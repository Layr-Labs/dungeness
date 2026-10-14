# Current benchmark architecture

## Active design

**[BENCHMARK]**

```text
fixed-depth signed binary-GCD walk on (u,v)
  -> sign/history tape
  -> coefficient replay
  -> reverse walk and cleanup
```

Both division and multiplication traverse this machinery. Replay is interleaved around tuned checkpoints to reduce the simultaneous tape and walk footprint.

## Why the tape exists

The update chooses a sign so an odd combination can be halved. For the present recurrence, both candidate signed preimages of the post-step state remain valid. The post-step values therefore do not determine the sign.

Consequently:

```text
discard sign
recompute sign from final values
```

is impossible without additional side information or a changed recurrence.

## Peak and cost

The tape is live with replay registers and carry/fold workspace. Replay is also the largest nonlinear-work block.

This makes two kinds of improvements unusually valuable:

- a primitive that lowers Toffoli without adding peak wires;
- a schedule/representation that shortens the simultaneous tape–replay interval.

## Established local evidence

- replay interleaving produced a trusted product win;
- generic checkpointing did not;
- radix-4 did not;
- growing explicit coefficients moved the peak rather than removing it;
- uniform width narrowing crossed correctness margins;
- square optimization matters only after its phase becomes the global peak.

## Rule for older notes

Notes about the legacy trailmix/dialog route are historical. Re-derive their lower bounds before applying them to ping-pong.
