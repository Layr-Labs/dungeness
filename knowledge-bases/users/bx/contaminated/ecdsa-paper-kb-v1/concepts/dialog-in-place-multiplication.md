# Dialog/history-based in-place multiplication

## Why this is the central idea

Conventional reversible inversion keeps Euclid state and Bézout coefficients live together or computes, uses, and uncomputes a bulky inverse. The paper separates branch discovery from coefficient evolution.

The two phases are:

1. **History construction:** reduce `(p,x)` to `(1,0)` and save enough branch information to reverse the process.
2. **Linear replay:** consume that history against a pair of modular registers.

Because replay is linear, initializing it with arbitrary `y` performs the desired multiply/divide at essentially the cost of coefficient reconstruction.

## History construction

Per fixed iteration:

```text
b0 = v & 1
b1 = (u > v)
record b0 and (b0 & b1)
if b0 & b1:
    swap(u,v)
if b0:
    v -= u
v >>= 1
```

The input `u=p` is odd. With sufficient iterations, the final state is `(1,0)`.

Reversibility comes from retaining the branch symbols, not from retaining all intermediate integers.

## Replay

Read symbols in reverse:

```text
s = 2*s mod p
if b0:
    s = s+r mod p
if b0 & b1:
    swap(r,s)
```

Depending on chosen direction and variable convention, this applies multiplication by `x` or `x^-1`. The released code's `ApplyBitVector` direction, initialized with `(y,0)`, produces `(0,x*y)`.

## Full in-place multiplier

```text
input x,y
d = history(x)           # x's qubits become/rehouse the tape
(y,tmp) = replay(d,y,0)  # result moves to tmp; y becomes zero
swap(y,tmp)
release tmp
x = inverse_history(d)
output x,x*y
```

Inverse the entire circuit to obtain division by `x`.

## Space reasoning

At history construction, `u` and `v` shrink while the tape grows. Their storage can overlap.

At replay, the tape plus two full modular registers are live:

```text
tape ~= 2.355n + O(sqrt(n))
r,s  = 2n
peak ~= 4.355n + O(sqrt(n))
```

For `n=256`, the companion code uses a 670-bit tape. `670 + 512 = 1182`, leaving only a small margin to the reported 1195-qubit implementation for controls and arithmetic workspace.

## Porting invariants

Before emitting a quantum circuit, build a small exact classical model and verify:

1. `history(p,x)` ends at `(1,0)`.
2. reversing history reconstructs `(p,x)`.
3. replay on `(y,0)` gives the expected `x*y` or `y/x`.
4. inverse replay restores `(y,0)`.
5. compressor/decompressor round-trips every reachable symbol block.
6. the whole `IPModMul` forward and inverse are identities when composed.

## Where a port usually fails

- wrong comparison direction (`u>v` versus `v>u`);
- recording bits before versus after a swap;
- iterating the tape in the wrong direction;
- using arithmetic shift semantics where unsigned logical shift is required;
- forgetting that subtraction is exact non-modular in history construction but modular in replay;
- erasing a comparison flag from a condition that fails on equality;
- mishandling empty tail iterations after Euclid has completed;
- assuming tape symbols are independent when designing compression;
- allowing register slices to shrink below a rare actual value;
- freeing a register that is mathematically known but not physically uncomputed.

## Implementation strategy

Do not begin with the full 256-bit point-add rewrite.

1. Implement a classical reference for widths 4-16.
2. Implement exact reversible history without compression.
3. Implement exact replay.
4. Compose a small-width in-place multiplier and run exhaustive tests.
5. Add compression.
6. Add register sharing.
7. Add pseudo-Mersenne replay arithmetic.
8. Add approximations one at a time.
9. Integrate at one point-add call site.
10. Run the full benchmark before optimizing further.
