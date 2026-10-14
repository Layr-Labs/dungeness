# Approximate and secp256k1-specific arithmetic

## Principle

**[PAPER]** Shor's point-add path need only succeed with a sufficiently large constant probability, so the circuit can replace some exact comparisons and carry ranges with high-probability approximations.

**[BENCHMARK]** ecdsa.fail requires zero failures over its fixed validation set. Approximation is permitted only insofar as that exact set passes and the circuit remains reversible and phase-clean.

## Truncated comparisons

Instead of comparing all `n` bits, compare only the most significant `k` bits.

Use cases:

- deciding `u > v` in history construction;
- detecting whether a modular-add output crosses `p`;
- erasing an overflow/reduction flag by checking `result < addend`.

The paper typically uses 40-50 significant bits. The companion code uses:

```text
TRUNCATE = 40
PADDING  = 40
PADDING2 = 50
```

The Euclid comparator actually sees `TRUNCATE + u_padding` bits, so at `n=256` it compares up to about 77 bits early in the run.

## Pseudo-Mersenne identity

For secp256k1:

```text
p = 2^256 - f
f = 2^32 + 977
```

Therefore:

```text
2^256 == f mod p
```

An overflow bit from a 256-bit addition can be folded back by adding `f` to the low end, instead of subtracting the full 256-bit modulus.

## Specialized modular doubling

Conceptual circuit:

```text
input x in [0,p)
shift x left through one overflow ancilla
if overflow:
    add f into a bounded low-bit slice
erase overflow from a deterministic output bit/relation
```

The companion Qarton code represents the shift using its register-order convention and then adds `f` to:

```text
low_width = bit_length(f) + padding
```

With padding 40, that is about 73 low bits.

The failure mode is an unexpectedly long carry propagation beyond the truncated slice.

## Specialized controlled modular addition

Fast form:

```text
if control:
    y_ext += x_ext
if carry_out:
    y_low += f
erase carry_out using a truncated comparison y < x
```

This omits full-width subtract/add-by-`p`.

## The `x+y=p` exceptional case

The fast overflow logic treats ordinary random sums well but does not naturally map `p` to canonical zero. During early Bézout replay, empty/history-padding iterations can create exactly this relation.

The companion code therefore uses:

- a special `x+y=p`-aware adder for the first 50 replay iterations;
- the cheaper fast adder afterwards.

The special adder approximately detects the all-ones high-bit pattern, XORs the modulus when needed, folds overflow by `f`, and uncomputes the detection from the zero high-bit pattern.

Do not remove this distinction without proving the early replay state cannot hit the exceptional relation.

## Modular square-add

The paper constructs controlled squaring by a double-and-add schedule:

```text
for bits of y:
    conditionally add y to accumulator
    double accumulator
```

Outside the in-place multiplier, more ancillas are available, so the companion implementation uses gate-efficient Gidney arithmetic here.

In the benchmark, inspect whether a specialized squarer already exists before porting this schedule.

## Measurement-based uncomputation

A comparator output can be erased by:

1. Hadamard/measurement on the output;
2. conditionally applying the phase correction/comparator;
3. releasing the zeroed wire.

The expected expensive correction executes with probability about one half. The benchmark must support the exact operation semantics, and the score may count average executed gates rather than emitted gates.

Check phase cleanliness explicitly. A classically correct MBU port can still fail the phase tests.

## Failure-budget reasoning

If an operation fails independently with probability `epsilon` and appears `m` times, a rough union bound is:

```text
P(any failure) <= m*epsilon
```

For a 9,024-shot all-pass benchmark, a per-shot failure near `2^-13.3` is not comfortably safe; the expected number of failures is on the order of one. Increase margins or retain exact variants until a full run passes.

## Safe introduction order

1. exact pseudo-Mersenne reduction;
2. full-width flag uncomputation;
3. low-slice `f` addition with conservative width;
4. truncated flag comparisons;
5. truncated Euclid comparison;
6. reduced iteration/padding constants.

Benchmark each layer separately so a failure can be localized.
