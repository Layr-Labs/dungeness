# Paper Knowledge Pack for ecdsa.fail

Use this as an implementation brief, not as proof. The only proof of a candidate is a passing untouched full benchmark.

## 0. Mission and evidence rules

Improve the secp256k1 point-addition score:

```text
score = average executed Toffoli * peak qubits
```

Preserve:

- all affine outputs;
- reversibility;
- every freed/non-output ancilla at zero;
- phase cleanliness;
- forward followed by reverse identity.

Edit only paths allowed by `benchmark.json`. Do not change the harness or generated score. Run the full benchmark before finishing.

Knowledge labels:

- **[PAPER]** arXiv:2606.02235v1.
- **[CODE]** authors' Qarton implementation.
- **[BENCHMARK]** ecdsa.fail repository/harness.
- **[INFERENCE]** hypothesis to test.

## 1. First map the repository

Before changing code, locate:

```text
top-level affine point-add schedule
inversion or in-place division
modular add/sub
modular double/halve
constant add/sub
comparison and flag uncompute
measurement-based uncomputation
qubit allocator/free semantics
classical-bit conditioned gates
peak-width diagnostics
full benchmark command
```

Search for existing Solinas/pseudo-Mersenne reduction, Kaliski/Euclid, history/dialog tape, compressed symbols, Gidney/CDKM adders, and phase-safe measurement cleanup. Do not duplicate an existing optimization.

## 2. Benchmark versus paper

**[BENCHMARK]** ABI:

```text
target_x: 256 qubits
target_y: 256 qubits
offset_x: 256 classical bits
offset_y: 256 classical bits
```

Output `target + offset`.

The paper studies a windowed circuit:

```text
|i>|R> -> |i>|R+P_i>
```

with three table lookups. That wrapper does not transfer: the benchmark offset is runtime classical coordinate data, not a lookup index or compile-time point.

What transfers is the paper's in-place multiplier and arithmetic architecture.

The paper tolerates rare random-input failures. The benchmark requires 9,024/9,024 shots. Paper parameters may need larger margins.

## 3. secp256k1 facts

```text
p = 2^256 - 2^32 - 977
  = 2^256 - 4,294,968,273
f = 2^32 + 977
a = 0
b = 7
2^256 == f mod p
```

Affine formulas for distinct non-opposite points:

```text
lambda = (y2-y1) * (x2-x1)^-1 mod p
x3     = lambda^2 - x1 - x2 mod p
y3     = lambda*(x1-x3) - y1 mod p
```

Useful cleanup identity:

```text
lambda = (offset_y + result_y) / (offset_x - result_x)
```

The expensive reversible problem is computing and erasing `lambda`.

## 4. Paper's central architecture

### 4.1 Fixed-step Euclid creates a history

**[PAPER]** Start with `(u,v)=(p,x)`, with `u` odd. For a fixed number of iterations:

```text
b0 = v & 1
b1 = (u > v)
record b0 and (b0 & b1)
if b0 & b1:
    swap(u,v)
if b0:
    v -= u          # ordinary integer subtraction
v >>= 1             # ordinary integer shift
```

With enough iterations, end at `(1,0)`.

Only three record symbols occur:

```text
(0,0), (1,0), (1,1)
```

### 4.2 Replay reconstructs Bézout action

Read records in reverse:

```text
s = 2*s mod p
if b0:
    s = s+r mod p
if b0 & b1:
    swap(r,s)
```

This phase uses modular arithmetic.

**[CODE]** In the released convention, replay initialized with `(y,0)` produces `(0,x*y mod p)`. Inverse replay performs division by `x`.

Verify direction with a classical model; comparison and traversal conventions can flip multiplication/inversion.

### 4.3 In-place multiplication

```text
input x,y
d = History(x)          # x's storage is converted/reused as history
Replay(d,y,tmp=0)       # gives y=0,tmp=x*y
swap(y,tmp)
release tmp
x = inverse_History(d)
output x,x*y
```

Inverse the complete circuit to map `y -> y*x^-1`.

The key cost advantage: history construction runs forward/backward, but coefficient replay runs once; `u,v` and Bézout values are not all live together.

## 5. Concrete n=256 parameters from companion code

```text
ITERATIONS_VAR = 2.4
U_PAD_VAR      = 2.3
TRUNCATE       = 40
ITER_CAN_BE_Q  = 50
PADDING        = 40
PADDING2       = 50
STEP           = 2
```

Derived:

```text
iterations = ceil((1.413*256 + 2.4*sqrt(256))/3)*3
           = 402
u/v pad    = ceil(2.3*sqrt(256))
           = 37
tape       = (402/3)*5
           = 670 qubits
```

These are empirical parameters, not correctness theorems.

## 6. History compression and register sharing

Three symbols have `3^3=27` possible blocks. Encode the corresponding six raw bits in five bits.

**[PAPER/CODE]** The authors use an ad hoc partial-domain reversible permutation costing five Toffolis. The companion file `compressor.py` contains the exact 27-state map and gate sequence.

The information lower bound for 402 independent ternary symbols is about:

```text
402*log2(3) ~= 637 bits
```

The 670-bit tape pays about 33 bits for cheap local coding.

`u` and `v` shrink over time. Approximate active width:

```text
width(i) = n - 0.5*log2(8/3)*i + c_pad*sqrt(n)
         ~= n - 0.7075*i + c_pad*sqrt(n)
```

Reuse cleared high wires for tape blocks. In the companion implementation, the physical `u/v` storage is interleaved and a prefix becomes the fixed tape.

Do not start with this sharing. First get exact uncompressed history/replay working at small width.

## 7. Space and cost targets

**[PAPER]** Replay peak:

```text
tape ~= 2.355n + O(sqrt(n))
pair  = 2n
total ~= 4.355n + O(sqrt(n))
```

At n=256:

```text
tape + pair = 670 + 512 = 1182
reported implementation = ~1192-1195 qubits
```

Paper-v1 resources, excluding the lookup window:

```text
space secp256k1: 1192 q, 2^21.19 Toffoli
gate  secp256k1: 1446 q, 2^20.83 Toffoli
space generic:   1192 q, 2^21.78 Toffoli
gate  generic:   1446 q, 2^21.42 Toffoli
```

Later companion README:

```text
space: 1195 q, 2,304,135 Toffoli
gate:  1443 q, 1,799,437 Toffoli
```

Do not use these as predicted benchmark scores; ABI and cost semantics differ.

Paper hot spots:

```text
90% in-place multiplier + inverse
54% replay
36% history construction
39% controlled modular add/inverse
22% hybrid adder
19% controlled swaps
15% constant adders
 9% square
 8% double/halve
```

## 8. Arithmetic choices by phase

### History construction

More ancillas are available because only one other modular value is live.

**[CODE]**

- use Gidney comparator;
- gate-efficient mode uses controlled Gidney adder;
- space mode uses a hybrid adder constrained to exactly the free ancilla budget.

### Replay

This is the peak-space phase.

**[CODE]**

- space mode uses CDKM controlled addition, low-space constant arithmetic, and borrowed-bit MCX;
- gate mode uses controlled Gidney add/comparison and costs about `n` additional qubits.

### Square-add

Outside the multiplier, workspace is plentiful. Use aggressive gate-efficient arithmetic if it does not change global peak.

The same primitive should not automatically be used in every phase.

## 9. Pseudo-Mersenne arithmetic

### 9.1 Doubling

Concept:

```text
shift x through an overflow bit
if overflow:
    add f=2^32+977 into low bits
erase overflow from an output relation
```

The companion code adds `f` into:

```text
bit_length(f)+padding
```

low bits. With padding 40, this is about 73 bits. Failure comes from a carry propagating farther.

### 9.2 Controlled modular add

Concept:

```text
if control:
    y_ext += x_ext
if carry:
    y_low += f
erase carry using y<x
```

Use a truncated high-bit comparison only after an exact version works.

### 9.3 Exact `x+y=p` case

The cheap form does not naturally canonicalize a sum exactly equal to `p`. During initial empty replay iterations, this case can occur.

**[CODE]** Use a special `x+y=p`-aware adder for the first 50 replay steps, then the fast adder.

Do not remove the early special form without instrumenting/proving the state relation.

## 10. Approximation hazards

Sources of failure:

```text
too few Euclid iterations
too little u/v high-bit padding
truncated Euclid comparison
truncated modular-overflow comparison
too-short f carry slice
switching away from x+y=p-safe add too early
wrong empty-tail behavior
```

The paper reports failure probability at most about `2^-13.3` after 10,000 random tests. For 9,024 all-or-nothing benchmark shots, that is not a comfortable margin.

Tune one parameter at a time, in this order:

```text
carry slice
comparison width
u/v padding
iteration count
early exceptional prefix
```

Start conservative.

## 11. Measurement-based uncomputation

Comparator/AND outputs can often be erased by Hadamard, measurement, and a conditional correction. This reduces expected Toffoli cost because the correction occurs about half the time.

Requirements:

- use only operation semantics supported by the benchmark IR;
- count average executed, not merely emitted gates;
- run phase-cleanliness tests;
- verify every measured/released qubit is physically in the required state.

Classical output correctness alone is insufficient.

## 12. Port plan

### Stage A: small exact model

For widths 4-16:

1. classical history;
2. reverse history;
3. replay and inverse replay;
4. full in-place multiply;
5. exhaustive tests.

### Stage B: reversible exact primitives

1. uncompressed two-bit-per-step history;
2. exact replay with full modular add/double;
3. forward+inverse identity;
4. inspect gate and peak scaling.

### Stage C: compression

1. port/synthesize 3-symbol-to-5-bit codec;
2. exhaust all 27 reachable inputs;
3. test inverse and empty blocks;
4. integrate blockwise reverse traversal.

### Stage D: sharing

1. static width schedule with generous pad;
2. prove/test high discarded bits are zero;
3. reuse released wires for tape;
4. confirm the benchmark peak actually drops.

### Stage E: secp arithmetic

1. exact Solinas fold;
2. bounded low-slice add of `f`;
3. early exceptional adder;
4. truncated comparisons;
5. MBU.

### Stage F: point add

Replace one existing multiply/divide path at a time. Reuse the repository's established affine identities and classical-offset arithmetic.

## 13. Short-term hypotheses if full port is too large

Ranked:

1. Find remaining full-`p` corrections in hot phases and replace with exact Solinas folds.
2. Use phase-local spare ancillas to switch selected CDKM operations to Gidney/hybrid without raising global peak.
3. Split exceptional `x+y=p` handling into a short initial prefix and a cheaper tail.
4. Fuse compare/reduce/uncompare.
5. Replace eligible comparison cleanup with phase-safe MBU.
6. Reuse registers known to end as `0`, `1`, or `p`.
7. Fuse history decompression with its controlled consumer.
8. Truncate comparisons only after shadow-testing exact versus truncated decisions on all benchmark shots.

## 14. Frequent invalid approaches

- Porting the window lookup machinery to the benchmark ABI.
- Treating the offset as a compile-time constant.
- Comparing only Toffoli and ignoring qubit product.
- Saving wires outside the true global peak.
- Assuming active-qubit count equals the evaluator's width.
- Releasing mathematically known values without gate-level uncomputation.
- Reversing history in the wrong direction.
- Using modular subtraction in the integer Euclid phase.
- Using ordinary integer subtraction in replay.
- Assuming the 3 symbols are six unconstrained bits.
- Tuning iteration/padding against a reduced test.
- Trusting emitted gate deltas when branches are shot-dependent.
- Declaring an approximate paper circuit valid without a full 9,024-shot run.

## 15. Product break-even

For base `(T,Q)`, a candidate `(T+dT,Q+dQ)` wins iff:

```text
(T+dT)(Q+dQ) < TQ
```

At public launch:

```text
T=3,942,753
Q=2,715
score=10,704,574,395
one qubit ~= 1,452 Toffolis of product value
```

Adding 256 qubits requires saving about 339k Toffolis to break even.

Compute this at the actual starting point before choosing space/gate mode.

## 16. Final checklist

- [ ] Base commit and baseline score recorded.
- [ ] Only editable paths changed.
- [ ] Classical model agrees with quantum conventions.
- [ ] Forward/inverse composition tested.
- [ ] Compressor exhaustive on reachable states.
- [ ] Exact `x+y=p` behavior covered.
- [ ] Approximation parameters listed.
- [ ] Peak phase measured, not guessed.
- [ ] Full untouched benchmark passes.
- [ ] `score.json` recorded.
- [ ] Diff explains which paper idea caused the change.

Primary sources:

- https://arxiv.org/abs/2606.02235
- https://gitlab.inria.fr/capsule/qarton-projects/ec-point-addition
- https://ecdsa.fail/
