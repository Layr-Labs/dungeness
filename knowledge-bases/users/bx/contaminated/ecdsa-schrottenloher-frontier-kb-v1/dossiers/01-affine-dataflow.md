---
kind: research-dossier
id: affine-dataflow-frontier
depends_on: []
---

# Dossier: is the affine dataflow itself optimal?

## Established construction

**[PAPER]** For distinct x-coordinates:

```text
lambda = (y2-y1)/(x2-x1)
x3     = lambda^2-x1-x2
y3     = lambda*(x1-x3)-y1
```

The paper arranges these operations around an in-place multiplication primitive
and its inverse. This avoids retaining a standalone modular inverse.

**[BENCHMARK]** The offset coordinates are already available as runtime
classical-bit registers. Paper lookup machinery is not required.

## The unresolved boundary

The formula does not uniquely determine:

- which x-difference representation survives division;
- whether the slope is stored explicitly or represented through another pair;
- when the original target coordinates cease to be needed;
- whether square, multiply, and final correction must be separate calls.

The reversible cost is determined by these lifetime choices.

## Recovery identities

Forward slope:

```text
lambda = (target_y-offset_y)/(target_x-offset_x)
```

Slope reconstructed from the output:

```text
lambda = (offset_y+result_y)/(offset_x-result_x)
```

**[INFERENCE]** The second relation can be treated as a cleanup oracle, but it
may cost another inversion-grade traversal. A useful alternative must change
the surrounding dataflow enough that cleanup is cheaper than retaining slope.

## Research moves

1. Write the complete affine shell as a sequence of reversible affine and
   bilinear maps, including where each original value is recoverable.
2. Search for adjacent operations that use the same addend, negation, or
   modular correction and can be algebraically fused.
3. Compare complete shells, not isolated multiplication counts.
4. Test whether a different sign convention for the x- or y-difference makes
   replay or square accumulation cheaper.

## Decisive test

Build a lifetime table for every 256-bit value. A proposal is interesting only
if it removes a live field register at the peak or deletes a repeated
full-width arithmetic shell without introducing an equally expensive inverse.
