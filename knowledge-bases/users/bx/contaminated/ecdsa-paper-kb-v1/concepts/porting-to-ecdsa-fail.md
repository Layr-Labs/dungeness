# Porting the paper to ecdsa.fail

## Executive conclusion

**[INFERENCE]** The paper is highly relevant, but the correct port target is the dialog/history-based in-place multiplier and its arithmetic—not the windowed lookup wrapper.

The cleanest pre-paper benchmark snapshot is public-launch commit:

```text
e8ce2c9edc2ae13a3e0f5a1688e6537f5de45247
```

Its recorded baseline is:

```text
Toffoli = 3,942,753
qubits  = 2,715
score   = 10,704,574,395
```

That code already contains a heavily optimized Kaliski-based affine adder and Solinas arithmetic, so the paper is not a beginner tutorial for the repository. Its primary new lever is changing how inversion/multiplication state is represented.

## Transfers directly

- affine addition dataflow;
- in-place multiplication as the central abstraction;
- fixed-step binary Euclid;
- recording branch symbols instead of carrying Bézout coefficients alongside Euclid;
- replaying symbols on `(y,0)`;
- shrinking `u,v` and reusing high wires for history;
- 3-symbol/5-bit history compression;
- phase-dependent adder selection;
- pseudo-Mersenne fold by `f=2^32+977`;
- early replay handling for `x+y=p`;
- measurement-based uncomputation;
- approximate MSB comparisons, if benchmark-safe.

## Does not transfer directly

- 16-bit window register;
- three table lookups and unlookups;
- compile-time constant point coordinates;
- paper's point-at-infinity control;
- paper resource totals as benchmark scores;
- random-input failure probability as a validity criterion;
- Qarton's register order and backend selection APIs.

## Repository reconnaissance checklist

Before writing code, locate:

```text
point-add top-level schedule
inversion/in-place division implementation
modular add/sub
modular double/halve
constant add/sub
comparison and flag uncompute
measurement/AND uncompute
qubit allocator and free semantics
conditional gate accounting
peak diagnostics
reduced and full benchmark commands
```

Classify each paper primitive as:

```text
already present
present but exact/expensive
present with different convention
missing
unsafe under benchmark semantics
```

## Recommended port sequence

### Phase 0: establish reproducibility

- Freeze a commit.
- Run the untouched benchmark.
- Record `score.json`, compiler/toolchain, and git status.

### Phase 1: classical model

Add a test-only model for:

- history creation;
- reverse history;
- replay;
- inverse replay;
- full in-place multiply.

Exhaust small widths and random 256-bit inputs.

### Phase 2: exact uncompressed history circuit

Implement fixed-step Euclid with two bits per iteration and no approximation. This will not be competitive; its purpose is to establish reversible conventions.

### Phase 3: exact replay

Use exact modular double/add and verify forward/inverse composition. Integrate at a microbenchmark or one isolated call site.

### Phase 4: 3-to-5 compression

Port the five-Toffoli compressor or synthesize an equivalent circuit in the benchmark IR. Exhaust all valid blocks and inverse paths.

### Phase 5: register sharing

Introduce a static width schedule. Start conservatively and instrument actual high-bit occupancy in a classical model.

### Phase 6: secp256k1 replay arithmetic

Use overflow folding by `f`, initially with full carry coverage. Then reduce low-slice width only after passing full validation.

### Phase 7: measurement uncomputation

Replace eligible comparator/AND cleanup. Verify phase tests at every step.

### Phase 8: full point-add integration

Replace one existing inversion/multiplication pathway at a time. Reuse the existing affine cleanup identities.

### Phase 9: tune approximation

Tune in this order:

```text
carry slice
comparison width
u/v padding
iteration count
early x+y=p-safe window
```

Never tune multiple failure parameters in one patch.

## Shorter-term experiments

A full architecture port may exceed a single agent run. The paper also suggests smaller bounded experiments:

1. identify full-modulus corrections in replay-like phases and replace them with exact Solinas folds;
2. use phase-local workspace to switch selected CDKM adders to Gidney/hybrid;
3. truncate comparisons already guarded by empirical high-bit margins;
4. fuse compare/reduction/uncompare;
5. specialize exceptional-case handling to a short initial prefix;
6. use measurement-based cleanup for comparator outputs;
7. reuse known `0`, `1`, or `p` endpoint registers.

The launch baseline already implements many Solinas and MBU ideas, so inspect before duplicating them.

## Success criteria

A convincing paper-enabled result has:

- same frozen base commit as control;
- same agent model, prompt, and budget;
- no external web access in either arm;
- the KB as the only intentional information difference;
- a valid full benchmark score;
- a source diff that can be attributed to paper-derived ideas;
- preferably multiple paired trials because agent runs are stochastic.

One paired trial is a pilot, not a definitive evaluation.
