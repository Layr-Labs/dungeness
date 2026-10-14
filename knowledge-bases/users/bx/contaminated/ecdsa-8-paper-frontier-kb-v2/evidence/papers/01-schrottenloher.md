# Schrottenloher: compact history, linear replay, and secp256k1 arithmetic

Source: arXiv:2606.02235v1, *Optimized Point Addition Circuits for Elliptic
Curve Discrete Logarithms*.

## Operational role

This is the closest complete source-domain spine for the benchmark. It combines:

- an affine point-addition dataflow;
- an in-place multiplication/division interface;
- a compact fixed-depth binary-Euclid transcript;
- linear replay of that transcript into an arbitrary coefficient register;
- register sharing;
- approximate arithmetic specialized to the secp256k1 pseudo-Mersenne prime.

It is therefore useful both as a baseline and as a map of where a complete
point-addition circuit spends cost. It should not be treated as the endpoint of
the search.

## Point-addition contract

**[EVIDENCE]** The paper represents affine curve points over a prime field and
uses a windowed point-addition unitary. For secp256k1 it states
`q = 2^256 - 4294968273`, with `a = 0`, `b = 7`. The high-level circuit
modifies the two coordinate registers in place. Its point-addition schedule
loads the selected classical point three times, performs a subtraction of its
coordinates, applies the inverse of an in-place multiplication, performs an
out-of-place square inside the existing dataflow, applies a forward in-place
multiplication, and restores lookup workspace. See pages
[6](../../source-pages/schrottenloher-2606.02235v1/page-06.md)–[8](../../source-pages/schrottenloher-2606.02235v1/page-08.md).

**[EVIDENCE]** For the complete ECDLP organization used in the paper, windowing
and endpoint optimizations reduce the secp256k1 computation to 28 windowed point
additions. This number belongs to the paper's Shor-level schedule, not to one
benchmark invocation. See [page 8](../../source-pages/schrottenloher-2606.02235v1/page-08.md).

## Information representation

**[EVIDENCE]** The Euclidean algorithm does not maintain Bézout coefficients
during its reduction. At each fixed iteration it computes:

```text
b0 = parity(v)
b1 = (u > v)
store b0 and (b0 & b1)
conditionally swap u,v
conditionally subtract u from v
halve v
```

The source estimates an average iteration count near `1.413 n`, with standard
deviation near `0.6 sqrt(n)`, and chooses a fixed budget
`1.413 n + c_iter sqrt(n)` with `c_iter ≈ 2.4`. See
[page 9](../../source-pages/schrottenloher-2606.02235v1/page-09.md) and
[page 10](../../source-pages/schrottenloher-2606.02235v1/page-10.md).

**[EVIDENCE]** The raw branch information has an information estimate near
`2.12 n + O(sqrt(n))` bits. The implemented fixed tape groups three branch
pairs, which have only 27 valid patterns, into five bits using a five-Toffoli
compressor. This produces a fixed transcript of approximately
`2.355 n + O(sqrt(n))` bits. The shrinking `u,v` registers share storage with
the growing transcript. See [page 10](../../source-pages/schrottenloher-2606.02235v1/page-10.md).

## Linear replay

**[EVIDENCE]** Reading the transcript in reverse controls only linear updates:

```text
s <- 2s mod q
if b0:       s <- s + r mod q
if b0 & b1: swap r,s
```

Starting replay from an arbitrary value rather than from `1` applies the same
Euclidean transformation to that value. The paper's ordering convention yields
multiplication by `x` in the stated reconstruction direction. This is what
allows the transcript to implement an in-place multiplication instead of
materializing an inverse. See
[page 11](../../source-pages/schrottenloher-2606.02235v1/page-11.md).

The complete in-place interface is:

```text
|x>|y>
  convert x to transcript g
  replay g on y
  convert g back to x
-> |x>|xy mod q>
```

The inverse circuit gives multiplication by `x^-1`. See
[page 12](../../source-pages/schrottenloher-2606.02235v1/page-12.md).

## Space and phase behavior

**[EVIDENCE]** During replay, two `n`-bit data registers coexist with the
approximately `2.355n` transcript, giving the paper's space-leading estimate
`4.355n + O(sqrt(n))`. During forward and reverse Euclid there is about one
register of otherwise unused space, permitting cheaper arithmetic in those
phases. The replay phase is the tight interval. See
[page 12](../../source-pages/schrottenloher-2606.02235v1/page-12.md).

**[EVIDENCE]** The circuits allow measurement-based uncomputation inside a
restricted “kickmix” style simulation model. Any benchmark transfer must retain
the classical outcomes and phase corrections supplied by the actual primitive;
the compact transcript itself is not deleted by measurement. See
[page 6](../../source-pages/schrottenloher-2606.02235v1/page-06.md).

## Arithmetic specialization

**[EVIDENCE]** The paper mixes low-ancilla CDKM-style arithmetic with
ancilla-rich Gidney-style arithmetic according to lifetime availability. It
also truncates selected comparisons to roughly 40–50 high bits and exploits
`q = 2^u - f` to replace corrections by `q` with short corrections by `f`.
See pages [13](../../source-pages/schrottenloher-2606.02235v1/page-13.md)–[16](../../source-pages/schrottenloher-2606.02235v1/page-16.md).

**[EVIDENCE]** A non-random boundary matters during early replay:
`x + y = q` can occur in initially empty iterations. The source supplies a
separate pseudo-Mersenne controlled-adder variant for that case. A transferred
approximation must not assume all replay inputs are independent uniform field
elements. See pages [14](../../source-pages/schrottenloher-2606.02235v1/page-14.md)–[17](../../source-pages/schrottenloher-2606.02235v1/page-17.md).

## Cost ownership reported by the paper

**[EVIDENCE]** In the paper's space-optimized secp256k1 design, approximately
90% of the CCX/AND cost is in the in-place multiplier and its inverse. Within
the total, reported shares include 54% reconstruction, 36% GCD construction,
39% controlled modular addition and inverse, 22% hybrid addition, 19%
controlled swaps, 15% constant addition, and 8% modular doubling. These
categories overlap as parent and child components. See
[page 17](../../source-pages/schrottenloher-2606.02235v1/page-17.md).

## Transfer barriers and experiments

- **[EVIDENCE]** Several reductions are probabilistic approximations calibrated
  for the source distribution. Exact benchmark correctness may reject them.
- **[EVIDENCE]** The fixed transcript size is an engineered code, not the
  information-theoretic minimum.
- **[INFERENCE]** Test alternative transcript alphabets, arithmetic/range
  coding, or a mixed explicit/implicit representation while preserving replay.
- **[INFERENCE]** The replay interval is a natural target for lifetime
  scheduling because it owns space while forward/reverse Euclid leave slack.
- **[INFERENCE]** Treat the branch tape and the Khattar Dialog as two instances
  of “small invertible transition sequence”; test whether a prime-field
  transition alphabet can reduce tape width without importing polynomial
  arithmetic.
- **[INFERENCE]** Re-profile exact benchmark code before optimizing the paper's
  listed percentages; implementation details can move ownership.
