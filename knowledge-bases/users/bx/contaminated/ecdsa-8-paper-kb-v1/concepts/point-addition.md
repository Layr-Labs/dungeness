# Reversible affine point addition

## Mathematical formulas

For affine points `P1=(x1,y1)` and `P2=(x2,y2)` with `x1 != x2`:

```text
lambda = (y2-y1) * (x2-x1)^-1 mod p
x3     = lambda^2 - x1 - x2 mod p
y3     = lambda*(x1-x3) - y1 mod p
```

The expensive part is not the formula itself. It is computing and then erasing `lambda` reversibly without retaining a large amount of garbage.

## Paper schedule

**[PAPER]** The paper uses three accesses to the selected constant point:

```text
1. load (x1,y1), subtract it from the target, unload
2. divide y-difference by x-difference in place
3. load 3*x1, update x accumulator, unload
4. controlled square/subtract
5. in-place multiply by the updated x accumulator
6. controlled negation
7. reload (x1,y1), finish x/y, unload
```

The schedule is designed so the same in-place multiplication primitive, forward or inverse, handles both appearances.

## Benchmark adaptation

**[BENCHMARK]** The offset coordinates are already present as classical bit registers. There is no `w`-bit index and no lookup table. Replace paper lookups with reversible arithmetic against classical-bit registers.

**[INFERENCE]** Preserve the paper's algebraic dataflow where it reduces live quantum state, but do not port lookup machinery.

## Two useful identities

Forward slope:

```text
lambda = (target_y - offset_y) / (target_x - offset_x)
```

Slope recovery from output:

```text
lambda = (offset_y + result_y) / (offset_x - result_x)
```

The second identity supports cleanup of a temporary slope register. Existing benchmark implementations often use two inversion-like phases for this reason.

## Architectural question

The paper's `IPModMul` maps:

```text
|x,y> -> |x, x*y>
```

and its inverse maps:

```text
|x,y> -> |x, y*x^-1>
```

This matches the reversible affine schedule directly. The highest-value port is therefore the in-place multiplier, not the top-level window controller.

## Special cases

The paper neglects doubling, opposite points, and most point-at-infinity cases because they occur with negligible probability in Shor's random path; it explicitly handles the zero window entry.

The benchmark defines its own input generation and expected behavior. Follow the harness rather than assuming the paper's validity domain. If a proposed approximation depends on excluding a case, prove the harness excludes it or test it explicitly.
